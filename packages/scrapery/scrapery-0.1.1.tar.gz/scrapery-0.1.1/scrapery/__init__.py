"""
Scrapery - A high-performance web scraping library
"""
from .html import *
from .xml import *
from .json import *
from .utils import *
from .async_utils import *
from .exceptions import *

__version__ = "0.1.1"

# Gather all __all__ from submodules to define the public API
__all__ = (
    html.__all__
    + xml.__all__
    + json.__all__
    + utils.__all__
    + async_utils.__all__
    # + exceptions.__all__
)
