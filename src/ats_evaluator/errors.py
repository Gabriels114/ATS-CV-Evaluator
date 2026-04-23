class ATSError(Exception):
    """Base exception for all ATS evaluator errors."""


class UnparseableDocumentError(ATSError):
    """Raised when a document cannot be parsed (e.g., scanned PDF with no text)."""


class ExtractionError(ATSError):
    """Raised when Claude fails to extract structured data from a document."""


class InvalidExtractionError(ExtractionError):
    """Raised when Claude's output fails schema validation after retries."""


class ConfigurationError(ATSError):
    """Raised for missing or invalid configuration (e.g., no API key)."""


class ScoringError(ATSError):
    """Raised when the scoring engine encounters an unrecoverable state."""
