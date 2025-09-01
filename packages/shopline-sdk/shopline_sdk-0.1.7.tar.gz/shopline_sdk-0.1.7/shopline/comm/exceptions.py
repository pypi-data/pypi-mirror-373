#!/usr/bin/python3
# @Time    : 2025-07-03
# @Author  : Kevin Kong (kfx2007@163.com)

class ShoplineException(Exception):
    """Base exception class for Shopline SDK."""
    
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ShoplineAPIException(ShoplineException):
    """Exception raised when API requests fail."""
    
    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message, error_code)
        self.status_code = status_code


class ShoplineAuthenticationException(ShoplineException):
    """Exception raised when authentication fails."""
    pass


class ShoplineValidationException(ShoplineException):
    """Exception raised when data validation fails."""
    pass


class ShoplineConfigurationException(ShoplineException):
    """Exception raised when configuration is invalid."""
    pass