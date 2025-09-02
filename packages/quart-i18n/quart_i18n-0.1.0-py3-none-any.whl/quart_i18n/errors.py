class I18nError(Exception):
    """Base exception for all i18n-related errors."""
    
class ConfigNotFoundError(I18nError):
    """Raised when the config directory or file is missing."""

class InvalidConfigError(I18nError):
    """Raised when a config file exists but cannot be parsed."""

class MissingPageError(I18nError):
    """Raised when a page-specific localization JSON is missing."""

class LanguageNotSupportedError(I18nError):
    """Raised when a requested language is not in the Language enum."""
