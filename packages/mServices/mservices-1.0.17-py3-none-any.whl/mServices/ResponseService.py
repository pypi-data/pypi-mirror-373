from django.core.serializers import serialize
from django.http import JsonResponse
from django.conf import settings
from django.forms.models import model_to_dict  # Add this

class ResponseService:
    @staticmethod
    def response(status_key, result=None, message=None, system_code=None):
        try:
            http_status_codes = {
                'SUCCESS': {'code': 200, 'success': True, 'message': 'Success'},
                'NOT_FOUND': {'code': 404, 'success': False, 'message': 'The requested resource was not found'},
                'FORBIDDEN': {'code': 403, 'success': False, 'message': 'Permission denied'},
                'INTERNAL_SERVER_ERROR': {'code': 500, 'success': False, 'message': 'An error occurred while processing the request'},
                'VALIDATION_ERROR': {'code': 417, 'success': False, 'message': 'There was a validation error'},
                'UNAUTHORIZED': {'code': 401, 'success': False, 'message': 'Unauthorized'},
                'CONFLICT': {'code': 409, 'success': False, 'message': 'Conflict'}
            }

            http_status = http_status_codes.get(status_key)

            # Auto-serialize Django model instances
            if hasattr(result, '_meta'):  # Single model instance
                result = model_to_dict(result)
            elif isinstance(result, list) and len(result) > 0 and hasattr(result[0], '_meta'):  # List of model instances
                result = [model_to_dict(item) for item in result]

            response_data = {
                'is_success': http_status['success'],
                'message': message if message else http_status['message'],
                'result': result,
                'system_code': system_code or ''
            }

            return JsonResponse(response_data, status=http_status['code'])
        except Exception as e:
            return JsonResponse({'message': 'Please check the response service', 'result': str(e)}, status=500)