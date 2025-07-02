from django.http import FileResponse, Http404
from django.conf import settings
import os

def serve_protected_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404("File not found")
    return FileResponse(open(file_path, 'rb')) 