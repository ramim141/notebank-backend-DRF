from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings 
from django.conf.urls.static import static 
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from notes.views_media import serve_protected_media


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/notes/', include('notes.urls')),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  
    
    re_path(r'^media/(?P<path>.*)$', serve_protected_media),
]

# শুধুমাত্র DEBUG মোডে মিডিয়া ফাইল সার্ভ করার জন্য এই লাইনটি থাকবে
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)