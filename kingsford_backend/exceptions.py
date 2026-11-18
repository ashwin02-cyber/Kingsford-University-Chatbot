from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        code = getattr(exc, 'default_code', 'error')
        if hasattr(response.data, 'get') and 'detail' in response.data:
            message = response.data['detail']
        else:
            message = str(response.data)

        response.data = {
            "error": {
                "code": str(code),
                "message": message
            }
        }
    return response
