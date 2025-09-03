from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class APIResponseWrapperMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        from rest_framework.response import Response

        if isinstance(response, Response):
            data = getattr(response, "data", None)
            if data and not all(k in data for k in ("success", "message", "status", "data")):
                response.data = {
                    "success": 200 <= response.status_code < 300,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": data or {}
                }

                # mark for re-rendering
                if hasattr(response, "_is_rendered"):
                    response._is_rendered = False

        return response

    def process_template_response(self, request, response):
        # leave TemplateResponse untouched
        return response

