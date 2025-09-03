# middleware.py
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class APIResponseWrapperMiddleware(MiddlewareMixin):
    """
    Wraps all DRF Response objects in a standard JSON format:
    {
        "success": true/false,
        "message": "Request successful" / "Something went wrong",
        "status": HTTP status code,
        "data": { ... original data ... }
    }
    """
    def process_response(self, request, response):
        # Only process DRF Response objects
        if isinstance(response, Response):
            data = getattr(response, "data", None)
            
            # Prevent double wrapping
            if data and not all(k in data for k in ("success", "message", "status", "data")):
                response.data = {
                    "success": 200 <= response.status_code < 300,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": data or {}
                }
                
                # Ensure DRF re-renders with new data
                if hasattr(response, "_is_rendered"):
                    response._is_rendered = False

        # Leave TemplateResponse and HttpResponse untouched
        return response
