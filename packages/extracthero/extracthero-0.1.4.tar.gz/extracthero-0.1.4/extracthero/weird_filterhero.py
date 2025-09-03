# extracthero/filterhero.py
# run with:  python -m extracthero.filterhero
"""
FilterHero — the "filter" phase of ExtractHero.
- Normalises raw input (HTML / JSON / dict / plain-text).
- Optionally reduces HTML to visible text.
- Uses a JSON fast-path when possible; otherwise builds LLM prompts.
- Supports multi-stage filtering pipelines with configurable models.
"""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

from llmservice import GenerationResult
from extracthero.myllmservice import MyLLMService
from extracthero.schemas import (
    ExtractConfig,
    FilterOp,
    CorpusPayload,   
    WhatToRetain, 
    ProcessResult
)

from domreducer import HtmlReducer
from string2dict import String2Dict
from extracthero.utils import load_html
import asyncio


import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=".*extracthero.filterhero.*"
)

import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o-mini")


# Default pipeline configurations
DEFAULT_PIPELINE_CONFIGS = {
    "standard": {
        "mode": "standard",
        "stages": [
            {"strategy": "liberal", "model": None}  # Uses default model
        ]
    },
    "two_stage": {
        "mode": "two_stage", 
        "stages": [
            {"strategy": "liberal", "model": "gpt-4o-mini"},
            {"strategy": "contextual", "model": "gpt-4o-mini"}
        ]
    },
    "three_stage": {
        "mode": "three_stage",
        "stages": [
            {"strategy": "negative", "model": "gpt-4o-mini"},  # Cheaper model for simple negative filter
            {"strategy": "contextual", "model": "gpt-4o-mini"}  # Better model for contextual understanding
        ]
    }
}


# ─────────────────────────────────────────────────────────────────────────────
class FilterHero:
    def __init__(
        self,
        config: Optional[ExtractConfig] = None,
        llm: Optional[MyLLMService] = None,
    ):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()
        self.html_reducer_op = None
    
    # ──────────────────────── public orchestrator ────────────────────────
    def run(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
        text_type: Optional[str] = None,
        filter_separately: bool = False,
        reduce_html: bool = True,
        enforce_llm_based_filter: bool = False,
        filter_strategy: str = "liberal",  # Used only if pipeline_config is not provided
        pipeline_config: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> FilterOp:
        """
        End-to-end filter phase with support for multi-stage pipelines.
        
        Parameters:
        -----------
        pipeline_config : str or dict, optional
            Can be:
            - A string: "standard", "two_stage", or "three_stage" (uses defaults)
            - A dict with structure:
              {
                  "mode": "three_stage",
                  "stages": [
                      {"strategy": "negative", "model": "gpt-4o-mini"},
                      {"strategy": "contextual", "model": "gpt-4o"}
                  ]
              }
            - If None, uses "standard" mode with filter_strategy parameter
        """
        ts = time()
        
        # Parse pipeline configuration
        pipeline_cfg = self._parse_pipeline_config(pipeline_config, filter_strategy)
       
        # 1) Pre-process (HTML reduction / JSON parsing / pass-through)
        payload = self._prepare_corpus(text, text_type, reduce_html)

        if payload.error:
            return FilterOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                reduced_html=payload.reduced_html,
                start_time=ts,
                success=False,
                error=payload.error,
                filter_strategy=self._get_strategy_string(pipeline_cfg)
            )

        # 2) Handle JSON fast-path or stringify payload for LLM
        proc = self.process_corpus_payload(
            payload, extraction_spec, enforce_llm_based_filter, ts
        )
        if proc.fast_op is not None:
            return proc.fast_op

        # 3) Execute appropriate pipeline based on mode
        mode = pipeline_cfg["mode"]
        
        if mode == "three_stage":
            return self._run_three_stage_pipeline(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )
        elif mode == "two_stage":
            return self._run_two_stage_pipeline(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )
        else:  # standard mode
            return self._run_standard_pipeline(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )

    # ─────────────────────── Configuration parsing ───────────────────────
    def _parse_pipeline_config(
        self, 
        pipeline_config: Optional[Union[str, Dict[str, Any]]], 
        filter_strategy: str
    ) -> Dict[str, Any]:
        """Parse pipeline configuration into standard format"""
        
        # If no config provided, use standard mode with provided filter_strategy
        if pipeline_config is None:
            return {
                "mode": "standard",
                "stages": [
                    {"strategy": filter_strategy, "model": None}
                ]
            }
        
        # If string provided, use default configuration
        if isinstance(pipeline_config, str):
            if pipeline_config in DEFAULT_PIPELINE_CONFIGS:
                return DEFAULT_PIPELINE_CONFIGS[pipeline_config].copy()
            else:
                raise ValueError(f"Unknown pipeline mode: {pipeline_config}")
        
        # If dict provided, validate and return
        if isinstance(pipeline_config, dict):
            if "mode" not in pipeline_config or "stages" not in pipeline_config:
                raise ValueError("pipeline_config dict must have 'mode' and 'stages' keys")
            return pipeline_config
            
        raise ValueError("pipeline_config must be None, str, or dict")

    def _get_strategy_string(self, pipeline_cfg: Dict[str, Any]) -> str:
        """Generate a string representation of the pipeline strategies"""
        strategies = [stage["strategy"] for stage in pipeline_cfg["stages"]]
        return "→".join(strategies)

    # ─────────────────────── Pipeline implementations ───────────────────────
    def _run_standard_pipeline(
        self,
        corpus: str,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_separately: bool,
        pipeline_cfg: Dict[str, Any],
        reduced_html: Optional[str],
        start_time: float,
    ) -> FilterOp:
        """Original single-stage pipeline"""
        stage_cfg = pipeline_cfg["stages"][0]
        
        gen_results = self._dispatch_with_model(
            corpus, 
            extraction_spec, 
            filter_separately,
            stage_cfg["strategy"],
            stage_cfg.get("model")
        )

        ok = (
            gen_results[0].success
            if isinstance(extraction_spec, WhatToRetain) or not filter_separately
            else all(r.success for r in gen_results)
        )

        content, usage = self._aggregate(gen_results, extraction_spec, filter_separately)

        filtered_data_token_size = None
        if ok and content is not None and isinstance(content, str):
            try:
                filtered_data_token_size = len(encoding.encode(content))
            except:
                filtered_data_token_size = None

        primary_generation_result = gen_results[0] if gen_results else None

        return FilterOp.from_result(
            config=self.config,
            content=content,
            usage=usage,
            reduced_html=reduced_html,
            html_reduce_op=self.html_reducer_op,
            generation_result=primary_generation_result,
            start_time=start_time,
            success=ok,
            error=None if ok else "LLM filter failed",
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=self._get_strategy_string(pipeline_cfg)
        )
     
    def _run_two_stage_pipeline(
        self,
        corpus: str,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_separately: bool,
        pipeline_cfg: Dict[str, Any],
        reduced_html: Optional[str],
        start_time: float,
    ) -> FilterOp:
        """Two-stage filtering: broad → precise"""
        total_usage = {}
        stages = pipeline_cfg["stages"]
        
        # Stage 1: Broad filter
        stage1_cfg = stages[0]
        stage1_results = self._dispatch_with_model(
            corpus, 
            extraction_spec, 
            filter_separately,
            stage1_cfg["strategy"],
            stage1_cfg.get("model")
        )
        
        if not all(r.success for r in stage1_results):
            return self._create_failed_filter_op(
                "Stage 1 filter failed", 
                reduced_html, 
                start_time, 
                self._get_strategy_string(pipeline_cfg)
            )
             
        stage1_content, stage1_usage = self._aggregate(
            stage1_results, extraction_spec, filter_separately
        )
        self._accumulate_usage(total_usage, stage1_usage)
        
        # Stage 2: Precise filter
        stage2_cfg = stages[1]
        stage2_corpus = (
            stage1_content if isinstance(stage1_content, str) 
            else _json.dumps(stage1_content, ensure_ascii=False, indent=2)
        )
        
        stage2_results = self._dispatch_with_model(
            stage2_corpus, 
            extraction_spec, 
            filter_separately,
            stage2_cfg["strategy"],
            stage2_cfg.get("model")
        )
        
        if not all(r.success for r in stage2_results):
            return self._create_failed_filter_op(
                "Stage 2 filter failed", 
                reduced_html, 
                start_time, 
                self._get_strategy_string(pipeline_cfg)
            )
            
        final_content, stage2_usage = self._aggregate(
            stage2_results, extraction_spec, filter_separately
        )
        self._accumulate_usage(total_usage, stage2_usage)
        
        filtered_data_token_size = None
        if final_content is not None and isinstance(final_content, str):
            try:
                filtered_data_token_size = len(encoding.encode(final_content))
            except:
                filtered_data_token_size = None
                
        return FilterOp.from_result(
            config=self.config,
            content=final_content,
            usage=total_usage,
            reduced_html=reduced_html,
            html_reduce_op=self.html_reducer_op,
            generation_result=stage2_results[0] if stage2_results else None,
            start_time=start_time,
            success=True,
            error=None,
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=self._get_strategy_string(pipeline_cfg)
        )
    
    def _run_three_stage_pipeline(
        self,
        corpus: str,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_separately: bool,
        pipeline_cfg: Dict[str, Any],
        reduced_html: Optional[str],
        start_time: float,
    ) -> FilterOp:
        """Three-stage filtering: negative → contextual → (parse handled separately)"""
        total_usage = {}
        stages = pipeline_cfg["stages"]
        
        # Stage 1: Negative filter (remove obviously irrelevant content)
        stage1_cfg = stages[0]
        stage1_results = self._dispatch_negative_filter(
            corpus, 
            extraction_spec,
            stage1_cfg.get("model")
        )
        
        if not stage1_results[0].success:
            return self._create_failed_filter_op(
                "Stage 1 negative filter failed", 
                reduced_html, 
                start_time, 
                "negative"
            )
            
        stage1_content = stage1_results[0].content
        self._accumulate_usage(total_usage, stage1_results[0].usage)
        
        # Stage 2: Contextual filter
        stage2_cfg = stages[1]
        stage2_results = self._dispatch_with_model(
            stage1_content, 
            extraction_spec, 
            filter_separately,
            stage2_cfg["strategy"],
            stage2_cfg.get("model")
        )
        
        if not all(r.success for r in stage2_results):
            return self._create_failed_filter_op(
                "Stage 2 contextual filter failed", 
                reduced_html, 
                start_time, 
                self._get_strategy_string(pipeline_cfg)
            )
            
        final_content, stage2_usage = self._aggregate(
            stage2_results, extraction_spec, filter_separately
        )
        self._accumulate_usage(total_usage, stage2_usage)
        
        filtered_data_token_size = None
        if final_content is not None and isinstance(final_content, str):
            try:
                filtered_data_token_size = len(encoding.encode(final_content))
            except:
                filtered_data_token_size = None
                
        return FilterOp.from_result(
            config=self.config,
            content=final_content,
            usage=total_usage,
            reduced_html=reduced_html,
            html_reduce_op=self.html_reducer_op,
            generation_result=stage2_results[0] if stage2_results else None,
            start_time=start_time,
            success=True,
            error=None,
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=self._get_strategy_string(pipeline_cfg)
        )

    # ─────────────────────── Enhanced dispatch methods ───────────────────────
    def _dispatch_with_model(
        self,
        corpus_str: str,
        items: WhatToRetain | List[WhatToRetain],
        separate: bool,
        filter_strategy: str,
        model_name: Optional[str] = None,
    ) -> List[GenerationResult]:
        """
        Dispatch LLM calls with optional model override.
        """
        it_list = [items] if isinstance(items, WhatToRetain) else items
        
        if len(it_list) == 1 or not separate:
            # Combined prompt approach
            prompt = "\n\n".join(it.compile() for it in it_list)
            generation_result = self.llm.filter_via_llm(
                corpus_str, 
                prompt, 
                filter_strategy=filter_strategy,
                model_name=model_name  # Pass model override
            )
            return [generation_result]

        # Separate calls approach
        generation_results = []
        for it in it_list:
            generation_result = self.llm.filter_via_llm(
                corpus_str, 
                it.compile(),
                filter_strategy=filter_strategy,
                model_name=model_name  # Pass model override
            )
            generation_results.append(generation_result)
        
        return generation_results

    def _dispatch_negative_filter(
        self,
        corpus: str,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        model_name: Optional[str] = None,
    ) -> List[GenerationResult]:
        """Special dispatch for negative filtering stage with model override"""
        # Create a combined description of what we're looking for
        if isinstance(extraction_spec, WhatToRetain):
            target_desc = extraction_spec.desc
        else:
            target_desc = "; ".join(spec.desc for spec in extraction_spec)
            
        negative_prompt = f"""Remove ONLY content that is CLEARLY AND OBVIOUSLY unrelated to: {target_desc}

**SOURCE CONTENT:**
{corpus}

**DEFINITELY REMOVE:**
- Navigation menus, headers, footers, breadcrumbs
- Cookie notices, privacy policies, legal disclaimers
- Unrelated product recommendations ("customers also bought", "similar products")
- Advertising banners, promotional content for other products
- Social media widgets, sharing buttons
- Comments sections, reviews for other products
- Company info, about us, career sections
- Newsletter signup forms
- Chat widgets, help buttons

**KEEP:**
- Any content that might relate to {target_desc}
- Technical specifications tables (even if they contain some unrelated specs)
- Product descriptions and features
- Any numbers with units that could be relevant
- Contextual information that helps understand the data

**IMPORTANT:** When in doubt, KEEP the content. It's better to include too much than to accidentally remove relevant information.

**OUTPUT:**
Return all content except the clearly irrelevant sections listed above."""

        generation_result = self.llm.filter_via_llm(
            corpus, 
            negative_prompt, 
            filter_strategy="negative",
            model_name=model_name  # Pass model override
        )
        return [generation_result]

    # ─────────────────────── Helper methods ───────────────────────
    def _create_failed_filter_op(
        self, 
        error_msg: str, 
        reduced_html: Optional[str], 
        start_time: float, 
        filter_strategy: str
    ) -> FilterOp:
        """Create a failed FilterOp with consistent structure"""
        return FilterOp.from_result(
            config=self.config,
            content=None,
            usage=None,
            reduced_html=reduced_html,
            html_reduce_op=self.html_reducer_op,
            generation_result=None,
            start_time=start_time,
            success=False,
            error=error_msg,
            filtered_data_token_size=None,
            filter_strategy=filter_strategy
        )

    def _accumulate_usage(
        self, 
        total_usage: Dict[str, int], 
        new_usage: Optional[Dict[str, int]]
    ) -> None:
        """Accumulate usage statistics across stages"""
        if new_usage:
            for k, v in new_usage.items():
                total_usage[k] = total_usage.get(k, 0) + v

    # ─────────────────────── async version ───────────────────────
    async def run_async(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
        text_type: Optional[str] = None,
        filter_separately: bool = False,
        reduce_html: bool = True,
        enforce_llm_based_filter: bool = False,
        filter_strategy: str = "liberal",
        pipeline_config: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> FilterOp:
        """
        Async version with pipeline config support.
        """
        ts = time()
        
        # Parse pipeline configuration
        pipeline_cfg = self._parse_pipeline_config(pipeline_config, filter_strategy)

        # 1) preprocess
        payload = self._prepare_corpus(text, text_type, reduce_html)
        if payload.error:
            return FilterOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                reduced_html=payload.reduced_html,
                start_time=ts,
                success=False,
                error=payload.error,
                filter_strategy=self._get_strategy_string(pipeline_cfg)
            )

        # 2) dict fast-path unless forced
        proc = self.process_corpus_payload(
            payload, extraction_spec, enforce_llm_based_filter, ts
        )
        if proc.fast_op is not None:
            return proc.fast_op

        # 3) Execute appropriate pipeline asynchronously
        mode = pipeline_cfg["mode"]
        
        if mode == "three_stage":
            return await self._run_three_stage_pipeline_async(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )
        elif mode == "two_stage":
            return await self._run_two_stage_pipeline_async(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )
        else:  # standard mode
            return await self._run_standard_pipeline_async(
                proc.corpus, 
                extraction_spec, 
                filter_separately,
                pipeline_cfg,
                proc.reduced,
                ts
            )

    # # ... (implement async versions of pipeline methods following same pattern)

    # # ─────────────────────── Existing helper methods (unchanged) ───────────────────────
    # def _prepare_corpus(
    #     self,
    #     text: str | Dict[str, Any],
    #     text_type: Optional[str],
    #     reduce_html: bool,
    # ) -> CorpusPayload:
    #     """Return CorpusPayload(corpus, corpus_type, reduced_html, error)"""
    #     # (keep existing implementation from original file)
        
    # def process_corpus_payload(
    #     self,
    #     payload: CorpusPayload,
    #     items: WhatToRetain | List[WhatToRetain],
    #     enforce_llm: bool,
    #     ts: float,
    # ) -> ProcessResult:
    #     """
    #     • If JSON and not forced → return FilterOp shortcut.  
    #     • Else → make sure corpus is a *string* for LLM.
    #     """
    #     # (keep existing implementation from original file)

    # def _aggregate(
    #     self,
    #     gen_results: List[GenerationResult],
    #     items: WhatToRetain | List[WhatToRetain],
    #     separate: bool,
    # ) -> Tuple[Any, Optional[Dict[str, int]]]:
        # (keep existing implementation from original file)
    
    # @staticmethod
    # def _stringify_json(data: Dict[str, Any]) -> str:
    #     return _json.dumps(data, ensure_ascii=False, indent=2)


# ─────────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":
    from extracthero.sample_dicts import sample_page_dict
    cfg = ExtractConfig()
    filter_hero = FilterHero(cfg)
    
    specs = [
        WhatToRetain(
            name="voltage",
            desc="all information about voltage",
            include_context_chunk=False,
        )
    ]
    
    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    
    # Test 1: Using string pipeline config (uses defaults)
    print("=== TEST 1: String Config (uses defaults) ===")
    filter_op = filter_hero.run(
        html_doc, 
        specs, 
        text_type="html",
        pipeline_config="three_stage"  # Will use default models
    )
    print(f"Success: {filter_op.success}")
    print(f"Strategy chain: {filter_op.filter_strategy}")
    
    # Test 2: Using custom pipeline config with specific models
    print("\n=== TEST 2: Custom Config with Models ===")
    custom_config = {
        "mode": "three_stage",
        "stages": [
            {"strategy": "negative", "model": "gpt-3.5-turbo"},  # Cheaper model for negative filter
            {"strategy": "contextual", "model": "gpt-4o"}        # Better model for contextual
        ]
    }
    filter_op = filter_hero.run(
        html_doc, 
        specs, 
        text_type="html",
        pipeline_config=custom_config
    )
    print(f"Success: {filter_op.success}")
    print(f"Strategy chain: {filter_op.filter_strategy}")
    print(f"Total cost: {filter_op.usage.get('total_cost', 'N/A')}")
    
    # Test 3: Backwards compatibility (no pipeline_config)
    print("\n=== TEST 3: Backwards Compatible ===")
    filter_op = filter_hero.run(
        html_doc, 
        specs, 
        text_type="html",
        filter_strategy="contextual"  # Old way still works
    )
    print(f"Success: {filter_op.success}")
    print(f"Strategy: {filter_op.filter_strategy}")