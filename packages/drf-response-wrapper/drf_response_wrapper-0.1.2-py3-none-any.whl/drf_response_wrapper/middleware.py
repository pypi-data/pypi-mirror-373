from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework import status

class APIResponseWrapperMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        # Skip template responses
        return response

    def process_response(self, request, response):
        # Only wrap DRF Response objects
        if isinstance(response, Response):
            # If response.data already has our keys, don't double-wrap
            if not all(k in response.data for k in ("success", "message", "status", "data")):
                wrapped_data = {
                    "success": True if 200 <= response.status_code < 300 else False,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": response.data or {}
                }
                response.data = wrapped_data
                response._is_rendered = False  # Force DRF to re-render with new data
        return response
