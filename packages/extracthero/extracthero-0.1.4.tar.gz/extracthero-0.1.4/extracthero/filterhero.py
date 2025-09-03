# extracthero/filterhero.py
# run with:  python -m extracthero.filterhero
"""
FilterHero — the "filter" phase of ExtractHero.
• Normalises raw input (HTML / JSON / dict / plain-text).
• Optionally reduces HTML to visible text.
• Uses a JSON fast-path when possible; otherwise builds LLM prompts.
"""

from __future__ import annotations
import tiktoken
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
    ProcessResult,
    FilterChainOp

)

from extracthero.utils import load_html
from extracthero.sample_dicts import sample_page_dict
import asyncio

from extracthero.filter_engine import FilterEngine



import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=".*extracthero.filterhero.*"
)


encoding = tiktoken.encoding_for_model("gpt-4o-mini")




# ─────────────────────────────────────────────────────────────────────────────
class FilterHero:
    def __init__(
        self,
        config: Optional[ExtractConfig] = None,
        llm: Optional[MyLLMService] = None,
    ):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()

        self.engine= FilterEngine(llm_service=self.llm)

    # ──────────────────────── public orchestrator ────────────────────────
    def run(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
    
        filter_strategy: str = "liberal",  
    ) -> FilterOp:
        """
        End-to-end filter phase.
        """
        ts = time()
        content=None
        filtered_data_token_size = None  

        gen_result = self.engine.execute_filtering(
            text, 
            extraction_spec, 
            filter_strategy  
        )

        if gen_result.success:
           content=gen_result.content
           # gen_result.content, gen_result.usage 
           if content is not None:
            try:
                
                filtered_data_token_size = len(encoding.encode(content))
            except Exception as e:
                filtered_data_token_size = None

        
        # 7) Wrap & return
        return FilterOp.from_result(
            config=self.config,
            content=content,
            usage=gen_result.usage,
            generation_result=gen_result,  # ← Pass the generation result here
            start_time=ts,
            success=gen_result.success,
            error=None if gen_result.success else "LLM filter failed",
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=filter_strategy
        )
    

    async def run_async(
        self,
        text: str | Dict[str, Any],
        extraction_spec: WhatToRetain | List[WhatToRetain],
        filter_strategy: str = "contextual",
    ) -> FilterOp:
        """Async end-to-end filter phase."""
        ts = time()
        content = None
        filtered_data_token_size = None  # Initialize it here
        
        
        gen_result = await self.engine.execute_filtering_async(
            text, 
            extraction_spec, 
            filter_strategy  
        )

        if gen_result.success:
            content = gen_result.content
            if content is not None:
                try:
                    filtered_data_token_size = len(encoding.encode(content))
                except Exception as e:
                    filtered_data_token_size = None

        return FilterOp.from_result(
            config=self.config,
            content=content,
            usage=gen_result.usage,
            generation_result=gen_result,
            start_time=ts,
            success=gen_result.success,
            error=None if gen_result.success else "LLM filter failed",
            filtered_data_token_size=filtered_data_token_size,
            filter_strategy=filter_strategy
        )
    

    def _combine_usage(self, usage_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Combine usage dictionaries from multiple stages."""
        if not usage_list:
            return None
        
        combined = {}
        
        # Sum numeric values
        for usage in usage_list:
            for key, value in usage.items():
                if isinstance(value, (int, float)):
                    combined[key] = combined.get(key, 0) + value
                elif key not in combined:
                    # For non-numeric values, keep the first occurrence
                    combined[key] = value
        
        return combined if combined else None
    

    def _calculate_reduction_details(
        self, 
        filter_ops: List[FilterOp], 
        initial_content: str
    ) -> List[Dict[str, int]]:
        """Calculate token reduction details for each stage."""
        reduction_details = []
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        
        try:
            # Calculate initial token size
            current_content = initial_content
            current_token_size = len(encoding.encode(current_content))
            
            for op in filter_ops:
                if op.success and op.content:
                    new_token_size = len(encoding.encode(op.content))
                    reduction_details.append({
                        "source_token_size": current_token_size,
                        "filtered_token_size": new_token_size
                    })
                    current_content = op.content
                    current_token_size = new_token_size
                else:
                    # Failed operation - no reduction
                    reduction_details.append({
                        "source_token_size": current_token_size,
                        "filtered_token_size": current_token_size
                    })
        
        except Exception:
            # If token calculation fails, return empty list
            reduction_details = []
        
        return reduction_details
    

    def chain(
        self,
        text: str | Dict[str, Any],
        stages: List[Tuple[List[WhatToRetain], str]],
    ) -> FilterChainOp:
        """
        Chain multiple filter operations synchronously.
        
        Parameters
        ----------
        text : str | Dict[str, Any]
            Initial input
        stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples
            
        Returns
        -------
        FilterChainOp
            Complete result of the filter chain
        """
        start_time = time()
        filter_ops = []
        current_input = text
        
        # Convert initial input to string if needed
        if isinstance(text, dict):
            initial_content = str(text)  # You might want to JSON serialize this
        else:
            initial_content = text
        
        # Execute each stage
        for extraction_spec, filter_strategy in stages:
            filter_op = self.run(current_input, extraction_spec, filter_strategy)
            filter_ops.append(filter_op)
            
            if not filter_op.success:
                break  # Stop on first failure
                
            current_input = filter_op.content
        
        # Build the result
        if not filter_ops:
            return FilterChainOp(
                success=False,
                content=None,
                elapsed_time=time() - start_time,
                generation_results=[],
                usage=None,
                error="No filter operations completed",
                start_time=start_time,
                filtered_data_token_size=None,
                stages_config=stages,
                reduction_details=[],
                filterops=[]
            )
        
        # Determine overall success (all stages must succeed)
        overall_success = all(op.success for op in filter_ops)
        
        # Get final content (from last successful operation)
        final_content = None
        for op in reversed(filter_ops):
            if op.success and op.content:
                final_content = op.content
                break
        
        # Calculate final token size
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        final_token_size = None
        if final_content:
            try:
                final_token_size = len(encoding.encode(final_content))
            except Exception:
                final_token_size = None
        
        # Combine usage from all stages
        combined_usage = self._combine_usage([op.usage for op in filter_ops if op.usage])
        
        # Extract generation results
        generation_results = [op.generation_result for op in filter_ops if op.generation_result]
        
        # Calculate reduction details
        reduction_details = self._calculate_reduction_details(filter_ops, initial_content)
        
        # Determine error message
        error_message = None
        if not overall_success:
            failed_ops = [op for op in filter_ops if not op.success]
            if failed_ops:
                error_message = f"Stage {filter_ops.index(failed_ops[0]) + 1} failed: {failed_ops[0].error}"
        
        return FilterChainOp(
            success=overall_success,
            content=final_content,
            elapsed_time=time() - start_time,
            generation_results=generation_results,
            usage=combined_usage,
            error=error_message,
            start_time=start_time,
            filtered_data_token_size=final_token_size,
            stages_config=stages,
            reduction_details=reduction_details,
            filterops=filter_ops
        )
    

    

    

    async def chain_async(
        self,
        text: str | Dict[str, Any],
        stages: List[Tuple[List[WhatToRetain], str]],
    ) -> FilterChainOp:
        """
        Chain multiple filter operations asynchronously.
        
        Parameters
        ----------
        text : str | Dict[str, Any]
            Initial input
        stages : List[Tuple[List[WhatToRetain], str]]
            List of (extraction_spec, filter_strategy) tuples
            
        Returns
        -------
        FilterChainOp
            Complete result of the filter chain
        """
        start_time = time()
        filter_ops = []
        current_input = text
        
        # Convert initial input to string if needed
        if isinstance(text, dict):
            initial_content = str(text)  # You might want to JSON serialize this
        else:
            initial_content = text
        
        # Execute each stage
        for extraction_spec, filter_strategy in stages:
            filter_op = await self.run_async(current_input, extraction_spec, filter_strategy)
            filter_ops.append(filter_op)
            
            if not filter_op.success:
                break  # Stop on first failure
                
            current_input = filter_op.content
        
        # Build the result (same logic as sync version)
        if not filter_ops:
            return FilterChainOp(
                success=False,
                content=None,
                elapsed_time=time() - start_time,
                generation_results=[],
                usage=None,
                error="No filter operations completed",
                start_time=start_time,
                filtered_data_token_size=None,
                stages_config=stages,
                reduction_details=[],
                filterops=[]
            )
        
        # Determine overall success
        overall_success = all(op.success for op in filter_ops)
        
        # Get final content
        final_content = None
        for op in reversed(filter_ops):
            if op.success and op.content:
                final_content = op.content
                break
        
        # Calculate final token size
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        final_token_size = None
        if final_content:
            try:
                final_token_size = len(encoding.encode(final_content))
            except Exception:
                final_token_size = None
        
        # Combine usage and build results
        combined_usage = self._combine_usage([op.usage for op in filter_ops if op.usage])
        generation_results = [op.generation_result for op in filter_ops if op.generation_result]
        reduction_details = self._calculate_reduction_details(filter_ops, initial_content)
        
        # Error handling
        error_message = None
        if not overall_success:
            failed_ops = [op for op in filter_ops if not op.success]
            if failed_ops:
                error_message = f"Stage {filter_ops.index(failed_ops[0]) + 1} failed: {failed_ops[0].error}"
        
        return FilterChainOp(
            success=overall_success,
            content=final_content,
            elapsed_time=time() - start_time,
            generation_results=generation_results,
            usage=combined_usage,
            error=error_message,
            start_time=start_time,
            filtered_data_token_size=final_token_size,
            stages_config=stages,
            reduction_details=reduction_details,
            filterops=filter_ops
        )
    




def example_chain_usage():
    filter_hero = FilterHero()

    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    
    
    stages = [
        ([WhatToRetain(name="voltage", desc="all voltage information")], "contextual"),
        # ([WhatToRetain(name="voltage", desc="only voltage related information")], "inclusive"),
        # ([WhatToRetain(name="voltage", desc="only voltage related information")], "contextual"),
        ([WhatToRetain(name="voltage", desc="only voltage related information")], "base"),
    
    ]
    
    chain_result = filter_hero.chain(html_doc, stages)
    
    if chain_result.success:
        print(f"Final content: {chain_result.content}")
        print(f"Total elapsed time: {chain_result.elapsed_time:.2f}s")
        print(f"Final token size: {chain_result.filtered_data_token_size}")
        print(f"Stages completed: {len(chain_result.stages_config)}")
        
        # Print stage info
        for i, (extraction_spec, filter_strategy) in enumerate(chain_result.stages_config):
            spec_names = [spec.name for spec in extraction_spec]
            print(f"Stage {i+1}: {spec_names} using '{filter_strategy}' strategy")
        
        # Print individual stage results
        for i, filter_op in enumerate(chain_result.filterops):
            status = "✅" if filter_op.success else "❌"
            print(f"Stage {i+1} {status}: {len(filter_op.content) if filter_op.content else 0} chars, {filter_op.elapsed_time:.2f}s")
            print("Content: ")
            print(" ")
            print(filter_op.content)
            print(" ")
            print(" ")
            print(" ")


        # Print reduction details
        for i, reduction in enumerate(chain_result.reduction_details):
            reduction_percent = (1 - reduction["filtered_token_size"] / reduction["source_token_size"]) * 100
            print(f"Stage {i+1}: {reduction['source_token_size']} → {reduction['filtered_token_size']} tokens ({reduction_percent:.1f}% reduction)")
            
        # Print total cost
        if chain_result.usage and "total_cost" in chain_result.usage:
            print(f"Total cost: ${chain_result.usage['total_cost']:.4f}")
    else:
        print(f"Chain failed: {chain_result.error}")




wrt_to_source_filter_desc="""
### Task
Return **every content chunk** that is relevant to the main product
described in the page’s hero section.

### How to decide relevance
1. **Keep** a chunk if its title, brand, or descriptive text
   • matches the hero product **or**
   • is ambiguous / generic enough that it _could_ be the hero product.
2. **Discard** a chunk **only when** there is a **strong, explicit** signal
   that it belongs to a _different_ item (e.g. totally different brand,
   unrelated product type, “customers also bought” label).
3. When in doubt, **keep** the chunk (favor recall).

### Output
Return the retained chunks exactly as HTML snippets.
""".strip()



# ─────────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":


    example_chain_usage()

   
    # cfg = ExtractConfig()
    # filter_hero = FilterHero(cfg)
    
   
    # html_doc1 = """
    # <html><body>
    #   <div class="product"><h2 class="title">Wireless Keyboard</h2><span class="price">€49.99</span></div>
    #   <div class="product"><h2 class="title">USB-C Hub</h2><span class="price">€29.50</span></div>
    # </body></html>
    # """
    # html_doc2 = load_html("extracthero/simple_html_sample_2.html")
    # html_doc3 = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    

    
    # specs = [
    #     WhatToRetain(
    #         name="product titles",
    #         desc="listing name of prodct",
    #         include_context_chunk=False,
    #     )
       
    # ]


    # #filter_op = filter_hero.run(html_doc1, specs, filter_strategy="recall")

    
    # # stages = [
    # #     ([WhatToRetain(name="voltage", desc="all voltage info")], "contextual"),
    # #     ([WhatToRetain(name="precise_voltage", desc="only voltage values")], "inclusive"),
    # # ]
    
    # stages_config = [
    #     (specs, "contextual"),
    #     (specs, "inclusive"),
    # ]


 
    
    # filter_ops = filter_hero.chain(html_doc3, stages)

    
    
    
    # print("cost: ", filter_op.usage["total_cost"])

    
    # # print("")
    # # # print("prompt: ", filter_op.generation_result.generation_request.formatted_prompt)

   



    
    # print("filter_strategy:", filter_op.filter_strategy)
    
    # print("Filtered corpus: ⬇")
    # print(" ")
    # print(filter_op.content)
    
    # print(" ")
    # # print(filter_op.start_time)

    
