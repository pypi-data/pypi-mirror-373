# extracthero/parse_engine.py

# to run python -m extracthero.parse_engine

from typing import Any, Dict, List, Optional, Union
from llmservice.generation_engine import GenerationResult
from extracthero.myllmservice import MyLLMService
from extracthero.schemas import WhatToRetain


class ParseEngine:
    """Core parsing engine that handles LLM parsing for all inputs.
    
    Converts dict inputs to string format and uses LLM for parsing.
    """
    
    def __init__(self, llm_service: MyLLMService):
        self.llm = llm_service or MyLLMService()
    
    def execute_parsing(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
        model_name: Optional[str] = None
    ) -> GenerationResult:
        """
        Execute parsing using LLM.
        
        Always uses LLM parsing for all inputs.
        """
        return self._parse_via_llm(corpus, items, model_name)

    async def execute_parsing_async(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
        model_name: Optional[str] = None
    ) -> GenerationResult:
        """Async version of execute_parsing."""
        return await self._parse_via_llm_async(corpus, items, model_name)

    # ──────────────────────── Private Methods ────────────────────────

    def _parse_via_llm(
        self, 
        corpus: str | Dict[str, Any], 
        items: WhatToRetain | List[WhatToRetain],
        model_name: Optional[str] = None
    ) -> GenerationResult:
        """Parse using LLM for all inputs."""
        try:
            # Convert corpus to string if needed
            corpus_str = self._convert_corpus_to_string(corpus)
            
            # Build parsing prompt
            prompt = self._build_parsing_prompt(items)
            
            # Use provided model or default
            model = model_name or "gpt-4o-mini"
            
            # Call LLM
            return self.llm.parse_via_llm(corpus_str, prompt, model=model)
            
        except Exception as e:
            return GenerationResult(
                success=False,
                trace_id="llm_parsing_error",
                content=None,
                usage={},
                error_message=f"LLM parsing failed: {str(e)}",
                model=model_name
            )

    async def _parse_via_llm_async(
        self, 
        corpus: str | Dict[str, Any], 
        items: WhatToRetain | List[WhatToRetain],
        model_name: Optional[str] = None
    ) -> GenerationResult:
        """Async LLM parsing."""
        try:
            # Convert corpus to string if needed
            corpus_str = self._convert_corpus_to_string(corpus)
            
            # Build parsing prompt
            prompt = self._build_parsing_prompt(items)
            
            # Use provided model or default
            model = model_name or "gpt-4o-mini"
            
            # Call async LLM
            return await self.llm.parse_via_llm_async(corpus_str, prompt, model=model)
            
        except Exception as e:
            return GenerationResult(
                success=False,
                trace_id="async_llm_parsing_error",
                content=None,
                usage={},
                error_message=f"Async LLM parsing failed: {str(e)}",
                model=model_name
            )

    # ──────────────────────── Helper Methods ────────────────────────

    def _convert_corpus_to_string(self, corpus: str | Dict[str, Any]) -> str:
        """Convert corpus to string format for LLM processing."""
        if isinstance(corpus, str):
            return corpus
        elif isinstance(corpus, dict):
            # Convert dict to readable key-value format
            lines = []
            for key, value in corpus.items():
                lines.append(f"{key}: {value}")
            return "\n".join(lines)
        else:
            # For any other type, convert to string
            return str(corpus)

    def _build_parsing_prompt(self, items: WhatToRetain | List[WhatToRetain]) -> str:
        """Build the parsing prompt from WhatToRetain specifications."""
        if isinstance(items, WhatToRetain):
            return items.compile_parser()
        else:
            return "\n\n".join(item.compile_parser() for item in items)


# ────────────────────────── ParseEngine Demo/Testing ──────────────────────────

def main():
    """Test ParseEngine independently."""
    print("🧪 Testing ParseEngine independently")
    print("=" * 50)
    
    # Initialize engine
    from extracthero.myllmservice import MyLLMService
    llm = MyLLMService()
    engine = ParseEngine(llm_service=llm)
    
    # Test items
    items = [
        WhatToRetain(name="title", desc="Product title", example="Wireless Keyboard"),
        WhatToRetain(name="price", desc="Product price with currency", example="€49.99"),
        WhatToRetain(name="rating", desc="Product rating", example="4.5")
    ]
    
    print("\n📋 Test Items:")
    for item in items:
        print(f"  - {item.name}: {item.desc}")
    
    # Test 1: Dict Input → LLM
    print("\n🔍 Test 1: Dict Input (Converted to String → LLM)")
    dict_data = {
        "title": "Gaming Mouse Pro",
        "price": "€39.99", 
        "rating": "4.7",
        "extra_field": "should be ignored"
    }
    
    result = engine.execute_parsing(dict_data, items)
    print(f"  Success: {result.success}")
    print(f"  Content: {result.content}")
    print(f"  Model used: {result.model}")
    if result.usage:
        print(f"  Cost: ${result.usage.get('total_cost', 0):.4f}")
    
    # Test 2: String Input → LLM
    print("\n🔍 Test 2: String Input → LLM")
    string_data = """
    title: USB-C Hub
    price: €29.50
    rating: 4.1
    description: 7-in-1 hub
    """
    
    result = engine.execute_parsing(string_data, items)
    print(f"  Success: {result.success}")
    print(f"  Content: {result.content}")



if __name__ == "__main__":
    main()
