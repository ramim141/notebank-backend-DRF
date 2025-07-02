from django.http import FileResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
import os

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
@xframe_options_exempt
def serve_protected_media(request, path):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        from django.http import HttpResponse
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404("File not found")
    response = FileResponse(open(file_path, 'rb'))
    response["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response["Access-Control-Allow-Credentials"] = "true"
    return response 