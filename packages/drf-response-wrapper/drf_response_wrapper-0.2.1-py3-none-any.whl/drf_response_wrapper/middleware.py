from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

class APIResponseWrapperMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        """
        Handles TemplateResponse or DRF Response safely.
        """
        if isinstance(response, Response):
            if response.data is not None and not all(
                k in response.data for k in ("success", "message", "status", "data")
            ):
                response.data = {
                    "success": 200 <= response.status_code < 300,
                    "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                    "status": response.status_code,
                    "data": response.data,
                }
        return response

    def process_response(self, request, response):
        """
        Fallback for normal HttpResponse (non-DRF).
        """
        try:
            if hasattr(response, "data"):
                # DRF Response already handled in process_template_response
                return response

            # Regular HttpResponse
            if response.get("Content-Type", "").startswith("application/json"):
                import json
                data = json.loads(response.content.decode("utf-8"))
                if not all(k in data for k in ("success", "message", "status", "data")):
                    wrapped = {
                        "success": 200 <= response.status_code < 300,
                        "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
                        "status": response.status_code,
                        "data": data,
                    }
                    response.content = json.dumps(wrapped).encode("utf-8")
            return response
        except Exception:
            return response
