# extracthero/filter_engine.py
"""
FilterEngine - Core filtering logic used by FilterHero.
Handles LLM dispatch, pipeline execution, and result aggregation.

python -m extracthero.filter_engine
"""

from __future__ import annotations

import json as _json
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio

from llmservice import GenerationResult
from extracthero.myllmservice import MyLLMService
from extracthero.schemas import WhatToRetain
from extracthero.utils import load_html




class FilterEngine:
    """
    Core filtering engine that handles LLM dispatch and multi-stage pipelines.
    Used by FilterHero as the execution engine.
    """
    
    def __init__(self, llm_service: Optional[MyLLMService] = None):
        self.llm = llm_service or MyLLMService()
    
 

    def execute_filtering(
        self,
        corpus: str,
        extraction_spec: Union[WhatToRetain, List[WhatToRetain]],
        strategy: str,
        model_name: Optional[str] = None
    ) -> Tuple[Any, Optional[Dict[str, int]], GenerationResult]:
        
        if isinstance(extraction_spec, WhatToRetain):
            target_desc = extraction_spec.desc
        else:
            target_desc = "; ".join(spec.desc for spec in extraction_spec)
        
        
        gen_results = self.llm.filter_via_llm(
                corpus, 
                target_desc, 
                filter_strategy=strategy,
                model=model_name
            )
        
        return gen_results
        #return gen_results.content, gen_results.usage, gen_results
    
    
    async def execute_filtering_async(
        self,
        corpus: str,
        extraction_spec: Union[WhatToRetain, List[WhatToRetain]],
        strategy: str,
        model_name: Optional[str] = None
    ) -> Tuple[Any, Optional[Dict[str, int]], GenerationResult]:
        


        if isinstance(extraction_spec, WhatToRetain):
            target_desc = extraction_spec.desc
        else:
            target_desc = "; ".join(spec.desc for spec in extraction_spec)
        
        
        gen_results = await self.llm.filter_via_llm_async(
                corpus, 
                target_desc, 
                filter_strategy=strategy,
                model=model_name
            )
        

        return gen_results
        
       
    



# ─────────────────────────────── demo ───────────────────────────────
if __name__ == "__main__":
    filter_engine=FilterEngine()
   
    specs = [
        WhatToRetain(
            name="name",
            desc="all information about name",
            include_context_chunk=False,
        )
    ]
    
    html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
    dummy_sample="""
    New york is too hot
     
    My name is Enes"""

    gen_results=filter_engine.execute_filtering(dummy_sample,
                                    extraction_spec=specs, 
                                    strategy="liberal", 
                                    model_name="gpt-4o-mini" )
    
   

    print(gen_results.content)
    
    
    