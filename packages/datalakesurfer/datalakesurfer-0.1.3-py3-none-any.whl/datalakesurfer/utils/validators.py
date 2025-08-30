import re
import logging
from urllib.parse import urlparse

class SourceValidators:
    """
    Source validation class with comprehensive logging for security and audit purposes.
    """    
    def __init__(self, logger=None):
        """
        Initialize the SourceValidators with optional logger. 
        Args:
            logger: Optional logger instance. If not provided, creates a new one.
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @classmethod
    def get_logger(cls):
        """
        Get a logger instance for static methods.
        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(__name__)
    @staticmethod
    def validate_account_url(value: str, logger=None) -> str:
        """
        Validate Azure Storage account URL with comprehensive security checks.
        Args:
            value: The account URL to validate
            logger: Optional logger instance
        Returns:
            str: The validated and sanitized account URL
        Raises:
            ValueError: If validation fails
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            
        logger.info(f"Starting account URL validation for domain extraction.")
        
        try:
            value = value.strip().rstrip('/')
            logger.info(f"Sanitized input URL format.")
            
            # Check for dangerous characters
            dangerous_chars = [';', '=', '?', ' ', '--']
            if any(c in value for c in dangerous_chars):
                logger.error(f"Account URL validation failed: contains illegal characters.")
                raise ValueError("account_url must not contain semicolons, equals, question marks, spaces, or comment markers.")

            parsed_url = urlparse(value)
            if parsed_url.scheme.lower() != "https":
                logger.error(f"Account URL validation failed: non-HTTPS scheme detected.")
                raise ValueError("account_url must use HTTPS.")

            domain = parsed_url.netloc
            logger.info(f"Extracted domain for validation.")
            
            if len(domain) > 253:
                logger.error(f"Account URL validation failed: domain too long ({len(domain)} characters).")
                raise ValueError("account_url domain is too long (max 253 characters).")

            allowed_patterns = [
                r"^[a-z0-9]{3,24}\.[a-z0-9-]+\.(dfs|blob)\.storage\.azure\.net$",
                r"^[a-z0-9]{3,24}\.(blob|dfs)\.core\.windows\.net$",
            ]
            
            pattern_matched = any(re.fullmatch(p, domain) for p in allowed_patterns)
            if not pattern_matched:
                logger.error(f"Account URL validation failed: domain pattern not recognized.")
                raise ValueError(f"Invalid account_url domain '{domain}'. Must match known Azure Storage patterns.")
            
            logger.info(f"Account URL validation successful.")
            return value
            
        except ValueError as e:
            logger.error(f"Account URL validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during account URL validation: {str(e)}")
            raise ValueError(f"Account URL validation failed due to unexpected error: {str(e)}")
    
    @staticmethod
    def validate_storage_account_name(value: str, logger=None) -> str:
        """
        Validate Azure Storage account name format.
        
        Args:
            value: The storage account name to validate
            logger: Optional logger instance
            
        Returns:
            str: The validated storage account name
            
        Raises:
            ValueError: If validation fails
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            
        logger.info("Starting storage account name validation.")
        
        try:
            if not re.fullmatch(r"^[a-z0-9]{3,24}$", value):
                logger.error(f"Storage account name validation failed: invalid format or length.")
                raise ValueError("Storage account name must be 3-24 characters long and contain only lowercase letters and numbers.")
            
            logger.info("Storage account name validation successful.")
            return value
            
        except ValueError as e:
            logger.error(f"Storage account name validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during storage account name validation: {str(e)}")
            raise ValueError(f"Storage account name validation failed due to unexpected error: {str(e)}")

    @staticmethod
    def validate_container_name(value: str, logger=None) -> str:
        """
        Validate Azure Storage container name format.
        Args:
            value: The container name to validate
            logger: Optional logger instance
        Returns:
            str: The validated container name
        Raises:
            ValueError: If validation fails
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        logger.info("Starting container name validation.")
        try:
            if not re.fullmatch(r"^(?!-)(?!.*--)[a-z0-9]([a-z0-9-]{1,61})[a-z0-9]$", value):
                logger.error(f"Container name validation failed: invalid format or contains consecutive hyphens.")
                raise ValueError("Container name must be 3-63 characters, lowercase, start/end with letter/number, and cannot contain consecutive hyphens.")
            logger.info("Container name validation successful.")
            return value
        except ValueError as e:
            logger.error(f"Container name validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during container name validation: {str(e)}")
            raise ValueError(f"Container name validation failed due to unexpected error: {str(e)}")

    @staticmethod
    def not_empty(value, logger=None):
        """
        Ensure no fields are empty with logging.
        Args:
            value: The value to validate
            logger: Optional logger instance
        Returns:
            str: The trimmed non-empty value
        Raises:
            ValueError: If value is empty or whitespace only
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            
        logger.info("Starting empty field validation.")
        try:
            if not value or value.strip() == "":
                logger.error("Field validation failed: empty or whitespace-only value.")
                raise ValueError('Field cannot be empty')
            result = value.strip()
            logger.info("Empty field validation successful.")
            return result
            
        except ValueError as e:
            logger.error(f"Empty field validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during empty field validation: {str(e)}")
            raise ValueError(f"Field validation failed due to unexpected error: {str(e)}")
    
    @staticmethod
    def validate_fabric_account_name(value, logger=None):
        """
        Only 'onelake' (all lowercase) is accepted as a valid account_name.
        Args:
            value: The account name to validate
            logger: Optional logger instance
        Returns:
            str: The validated account name
        Raises:
            ValueError: If validation fails
        """
        if logger is None:
            logger = logging.getLogger(__name__)
        logger.info("Starting Fabric account name validation.")
        try:
            if isinstance(value, str):
                value = value.strip()
            else:
                logger.error("Fabric account name validation failed: non-string value provided.")
                raise ValueError("Invalid account_name. Value must be a string.")
            
            if value.lower() != "onelake":
                logger.error(f"Fabric account name validation failed: invalid account name '{value}'.")
                raise ValueError("Invalid account_name. Only 'onelake' is allowed.")
            
            logger.info("Fabric account name validation successful.")
            return value
            
        except ValueError as e:
            logger.error(f"Fabric account name validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during Fabric account name validation: {str(e)}")
            raise ValueError(f"Fabric account name validation failed due to unexpected error: {str(e)}")    
    @staticmethod
    def validate_expires_on(value, logger=None):
        """
        Validate token expiration timestamp.
        
        Args:
            value: The expiration timestamp to validate
            logger: Optional logger instance
            
        Returns:
            int: The validated expiration timestamp
            
        Raises:
            ValueError: If validation fails
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            
        logger.info("Starting token expiration validation.")
        
        try:
            if not isinstance(value, int):
                logger.error(f"Token expiration validation failed: non-integer value provided.")
                raise ValueError("Value must be an integer")
            
            if value <= 0:
                logger.error(f"Token expiration validation failed: non-positive value.")
                raise ValueError("Value must be a positive integer")
            
            if value > 2_147_483_647:
                logger.error(f"Token expiration validation failed: value exceeds 32-bit limit.")
                raise ValueError("Value exceeds 32-bit signed integer max limit")
            
            logger.info("Token expiration validation successful.")
            return value
            
        except ValueError as e:
            logger.error(f"Token expiration validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during token expiration validation: {str(e)}")
            raise ValueError(f"Token expiration validation failed due to unexpected error: {str(e)}")