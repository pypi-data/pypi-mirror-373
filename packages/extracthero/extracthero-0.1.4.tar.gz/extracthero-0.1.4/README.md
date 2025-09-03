# extracthero

Extract **accurate, structured facts** from messy real-world content — raw HTML, screenshots, PDFs, JSON blobs or plain text — with *almost zero compromise.*

--

## Why extracthero?

| Pain-point                                                       | extracthero's answer                                                                                                                                                                                        |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *DOM spaghetti* (ads, nav bars, JS widgets) pollutes extraction. Markdown converters drop dynamic/JS-rendered elements. | We use a rule-based **DomReducer** to remove non-content related HTML tags. This process is custom tailored to not destroy any structural data including tables etc. In general this gives us 20% reduction in size. Markdown converting operations are too vague to trust for prod and they usually dismiss useful data. |
| Needle in haystack is common problem. If you overwork a LLM, it can hallucinate or start outputting unstructured garbage which breaks production. | We define extraction in 2 phases. **First phase is context aware filtering**, and **second phase is parsing this filtered data**. Since LLM processes less data, the attention mechanism works better as well and more accurate results. |
| LLM prompts that just say "extract price" are brittle because in real life scenarios extraction logic is more complex and dependent on other variables. | Extracthero asks you to fill **`WhatToRetain`** specifications that include the field's `name`, `desc`, and optional `text_rules`, so the LLM knows the full context and returns *sniper-accurate* results. |
| In real life, source data comes in different formats (JSON, strings, dicts, HTML) and each requires different optimization strategies. | ExtractHero handles each data format intelligently. You can input JSON and if it can extract keys directly, it will use a fast-path. If it doesn't find what you need, you can use fallback mechanisms to route it to LLM processing for extraction. |
| Post-hoc validation is messy. | Regex/type guards live inside each `WhatToRetain`; a failed field flips `success=False`, so you can retry or send to manual review. |

---

## Key ideas

### 1  Schema-first extraction

```python
from extracthero import WhatToRetain

price_spec = WhatToRetain(
    name="price",
    desc="currency-prefixed current product price",
    regex_validator=r"€\d+\.\d{2}",
    text_rules=[
        "Ignore crossed-out promotional prices",
        "Return the live price only"
    ],
    example="€49.99"
)
```
