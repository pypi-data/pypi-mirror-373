# extracthero/extracthero.py
# run with: python -m extracthero.extracthero

from __future__ import annotations

from time import time
from typing import List, Union, Optional, Tuple, Dict
import json
import tiktoken

from extracthero.myllmservice import MyLLMService
from extracthero.schemas import (
    ExtractConfig,
    ExtractOp,
    FilterOp,
    FilterChainOp,
    ParseOp,
    WhatToRetain,
)
from extracthero.filterhero import FilterHero
from extracthero.parsehero import ParseHero
from extracthero.utils import load_html
from domreducer import HtmlReducer


class ExtractHero:
    """High-level orchestrator with 3 phases: HTML Reduction → Filter → Parse."""

    def __init__(self, config: ExtractConfig | None = None, llm: MyLLMService | None = None):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()
        self.filter_hero = FilterHero(self.config, self.llm)
        self.parse_hero = ParseHero(self.config, self.llm)
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")

    def _count_tokens(self, text: str | dict | None) -> int:
        """Count tokens in text or dict content."""
        if text is None:
            return 0
        
        if isinstance(text, dict):
            text = json.dumps(text)
        
        try:
            return len(self.encoding.encode(str(text)))
        except Exception:
            return 0

    def _trim_if_needed(self, text: str, trim_char_length: Optional[int]) -> Tuple[str, Optional[int]]:
        """
        Trim text to specified character length if needed.
        
        Returns:
            Tuple of (trimmed_text, trimmed_to_chars or None)
        """
        if trim_char_length and len(text) > trim_char_length:
            return text[:trim_char_length], trim_char_length
        return text, None

    def extract(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_strategy: str = "contextual",
        reduce_html: bool = True,
        model_name: Optional[str] = None,
        trim_char_length: Optional[int] = None,
    ) -> ExtractOp:
        """
        Three-phase extraction pipeline: HTML Reduction → Trimming → Filter → Parse.

        Parameters
        ----------
        text : str | dict
            The source content to extract data from
        extraction_spec : WhatToRetain | List[WhatToRetain]
            Defines what data to extract and how
        filter_strategy : str
            Strategy for filtering ("contextual", "liberal", "inclusive", etc.)
        reduce_html : bool, default True
            Apply HTML reduction before filtering (only for HTML content)
        model_name : Optional[str]
            Specific model to use for LLM operations
        trim_char_length : Optional[int]
            Maximum character length to trim to after HTML reduction. None means no trimming.
            
        Returns
        -------
        ExtractOp
            Rich result object with content, timing, usage, and error details
        """
        extraction_start_time = time()
        
        # Initialize tracking variables
        reduced_html = None
        html_reduce_op = None
        corpus_to_filter = text
        stage_tokens = {}
        trimmed_to = None
        
        # Phase 0: Optional HTML Reduction
        if reduce_html and isinstance(text, str) and "<" in text and ">" in text:
            try:
                html_reduce_op = HtmlReducer(str(text)).reduce()
                if html_reduce_op.success:
                    reduced_html = html_reduce_op.reduced_data
                    corpus_to_filter = html_reduce_op.reduced_data
                    # Use existing token counts from html_reduce_op
                    stage_tokens["HTML Reduction"] = {
                        "input": html_reduce_op.total_token,
                        "output": html_reduce_op.reduced_total_token
                    }
                else:
                    corpus_to_filter = text
            except Exception as e:
                corpus_to_filter = text
        
        # Phase 0.5: Trimming if needed (after HTML reduction)
        if trim_char_length and isinstance(corpus_to_filter, str):
            corpus_to_filter, trimmed_to = self._trim_if_needed(corpus_to_filter, trim_char_length)
            if trimmed_to:
                # Add trimming info to stage tokens
                trimmed_tokens = self._count_tokens(corpus_to_filter)
                pre_trim_tokens = stage_tokens.get("HTML Reduction", {}).get("output", self._count_tokens(text))
                stage_tokens["Trimming"] = {
                    "input": pre_trim_tokens,
                    "output": trimmed_tokens,
                    "trimmed_to_chars": trimmed_to
                }
        
        # Phase 1: Filtering
        filter_input_tokens = self._count_tokens(corpus_to_filter)
        filter_op: FilterOp = self.filter_hero.run(
            corpus_to_filter,
            extraction_spec,
            filter_strategy=filter_strategy
        )
        
        # Use filtered_data_token_size if available, otherwise calculate
        filter_output_tokens = filter_op.filtered_data_token_size if filter_op.filtered_data_token_size else self._count_tokens(filter_op.content if filter_op.success else None)
        
        stage_tokens["Filter"] = {
            "input": filter_input_tokens,
            "output": filter_output_tokens
        }

        # Check if filter phase failed
        if not filter_op.success:
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter phase failed - parse not attempted",
                generation_result=None
            )
            
            return ExtractOp.from_operations(
                filter_op=filter_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None,
                reduced_html=reduced_html,
                html_reduce_op=html_reduce_op,
                stage_tokens=stage_tokens,
                trimmed_to=trimmed_to
            )

        # Phase 2: Parsing
        parse_input_tokens = filter_output_tokens  # Use the filter output tokens
        parse_op = self.parse_hero.run(
            filter_op.content, 
            extraction_spec,
            model_name=model_name
        )
        parse_output_tokens = self._count_tokens(parse_op.content if parse_op.success else None)
        stage_tokens["Parse"] = {
            "input": parse_input_tokens,
            "output": parse_output_tokens
        }
        
        # Create ExtractOp with all metrics
        result = ExtractOp.from_operations(
            filter_op=filter_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None,
            reduced_html=reduced_html,
            html_reduce_op=html_reduce_op,
            stage_tokens=stage_tokens,
            trimmed_to=trimmed_to
        )
        
        return result

    def extract_with_chain(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_stages: List[Tuple[List[WhatToRetain], str]],
        reduce_html: bool = True,
        model_name: Optional[str] = None,
        trim_char_length: Optional[int] = None,
    ) -> ExtractOp:
        """
        Three-phase extraction with filter chaining.

        Parameters
        ----------
        text : str | dict
            The source content to extract data from
        extraction_spec : WhatToRetain | List[WhatToRetain]
            Final specifications for parsing
        filter_stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples for chaining
        reduce_html : bool, default True
            Apply HTML reduction before filtering
        model_name : Optional[str]
            Specific model to use
        trim_char_length : Optional[int]
            Maximum character length to trim to after HTML reduction. None means no trimming.
            
        Returns
        -------
        ExtractOp
            Rich result object with filter chain details
        """
        extraction_start_time = time()
        
        # Initialize tracking variables
        reduced_html = None
        html_reduce_op = None
        corpus_to_filter = text
        stage_tokens = {}
        trimmed_to = None
        
        # Phase 0: Optional HTML Reduction
        if reduce_html and isinstance(text, str) and "<" in text and ">" in text:
            try:
                html_reduce_op = HtmlReducer(str(text)).reduce()
                if html_reduce_op.success:
                    reduced_html = html_reduce_op.reduced_data
                    corpus_to_filter = html_reduce_op.reduced_data
                    # Use existing token counts from html_reduce_op
                    stage_tokens["HTML Reduction"] = {
                        "input": html_reduce_op.total_token,
                        "output": html_reduce_op.reduced_total_token
                    }
                else:
                    corpus_to_filter = text
            except Exception as e:
                corpus_to_filter = text
        
        # Phase 0.5: Trimming if needed (after HTML reduction)
        if trim_char_length and isinstance(corpus_to_filter, str):
            corpus_to_filter, trimmed_to = self._trim_if_needed(corpus_to_filter, trim_char_length)
            if trimmed_to:
                # Add trimming info to stage tokens
                trimmed_tokens = self._count_tokens(corpus_to_filter)
                pre_trim_tokens = stage_tokens.get("HTML Reduction", {}).get("output", self._count_tokens(text))
                stage_tokens["Trimming"] = {
                    "input": pre_trim_tokens,
                    "output": trimmed_tokens,
                    "trimmed_to_chars": trimmed_to
                }
        
        # Phase 1: Filter Chain
        filter_input_tokens = self._count_tokens(corpus_to_filter)
        filter_chain_op: FilterChainOp = self.filter_hero.chain(
            corpus_to_filter,
            filter_stages
        )
        
        # Use filtered_data_token_size if available
        filter_output_tokens = filter_chain_op.filtered_data_token_size if filter_chain_op.filtered_data_token_size else self._count_tokens(filter_chain_op.content if filter_chain_op.success else None)
        
        # Track tokens for each filter stage
        stage_tokens["Filter Chain (Total)"] = {
            "input": filter_input_tokens,
            "output": filter_output_tokens
        }
        
        # Add individual filter stage tokens if available (these are already calculated in reduction_details)
        if filter_chain_op.reduction_details:
            for i, reduction in enumerate(filter_chain_op.reduction_details):
                stage_tokens[f"Filter Stage {i+1}"] = {
                    "input": reduction.get("source_token_size", 0),
                    "output": reduction.get("filtered_token_size", 0)
                }

        # Check if filter chain failed
        if not filter_chain_op.success:
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter chain failed - parse not attempted",
                generation_result=None
            )
            
            return ExtractOp.from_operations(
                filter_chain_op=filter_chain_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None,
                reduced_html=reduced_html,
                html_reduce_op=html_reduce_op,
                stage_tokens=stage_tokens,
                trimmed_to=trimmed_to
            )

        # Phase 2: Parsing
        parse_input_tokens = filter_output_tokens  # Use the filter chain output tokens
        parse_op = self.parse_hero.run(
            filter_chain_op.content, 
            extraction_spec,
            model_name=model_name
        )
        parse_output_tokens = self._count_tokens(parse_op.content if parse_op.success else None)
        stage_tokens["Parse"] = {
            "input": parse_input_tokens,
            "output": parse_output_tokens
        }
        
        # Create ExtractOp with chain results
        result = ExtractOp.from_operations(
            filter_chain_op=filter_chain_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None,
            reduced_html=reduced_html,
            html_reduce_op=html_reduce_op,
            stage_tokens=stage_tokens,
            trimmed_to=trimmed_to
        )
        
        return result

    async def extract_async(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_strategy: str = "contextual",
        reduce_html: bool = True,
        model_name: Optional[str] = None,
        trim_char_length: Optional[int] = None,
    ) -> ExtractOp:
        """
        Async three-phase extraction pipeline.
        
        Parameters
        ----------
        text : str | dict
            The source content to extract data from
        extraction_spec : WhatToRetain | List[WhatToRetain]
            Defines what data to extract and how
        filter_strategy : str
            Strategy for filtering ("contextual", "liberal", "inclusive", etc.)
        reduce_html : bool, default True
            Apply HTML reduction before filtering (only for HTML content)
        model_name : Optional[str]
            Specific model to use for LLM operations
        trim_char_length : Optional[int]
            Maximum character length to trim to after HTML reduction. None means no trimming.
            
        Returns
        -------
        ExtractOp
            Rich result object with content, timing, usage, and error details
        """
        extraction_start_time = time()
        
        # Initialize tracking variables
        reduced_html = None
        html_reduce_op = None
        corpus_to_filter = text
        stage_tokens = {}
        trimmed_to = None
        
        # Phase 0: Optional HTML Reduction
        if reduce_html and isinstance(text, str) and "<" in text and ">" in text:
            try:
                html_reduce_op = HtmlReducer(str(text)).reduce()
                if html_reduce_op.success:
                    reduced_html = html_reduce_op.reduced_data
                    corpus_to_filter = html_reduce_op.reduced_data
                    # Use existing token counts
                    stage_tokens["HTML Reduction"] = {
                        "input": html_reduce_op.total_token,
                        "output": html_reduce_op.reduced_total_token
                    }
                else:
                    corpus_to_filter = text
            except Exception as e:
                corpus_to_filter = text
        
        # Phase 0.5: Trimming if needed (after HTML reduction)
        if trim_char_length and isinstance(corpus_to_filter, str):
            corpus_to_filter, trimmed_to = self._trim_if_needed(corpus_to_filter, trim_char_length)
            if trimmed_to:
                # Add trimming info to stage tokens
                trimmed_tokens = self._count_tokens(corpus_to_filter)
                pre_trim_tokens = stage_tokens.get("HTML Reduction", {}).get("output", self._count_tokens(text))
                stage_tokens["Trimming"] = {
                    "input": pre_trim_tokens,
                    "output": trimmed_tokens,
                    "trimmed_to_chars": trimmed_to
                }
        
        # Phase 1: Async Filtering
        filter_input_tokens = self._count_tokens(corpus_to_filter)
        filter_op: FilterOp = await self.filter_hero.run_async(
            corpus_to_filter,
            extraction_spec,
            filter_strategy=filter_strategy
        )
        
        filter_output_tokens = filter_op.filtered_data_token_size if filter_op.filtered_data_token_size else self._count_tokens(filter_op.content if filter_op.success else None)
        
        stage_tokens["Filter"] = {
            "input": filter_input_tokens,
            "output": filter_output_tokens
        }

        if not filter_op.success:
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter phase failed - parse not attempted",
                generation_result=None
            )
            
            return ExtractOp.from_operations(
                filter_op=filter_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None,
                reduced_html=reduced_html,
                html_reduce_op=html_reduce_op,
                stage_tokens=stage_tokens,
                trimmed_to=trimmed_to
            )

        # Phase 2: Async Parsing
        parse_input_tokens = filter_output_tokens
        parse_op = await self.parse_hero.run_async(
            filter_op.content, 
            extraction_spec,
            model_name=model_name
        )
        parse_output_tokens = self._count_tokens(parse_op.content if parse_op.success else None)
        stage_tokens["Parse"] = {
            "input": parse_input_tokens,
            "output": parse_output_tokens
        }
        
        result = ExtractOp.from_operations(
            filter_op=filter_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None,
            reduced_html=reduced_html,
            html_reduce_op=html_reduce_op,
            stage_tokens=stage_tokens,
            trimmed_to=trimmed_to
        )
        
        return result

    async def extract_with_chain_async(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_stages: List[Tuple[List[WhatToRetain], str]],
        reduce_html: bool = True,
        model_name: Optional[str] = None,
        trim_char_length: Optional[int] = None,
    ) -> ExtractOp:
        """
        Async three-phase extraction with filter chaining.
        
        Parameters
        ----------
        text : str | dict
            The source content to extract data from
        extraction_spec : WhatToRetain | List[WhatToRetain]
            Final specifications for parsing
        filter_stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples for chaining
        reduce_html : bool, default True
            Apply HTML reduction before filtering
        model_name : Optional[str]
            Specific model to use
        trim_char_length : Optional[int]
            Maximum character length to trim to after HTML reduction. None means no trimming.
            
        Returns
        -------
        ExtractOp
            Rich result object with filter chain details
        """
        extraction_start_time = time()
        
        # Initialize tracking variables
        reduced_html = None
        html_reduce_op = None
        corpus_to_filter = text
        stage_tokens = {}
        trimmed_to = None
        
        # Phase 0: Optional HTML Reduction
        if reduce_html and isinstance(text, str) and "<" in text and ">" in text:
            try:
                html_reduce_op = HtmlReducer(str(text)).reduce()
                if html_reduce_op.success:
                    reduced_html = html_reduce_op.reduced_data
                    corpus_to_filter = html_reduce_op.reduced_data
                    # Use existing token counts
                    stage_tokens["HTML Reduction"] = {
                        "input": html_reduce_op.total_token,
                        "output": html_reduce_op.reduced_total_token
                    }
                else:
                    corpus_to_filter = text
            except Exception as e:
                corpus_to_filter = text
        
        # Phase 0.5: Trimming if needed (after HTML reduction)
        if trim_char_length and isinstance(corpus_to_filter, str):
            corpus_to_filter, trimmed_to = self._trim_if_needed(corpus_to_filter, trim_char_length)
            if trimmed_to:
                # Add trimming info to stage tokens
                trimmed_tokens = self._count_tokens(corpus_to_filter)
                pre_trim_tokens = stage_tokens.get("HTML Reduction", {}).get("output", self._count_tokens(text))
                stage_tokens["Trimming"] = {
                    "input": pre_trim_tokens,
                    "output": trimmed_tokens,
                    "trimmed_to_chars": trimmed_to
                }
        
        # Phase 1: Async Filter Chain
        filter_input_tokens = self._count_tokens(corpus_to_filter)
        filter_chain_op: FilterChainOp = await self.filter_hero.chain_async(
            corpus_to_filter,
            filter_stages
        )
        
        filter_output_tokens = filter_chain_op.filtered_data_token_size if filter_chain_op.filtered_data_token_size else self._count_tokens(filter_chain_op.content if filter_chain_op.success else None)
        
        # Track tokens for each filter stage
        stage_tokens["Filter Chain (Total)"] = {
            "input": filter_input_tokens,
            "output": filter_output_tokens
        }
        
        # Add individual filter stage tokens
        if filter_chain_op.reduction_details:
            for i, reduction in enumerate(filter_chain_op.reduction_details):
                stage_tokens[f"Filter Stage {i+1}"] = {
                    "input": reduction.get("source_token_size", 0),
                    "output": reduction.get("filtered_token_size", 0)
                }

        if not filter_chain_op.success:
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter chain failed - parse not attempted",
                generation_result=None
            )
            
            return ExtractOp.from_operations(
                filter_chain_op=filter_chain_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None,
                reduced_html=reduced_html,
                html_reduce_op=html_reduce_op,
                stage_tokens=stage_tokens,
                trimmed_to=trimmed_to
            )

        # Phase 2: Async Parsing
        parse_input_tokens = filter_output_tokens
        parse_op = await self.parse_hero.run_async(
            filter_chain_op.content, 
            extraction_spec,
            model_name=model_name
        )
        parse_output_tokens = self._count_tokens(parse_op.content if parse_op.success else None)
        stage_tokens["Parse"] = {
            "input": parse_input_tokens,
            "output": parse_output_tokens
        }
        
        result = ExtractOp.from_operations(
            filter_chain_op=filter_chain_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None,
            reduced_html=reduced_html,
            html_reduce_op=html_reduce_op,
            stage_tokens=stage_tokens,
            trimmed_to=trimmed_to
        )
        
        return result


# ─────────────────────────── Demo ───────────────────────────
def main() -> None:
    """Demo showing different extraction methods."""
    extractor = ExtractHero()
    
    specs = [
        WhatToRetain(
            name="reverse_voltage_value",
            desc="reverse voltage value in units of V",
        ),
    ]
    
    # Example: Load real HTML file
    print("\n📋 Real HTML file extraction with token tracking")
    try:
        html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
        
        # Example with trimming
        extract_op = extractor.extract(
            html_doc, 
            specs, 
            reduce_html=True,
            # trim_char_length=50000  # Trim to 50,000 chars
            trim_char_length=None 
        )
        
        if extract_op.success:
            print(f"✅ Success! Extracted: {extract_op.content}")
            if extract_op.trimmed_to:
                print(f"⚠️  Input was trimmed to {extract_op.trimmed_to:,} characters")
            print(f"\n{extract_op.token_summary}")
            print(f"\nTotal time: {extract_op.elapsed_time:.3f}s")
            if extract_op.usage:
                print(f"Total cost: ${extract_op.usage.get('total_cost', 0):.4f}")
        else:
            print(f"❌ Failed: {extract_op.error}")
    except Exception as e:
        print(f"Could not load HTML file: {e}")


if __name__ == "__main__":
    main()