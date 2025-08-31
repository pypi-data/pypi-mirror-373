class ScraperyError(Exception):
    """Base exception for scrapery library."""
    pass

class ParserError(ScraperyError):
    """Exception raised for parsing errors."""
    pass

class ValidationError(ScraperyError):
    """Exception raised for validation errors."""
    pass

class SelectorError(ScraperyError):
    """Exception raised for selector errors."""
    pass

class FileError(ScraperyError):
    """Exception raised for file-related errors."""
    pass

class NetworkError(ScraperyError):
    """Exception raised for network errors."""
    pass

class EncodingError(ScraperyError):
    """Exception raised for encoding-related errors."""
    pass