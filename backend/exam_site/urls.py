from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from exams.views import certificate_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('exams.urls')),
    path('certificate/<str:session_id>/', certificate_view, name='certificate'),
    path('', TemplateView.as_view(template_name='index.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
