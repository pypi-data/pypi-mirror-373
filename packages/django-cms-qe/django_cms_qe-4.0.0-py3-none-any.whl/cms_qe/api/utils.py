"""
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'cms_qe.api.utils.exception_handler'
}
"""
from rest_framework.response import Response
from rest_framework.views import exception_handler as rest_exception_handler


def exception_handler(exc: Exception, context: dict) -> Response:
    response = rest_exception_handler(exc, context)
    if response is not None:
        response.data["error"] = {"message": response.data.get("detail")}
    return response
