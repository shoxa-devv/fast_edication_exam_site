from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('categories/', views.get_categories, name='categories'),
    path('questions/', views.get_questions, name='questions'),
    path('detect-ai/', views.detect_ai, name='detect_ai'),
    path('ai-assist/', views.ai_assist, name='ai_assist'),
    path('submit-exam/', views.submit_exam, name='submit_exam'),
    path('exam-results/<str:exam_id>/', views.get_exam_results, name='exam_results'),
]
