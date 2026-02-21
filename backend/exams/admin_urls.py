from django.urls import path
from . import admin_views as v

urlpatterns = [
    path('login/', v.admin_login, name='panel_login'),
    path('logout/', v.admin_logout, name='panel_logout'),
    path('', v.dashboard, name='panel_dashboard'),
    path('questions/', v.questions_list, name='panel_questions'),
    path('questions/add/', v.question_edit, name='panel_question_add'),
    path('questions/<int:pk>/edit/', v.question_edit, name='panel_question_edit'),
    path('questions/<int:pk>/delete/', v.question_delete, name='panel_question_delete'),
    path('exams/', v.exams_list, name='panel_exams'),
    path('exams/<int:pk>/', v.exam_detail, name='panel_exam_detail'),
    path('users/', v.users_list, name='panel_users'),
    path('categories/', v.categories_list, name='panel_categories'),
    path('categories/add/', v.category_edit, name='panel_category_add'),
    path('categories/<int:pk>/edit/', v.category_edit, name='panel_category_edit'),
]
