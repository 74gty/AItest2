class FindataError(Exception):
    def __init__(self, code, message, status_code=400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def error_response(error):
    return {
        "success": False,
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
