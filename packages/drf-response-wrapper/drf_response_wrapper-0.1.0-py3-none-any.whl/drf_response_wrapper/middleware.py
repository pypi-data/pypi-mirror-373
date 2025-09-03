from rest_framework.response import Response
from django.http import JsonResponse

class APIResponseWrapperMiddleware:
    """
    সব DRF API response কে wrap করবে একই format এ
    { success, message, status, data }
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # DRF Response wrap
        if isinstance(response, Response):
            # response already wrapped 
            if "success" not in response.data:
                data = response.data
                status_code = response.status_code
                wrapped = {
                    "success": 200 <= status_code < 300,
                    "message": "Request successful" if 200 <= status_code < 300 else "Request failed",
                    "status": status_code,
                    "data": data or {}
                }
                response.data = wrapped
                response.content_type = "application/json"

        return response
