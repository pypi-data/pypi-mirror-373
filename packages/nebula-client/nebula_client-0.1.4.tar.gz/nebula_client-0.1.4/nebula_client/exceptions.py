"""
Custom exceptions for the Nebula Simple SDK
"""


class NebulaException(Exception):
    """Base exception for Nebula API errors"""
    
    def __init__(self, message: str, status_code: int = None, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"Nebula API Error ({self.status_code}): {self.message}"
        return f"Nebula API Error: {self.message}"


class NebulaClientException(Exception):
    """Exception for client-side errors (network, configuration, etc.)"""
    
    def __init__(self, message: str, original_exception: Exception = None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)
    
    def __str__(self):
        return f"Nebula Client Error: {self.message}"


class NebulaAuthenticationException(NebulaException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class NebulaRateLimitException(NebulaException):
    """Exception for rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class NebulaValidationException(NebulaException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)


class NebulaClusterNotFoundException(NebulaException):
    """Exception for missing clusters during client validation"""
    
    def __init__(self, cluster_id: str):
        super().__init__(f"Cluster not found: {cluster_id}", status_code=404) 