from django.urls import path
from . import admin_views as v

urlpatterns = [
    # Auth
    path('login/', v.admin_login, name='panel_login'),
    path('logout/', v.admin_logout, name='panel_logout'),

    # Dashboard
    path('', v.dashboard, name='panel_dashboard'),

    # Site Settings
    path('settings/', v.site_settings, name='panel_settings'),

    # Levels
    path('levels/', v.levels_list, name='panel_levels'),
    path('levels/add/', v.level_edit, name='panel_level_add'),
    path('levels/<int:pk>/edit/', v.level_edit, name='panel_level_edit'),
    path('levels/<int:pk>/delete/', v.level_delete, name='panel_level_delete'),

    # Questions
    path('questions/', v.questions_list, name='panel_questions'),
    path('questions/add/', v.question_edit, name='panel_question_add'),
    path('questions/<int:pk>/edit/', v.question_edit, name='panel_question_edit'),
    path('questions/<int:pk>/delete/', v.question_delete, name='panel_question_delete'),

    # Categories
    path('categories/', v.categories_list, name='panel_categories'),
    path('categories/add/', v.category_edit, name='panel_category_add'),
    path('categories/<int:pk>/edit/', v.category_edit, name='panel_category_edit'),
    path('categories/<int:pk>/delete/', v.category_delete, name='panel_category_delete'),

    # Exams
    path('exams/', v.exams_list, name='panel_exams'),
    path('exams/<int:pk>/', v.exam_detail, name='panel_exam_detail'),
    path('exams/<int:pk>/delete/', v.exam_delete, name='panel_exam_delete'),

    # Students
    path('students/', v.students_list, name='panel_students'),
    path('students/<int:pk>/delete/', v.student_delete, name='panel_student_delete'),

    # Teachers
    path('teachers/', v.teachers_list, name='panel_teachers'),
    path('teachers/<int:pk>/delete/', v.teacher_delete, name='panel_teacher_delete'),

    # Months
    path('months/', v.months_list, name='panel_months'),
    path('months/add/', v.month_edit, name='panel_month_add'),
    path('months/<int:pk>/edit/', v.month_edit, name='panel_month_edit'),
    path('months/<int:pk>/delete/', v.month_delete, name='panel_month_delete'),
]
