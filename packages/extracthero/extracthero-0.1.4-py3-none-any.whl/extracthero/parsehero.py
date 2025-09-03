# extracthero/parsehero.py

# run with: python -m extracthero.parsehero
"""
ParseHero — the "parse" phase of ExtractHero.
- Converts a filtered corpus into structured data keyed by WhatToRetain specs.
- Uses ParseEngine for core parsing logic.
- Returns a ParseOp.
"""

from __future__ import annotations

from time import time
from typing import Any, Dict, List, Optional, Union

from extracthero.myllmservice import MyLLMService
from extracthero.schemas import ExtractConfig, ParseOp, WhatToRetain
from extracthero.parse_engine import ParseEngine

import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=r".*extracthero\.parsehero.*"
)


class ParseHero:
    """High-level parsing orchestrator using ParseEngine for core logic."""
    
    def __init__(
        self,
        config: Optional[ExtractConfig] = None,
        llm: Optional[MyLLMService] = None,
    ):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()
        self.engine = ParseEngine(llm_service=self.llm)

    def run(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
        model_name: Optional[str] = None,
    ) -> ParseOp:
        """
        Parse the corpus into structured data using the WhatToRetain specifications.
        
        Parameters
        ----------
        corpus : str | Dict[str, Any]
            The filtered corpus to parse (text or dict)
        items : WhatToRetain | List[WhatToRetain]
            Specifications for what to extract
        enforce_llm_based_parse : bool
            Kept for compatibility (always uses LLM now)
        model_name : Optional[str]
            Specific model to use (default: gpt-4o-mini)
            
        Returns
        -------
        ParseOp
            Parsing operation result with extracted content
        """
        start_ts = time()

        # Use ParseEngine for core logic
        generation_result = self.engine.execute_parsing(
            corpus=corpus,
            items=items,
            enforce_llm_based_parse=enforce_llm_based_parse,
            model_name=model_name
        )

        # Build ParseOp result
        return ParseOp.from_result(
            config=self.config,
            content=generation_result.content,
            usage=generation_result.usage,
            start_time=start_ts,
            success=generation_result.success,
            error=generation_result.error_message,
            generation_result=generation_result
        )

    async def run_async(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
        model_name: Optional[str] = None,
    ) -> ParseOp:
        """
        Async version of run method.
        
        Parameters
        ----------
        corpus : str | Dict[str, Any]
            The filtered corpus to parse (text or dict)
        items : WhatToRetain | List[WhatToRetain]
            Specifications for what to extract
        enforce_llm_based_parse : bool
            Kept for compatibility (always uses LLM now)
        model_name : Optional[str]
            Specific model to use (default: gpt-4o-mini)
            
        Returns
        -------
        ParseOp
            Parsing operation result with extracted content
        """
        start_ts = time()

        # Use ParseEngine for core async logic
        generation_result = await self.engine.execute_parsing_async(
            corpus=corpus,
            items=items,
            enforce_llm_based_parse=enforce_llm_based_parse,
            model_name=model_name
        )

        # Build ParseOp result
        return ParseOp.from_result(
            config=self.config,
            content=generation_result.content,
            usage=generation_result.usage,
            start_time=start_ts,
            success=generation_result.success,
            error=generation_result.error_message,
            generation_result=generation_result
        )


# ────────────────────────── Usage Examples ───────────────────────────────

def example_usage():
    """Examples of using ParseHero."""
    
    from extracthero.utils import load_html
    
    hero = ParseHero()
    
    # Define what to extract
    items = [
        WhatToRetain(
            name="title", 
            desc="Product title",
            example="Wireless Keyboard Pro"
        ),
        WhatToRetain(
            name="price", 
            desc="Product price with currency",
            example="€49.99"
        ),
        WhatToRetain(
            name="rating", 
            desc="Product rating",
            example="4.5"
        ),
    ]
    
    print("🦸 ParseHero Examples")
    print("=" * 50)
    
    # Example 1: Parse filtered text
    print("\n📝 Example 1: Parse Filtered Text")
    filtered_text = """
    title: Wireless Keyboard Pro
    price: €49.99
    rating: 4.5 ★
    """
    
    result = hero.run(filtered_text, items)
    print(f"Success: {result.success}")
    print(f"Content: {result.content}")
    print(f"Elapsed: {result.elapsed_time:.2f}s")
    if result.usage:
        print(f"Cost: ${result.usage.get('total_cost', 0):.4f}")
    
    # Example 2: Parse dict input
    print("\n📝 Example 2: Parse Dict Input")
    dict_data = {
        "title": "USB-C Hub", 
        "price": "€29.50", 
        "rating": "4.1",
        "extra": "ignored"
    }
    
    result = hero.run(dict_data, items)
    print(f"Success: {result.success}")
    print(f"Content: {result.content}")
    print(f"Model: {result.generation_result.model if result.generation_result else 'None'}")
    
    # Example 3: Parse HTML snippet
    print("\n📝 Example 3: Parse HTML Snippet")
    html_snippet = """
    <div class="product">
        <h2 class="title">Gaming Mouse</h2>
        <span class="price">€35.00</span>
        <div class="rating">4.8/5</div>
    </div>
    """
    
    result = hero.run(html_snippet, items)
    print(f"Success: {result.success}")
    print(f"Content: {result.content}")
    
    # Example 4: Single item extraction
    print("\n📝 Example 4: Single Item Extraction")
    single_item = WhatToRetain(name="title", desc="Product title only")
    
    result = hero.run(filtered_text, single_item)
    print(f"Success: {result.success}")
    print(f"Content: {result.content}")
    
   
    
    # Example 5: Real HTML file (if exists)
    print("\n📝 Example 5: Real HTML File")
    try:
        html_doc = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")
        print(len(html_doc))
        voltage_spec = WhatToRetain(
            name="voltage", 
            desc="voltage specifications",
            example="5V, 3.3V"
        )
        
        result = hero.run(html_doc[5000], voltage_spec)  # Using first 500 chars
        print(f"Success: {result.success}")
        print(f"Content: {result.content}")
    except Exception as e:
        print(f"Could not load HTML file: {e}")
    
    print("\n✨ ParseHero examples completed!")


async def example_async_usage():
    """Async usage examples."""
    
    hero = ParseHero()
    items = [
        WhatToRetain(name="title", desc="Product title"),
        WhatToRetain(name="price", desc="Product price"),
    ]
    
    print("\n🚀 Async ParseHero Example")
    print("=" * 50)
    
    # Async parsing
    text = "title: Gaming Headset\nprice: €79.99"
    result = await hero.run_async(text, items)
    print(f"Async Success: {result.success}")
    print(f"Async Content: {result.content}")


# ────────────────────────── Main Demo ───────────────────────────────

if __name__ == "__main__":
    import asyncio
    
    
    
    # Run sync examples
    example_usage()
    
    # # Run async example
    # print("\n" + "=" * 50)
    # asyncio.run(example_async_usage())