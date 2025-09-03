from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class APIResponseWrapperMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Wrap only DRF Response objects
        if isinstance(response, Response):
            # Prevent double-wrapping
            if not all(k in response.data for k in ("success", "message", "status", "data")):
                wrapped_data = {
                    "success": True if 200 <= response.status_code < 300 else False,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": response.data or {}
                }
                response.data = wrapped_data
                response._is_rendered = False  # Force DRF to re-render
        # Otherwise, do nothing (template / normal HttpResponse)
        return response
