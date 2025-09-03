from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    """API exception raised when the configured storage provider is unavailable"""

    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"
