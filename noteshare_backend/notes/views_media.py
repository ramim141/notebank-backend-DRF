from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-production-frontend.com",  # Replace with your actual production frontend URL
]

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def serve_protected_media(request, path):
    origin = request.headers.get("Origin")
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = HttpResponse()
        if origin in ALLOWED_ORIGINS:
            response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404("File not found")
    response = FileResponse(open(file_path, 'rb'))
    if origin in ALLOWED_ORIGINS:
        response["Access-Control-Allow-Origin"] = origin
    response["Access-Control-Allow-Credentials"] = "true"
    return response 