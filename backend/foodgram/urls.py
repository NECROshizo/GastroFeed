from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),

    # re_path(r'^auth/', include('djoser.urls')),
    # re_path(r'^auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
