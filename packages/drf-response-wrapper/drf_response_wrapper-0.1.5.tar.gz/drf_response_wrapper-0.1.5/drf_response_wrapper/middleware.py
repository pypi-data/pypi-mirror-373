from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class APIResponseWrapperMiddleware(MiddlewareMixin):
    """
    Safe middleware for wrapping DRF Responses only.
    Works for Django 2.x → 5.x and Python 3.7+
    """

    def process_response(self, request, response):
        # Only wrap DRF Response
        if isinstance(response, Response):
            data = getattr(response, "data", None)

            # Skip already wrapped responses
            if data and not all(k in data for k in ("success", "message", "status", "data")):
                response.data = {
                    "success": 200 <= response.status_code < 300,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": data or {}
                }
                
                # Make sure DRF re-renders
                if hasattr(response, "_is_rendered"):
                    response._is_rendered = False

        return response
