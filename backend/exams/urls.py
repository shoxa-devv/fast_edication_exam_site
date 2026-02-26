from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('levels/', views.get_levels, name='levels'),
    path('levels/<slug:level_slug>/months/', views.get_months, name='months'),
    path('levels/<slug:level_slug>/months/<int:month_number>/questions/',
         views.get_questions, name='questions'),
    path('levels/<slug:level_slug>/months/<int:month_number>/vocabulary/',
         views.get_vocabulary, name='vocabulary'),
    path('submit-exam/', views.submit_exam, name='submit_exam'),
    path('check-ai/', views.check_ai, name='check_ai'),
]
