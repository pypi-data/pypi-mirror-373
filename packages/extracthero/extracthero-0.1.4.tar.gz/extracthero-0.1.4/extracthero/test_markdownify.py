
# to run python -m extracthero.test_markdownify

from markdownify import markdownify as md
from extracthero.utils import load_html


html_doc1 = """
<html><body>
    <div class="product"><h2 class="title">Wireless Keyboard</h2><span class="price">€49.99</span></div>
    <div class="product"><h2 class="title">USB-C Hub</h2><span class="price">€29.50</span></div>
</body></html>
"""

r=md(html_doc1)
print(r)


import html2text

r=html2text.html2text(html_doc1)
print(r)



#html_doc2 = load_html("extracthero/simple_html_sample_2.html")
# r=md(html_doc2)
# print(r)
# html_doc3 = load_html("extracthero/real_life_samples/1/nexperia-aa4afebbd10348ec91358f07facf06f1.html")

