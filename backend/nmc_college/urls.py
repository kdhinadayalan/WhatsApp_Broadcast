from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('contacts.urls')),
    path('api/', include('wa_templates.urls')),
    path('api/', include('broadcasts.urls')),
    path('api/', include('whatsapp_integration.urls')),
    path('api/ai-assistant/', include('ai_assistant.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

