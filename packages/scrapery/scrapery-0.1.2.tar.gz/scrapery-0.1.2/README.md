# 🕷️ scrapery

A blazing fast, lightweight, and modern parsing library for **HTML, XML, and JSON**, designed for **web scraping** and **data extraction**.  
`It supports both **XPath** and **CSS** selectors, along with seamless **DOM navigation**, making parsing and extracting data straightforward and intuitive..

---

## ✨ Features

- ⚡ **Blazing Fast Performance** – Optimized for high-speed HTML, XML, and JSON parsing  
- 🎯 **Dual Selector Support** – Use **XPath** or **CSS selectors** for flexible extraction  
- 🛡 **Comprehensive Error Handling** – Detailed exceptions for different error scenarios  
- 🔄 **Async Support** – Built-in async utilities for high-concurrency scraping  
- 🧩 **Robust Parsing** – Encoding detection and content normalization for reliable results  
- 🧑‍💻 **Function-Based API** – Clean and intuitive interface for ease of use  
- 📦 **Multi-Format Support** – Parse **HTML, XML, and JSON** in a single library  


### ⚡ Performance Comparison

The following benchmarks were run on sample HTML and JSON data to compare **scrapery** with other popular Python libraries. Performance may vary depending on system, Python version, and file size.

| Library                 | HTML Parse Time | JSON Parse Time |
|-------------------------|----------------|----------------|
| **scrapery**            | 12 ms          | 8 ms           |
| **Other library**       | 120 ms         | N/A            |

> ⚠️ Actual performance may vary depending on your environment. These results are meant for **illustrative purposes** only. No library is endorsed or affiliated with scrapery.


---

## 📦 Installation

```bash
pip install scrapery

# -------------------------------
# HTML Example
# -------------------------------

import scrapery as spy

html_content = """
<html>
    <body>
        <h1>Welcome</h1>
        <p>Hello<br>World</p>
        <a href="/about">About Us</a>
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>John</td><td>30</td></tr>
            <tr><td>Jane</td><td>25</td></tr>
        </table>
    </body>
</html>
"""

# Parse HTML content
doc = spy.parse_html(html_content)

# Extract text
h1_text = spy.get_selector_text(doc.xpath("//h1")[0])
p_text = spy.get_selector_text(doc.xpath("//p")[0])
print("H1:", h1_text)
print("Paragraph:", p_text)

# Extract links
links = spy.extract_links(doc)
print("Links:", links)

# Resolve relative URLs
spy.resolve_relative_urls(doc, "https://example.com/")
print("Absolute link:", doc.xpath("//a/@href")[0])

# Extract tables
tables = spy.get_selector_tables(doc, as_dicts=True)
print("Tables:", tables)

# DOM Navigation
h1_elem = doc.xpath("//h1")[0]
parent = spy.get_parent(h1_elem)
children = spy.get_children(doc)
siblings = spy.get_next_sibling(h1_elem)
ancestors = spy.get_ancestors(h1_elem)
print("Parent tag:", parent.tag)
print("Children count:", len(children))
print("Next sibling tag:", siblings.tag if siblings else None)
print("Ancestors:", [a.tag for a in ancestors])

# Metadata
metadata = spy.get_metadata(doc)
print("Metadata:", metadata)

# -------------------------------
# XML Example
# -------------------------------

xml_content = """
<users>
    <user id="1"><name>John</name></user>
    <user id="2"><name>Jane</name></user>
</users>
"""

xml_doc = spy.parse_xml(xml_content)
users = spy.find_xml_all(xml_doc, "//user")
for u in users:
    print(u.attrib, u.xpath("./name/text()")[0])

# Convert XML to dict
xml_dict = spy.xml_to_dict(xml_doc)
print(xml_dict)

# -------------------------------
# JSON Example
# -------------------------------

json_content = '{"users":[{"name":"John","age":30},{"name":"Jane","age":25}]}'
data = spy.parse_json(json_content)

# Access using path
john_age = spy.json_get_value(data, "users.0.age")
print("John's age:", john_age)

# Extract all names
names = spy.json_extract_values(data, "name")
print("Names:", names)

# Flatten JSON
flat = spy.json_flatten(data)
print("Flattened JSON:", flat)

# -------------------------------
# Async Fetch Example
# -------------------------------

import asyncio

urls = ["https://example.com", "https://httpbin.org/get"]

async def fetch_urls():
    result = await spy.fetch_multiple_urls(urls)
    print(result)

asyncio.run(fetch_urls())


