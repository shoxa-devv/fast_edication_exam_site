"""URL configuration for exam_site project."""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', include('exams.admin_urls')),
    path('api/', include('exams.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]

# In DEBUG mode, django.contrib.staticfiles handles /static/ automatically
# from STATICFILES_DIRS. Only add media serving.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
