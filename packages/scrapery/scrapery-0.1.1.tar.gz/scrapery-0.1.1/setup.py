from setuptools import setup, find_packages

# Read README with UTF-8 encoding to avoid UnicodeDecodeError on Windows
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scrapery",  # Package name
    version="0.1.1",  # Current version
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="Scrapery: A fast, lightweight library to scrape HTML, XML, and JSON using XPath, CSS selectors, and intuitive DOM navigation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Natural Language :: English"
    ],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "lxml>=4.9.2",
        "ujson>=5.8.0",
        "aiohttp>=3.8.5",
        "chardet>=5.1.0",
        "jmespath>=1.0.1"
    ],
    keywords="web scraping, html parser, xml parser, json parser, aiohttp, lxml, ujson, data extraction, scraping tools",
    include_package_data=True,
    zip_safe=False,
)
