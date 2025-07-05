# noteshare_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from notes.views import download_note_file # ❗️ এই লাইনটি যুক্ত করুন

urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('api/users/', include('users.urls')),
    path('api/', include('notes.urls')),
    
 
    path('download/note/<int:pk>/', download_note_file, name='secure-note-download'),

    # Schema URL
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)