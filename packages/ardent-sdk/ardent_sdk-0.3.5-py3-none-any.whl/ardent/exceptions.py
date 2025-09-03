class ArdentError(Exception):
    """Base exception for Ardent SDK"""
    pass

class ArdentAPIError(ArdentError):
    """Raised when API returns an error response"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ArdentAuthError(ArdentError):
    """Raised when authentication fails"""
    pass

class ArdentValidationError(ArdentError):
    """Raised when input validation fails"""
    pass