"""Custom admin panel views — fully built from scratch."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    SiteSettings, Teacher, Level, Month, Category, Question,
    VocabularyWord, Student, ExamSession, Answer
)
import json

staff_required = user_passes_test(lambda u: u.is_staff)


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('/admin/')
        error = 'Login yoki parol noto\'g\'ri.'
    return render(request, 'panel/login.html', {'error': error})


def admin_logout(request):
    logout(request)
    return redirect('/admin/login/')


@login_required(login_url='/admin/login/')
@staff_required
def dashboard(request):
    ctx = {
        'total_questions': Question.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_exams': ExamSession.objects.count(),
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_levels': Level.objects.filter(is_active=True).count(),
        'recent_exams': ExamSession.objects.select_related(
            'student', 'level', 'month'
        ).order_by('-started_at')[:10],
    }
    return render(request, 'panel/dashboard.html', ctx)


# ── Site Settings ──
@login_required(login_url='/admin/login/')
@staff_required
def site_settings(request):
    settings_obj = SiteSettings.load()
    saved = False

    if request.method == 'POST':
        settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
        settings_obj.tagline = request.POST.get('tagline', settings_obj.tagline)

        if request.FILES.get('logo'):
            settings_obj.logo = request.FILES['logo']
        if request.FILES.get('hero_image'):
            settings_obj.hero_image = request.FILES['hero_image']
        if request.FILES.get('certificate_bg'):
            settings_obj.certificate_bg = request.FILES['certificate_bg']
        if request.FILES.get('certificate_stamp'):
            settings_obj.certificate_stamp = request.FILES['certificate_stamp']

        # Handle image removal
        if request.POST.get('remove_logo') == '1':
            settings_obj.logo = None
        if request.POST.get('remove_hero_image') == '1':
            settings_obj.hero_image = None
        if request.POST.get('remove_certificate_bg') == '1':
            settings_obj.certificate_bg = None
        if request.POST.get('remove_certificate_stamp') == '1':
            settings_obj.certificate_stamp = None

        settings_obj.save()
        saved = True

    return render(request, 'panel/settings.html', {
        'settings': settings_obj,
        'saved': saved,
    })


# ── Levels ──
@login_required(login_url='/admin/login/')
@staff_required
def levels_list(request):
    levels = Level.objects.order_by('order')
    return render(request, 'panel/levels.html', {'levels': levels})


@login_required(login_url='/admin/login/')
@staff_required
def level_edit(request, pk=None):
    level = get_object_or_404(Level, pk=pk) if pk else None

    if request.method == 'POST':
        name = request.POST.get('name', '')
        slug = request.POST.get('slug', '')
        description = request.POST.get('description', '')
        order = request.POST.get('order', 0)
        color = request.POST.get('color', '#002147')
        icon = request.POST.get('icon', '📚')
        is_active = request.POST.get('is_active') == 'on'

        data = {
            'name': name,
            'slug': slug,
            'description': description,
            'order': int(order) if order else 0,
            'color': color,
            'icon': icon,
            'is_active': is_active,
        }

        if level:
            for k, v in data.items():
                setattr(level, k, v)
            if request.FILES.get('image'):
                level.image = request.FILES['image']
            if request.POST.get('remove_image') == '1':
                level.image = None
            level.save()
        else:
            level = Level(**data)
            if request.FILES.get('image'):
                level.image = request.FILES['image']
            level.save()

        return redirect('/admin/levels/')

    return render(request, 'panel/level_form.html', {'level': level})


@login_required(login_url='/admin/login/')
@staff_required
def level_delete(request, pk):
    level = get_object_or_404(Level, pk=pk)
    level.delete()
    return redirect('/admin/levels/')


# ── Questions ──
@login_required(login_url='/admin/login/')
@staff_required
def questions_list(request):
    cat_filter = request.GET.get('category', '')
    level_filter = request.GET.get('level', '')
    qs = Question.objects.select_related('category', 'level', 'month').order_by(
        'level__order', 'month__number', 'category__order', 'order', 'id'
    )
    if cat_filter:
        qs = qs.filter(category__slug=cat_filter)
    if level_filter:
        qs = qs.filter(level__slug=level_filter)
    categories = Category.objects.order_by('order')
    levels = Level.objects.order_by('order')
    return render(request, 'panel/questions.html', {
        'questions': qs, 'categories': categories,
        'levels': levels, 'current_cat': cat_filter, 'current_level': level_filter,
    })


@login_required(login_url='/admin/login/')
@staff_required
def question_edit(request, pk=None):
    question = get_object_or_404(Question, pk=pk) if pk else None
    categories = Category.objects.order_by('order')
    levels = Level.objects.order_by('order')
    months = Month.objects.order_by('level__order', 'number')

    if request.method == 'POST':
        cat_id = request.POST.get('category')
        level_id = request.POST.get('level')
        month_id = request.POST.get('month')
        q_type = request.POST.get('question_type')
        q_text = request.POST.get('question_text', '')
        instructions = request.POST.get('instructions', '')
        correct_idx = request.POST.get('correct_answer_index')
        points = request.POST.get('points', 1)
        min_words = request.POST.get('min_words', 0)
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'

        options = []
        for i in range(6):
            opt = request.POST.get(f'option_{i}', '').strip()
            if opt:
                options.append(opt)

        data = {
            'category_id': cat_id,
            'level_id': level_id,
            'month_id': month_id,
            'question_type': q_type,
            'question_text': q_text,
            'instructions': instructions,
            'options': options if options else None,
            'correct_answer_index': int(correct_idx) if correct_idx and correct_idx.isdigit() else None,
            'points': int(points) if points else 1,
            'min_words': int(min_words) if min_words else 0,
            'order': int(order) if order else 0,
            'is_active': is_active,
        }

        if question:
            for k, v in data.items():
                setattr(question, k, v)
            question.save()
        else:
            question = Question.objects.create(**data)

        return redirect('/admin/questions/')

    return render(request, 'panel/question_form.html', {
        'question': question, 'categories': categories,
        'levels': levels, 'months': months,
    })


@login_required(login_url='/admin/login/')
@staff_required
def question_delete(request, pk):
    q = get_object_or_404(Question, pk=pk)
    q.delete()
    return redirect('/admin/questions/')


# ── Categories ──
@login_required(login_url='/admin/login/')
@staff_required
def categories_list(request):
    cats = Category.objects.order_by('order')
    return render(request, 'panel/categories.html', {'categories': cats})


@login_required(login_url='/admin/login/')
@staff_required
def category_edit(request, pk=None):
    cat = get_object_or_404(Category, pk=pk) if pk else None
    if request.method == 'POST':
        name = request.POST.get('name', '')
        slug = request.POST.get('slug', '')
        desc = request.POST.get('description', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        data = {'name': name, 'slug': slug, 'description': desc, 'order': int(order), 'is_active': is_active}
        if cat:
            for k, v in data.items():
                setattr(cat, k, v)
            cat.save()
        else:
            Category.objects.create(**data)
        return redirect('/admin/categories/')
    return render(request, 'panel/category_form.html', {'category': cat})


@login_required(login_url='/admin/login/')
@staff_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    return redirect('/admin/categories/')


# ── Exams ──
@login_required(login_url='/admin/login/')
@staff_required
def exams_list(request):
    exams = ExamSession.objects.select_related(
        'student', 'student__teacher', 'level', 'month'
    ).order_by('-started_at')
    return render(request, 'panel/exams.html', {'exams': exams})


@login_required(login_url='/admin/login/')
@staff_required
def exam_detail(request, pk):
    exam = get_object_or_404(ExamSession, pk=pk)
    answers = exam.answers.select_related(
        'question', 'question__category'
    ).order_by('question__category__order', 'question__order')
    return render(request, 'panel/exam_detail.html', {'exam': exam, 'answers': answers})


@login_required(login_url='/admin/login/')
@staff_required
def exam_delete(request, pk):
    exam = get_object_or_404(ExamSession, pk=pk)
    exam.delete()
    return redirect('/admin/exams/')


# ── Students ──
@login_required(login_url='/admin/login/')
@staff_required
def students_list(request):
    students = Student.objects.select_related('teacher').order_by('-created_at')
    student_data = []
    for s in students:
        exam_count = s.exam_sessions.count()
        student_data.append({'student': s, 'exam_count': exam_count})
    return render(request, 'panel/students.html', {'students': student_data})


@login_required(login_url='/admin/login/')
@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('/admin/students/')


# ── Teachers ──
@login_required(login_url='/admin/login/')
@staff_required
def teachers_list(request):
    teachers = Teacher.objects.order_by('last_name', 'first_name')
    teacher_data = []
    for t in teachers:
        student_count = t.students.count()
        teacher_data.append({'teacher': t, 'student_count': student_count})
    return render(request, 'panel/teachers.html', {'teachers': teacher_data})


@login_required(login_url='/admin/login/')
@staff_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    return redirect('/admin/teachers/')


# ── Months ──
@login_required(login_url='/admin/login/')
@staff_required
def months_list(request):
    months = Month.objects.select_related('level').order_by('level__order', 'number')
    return render(request, 'panel/months.html', {'months': months})


@login_required(login_url='/admin/login/')
@staff_required
def month_edit(request, pk=None):
    month = get_object_or_404(Month, pk=pk) if pk else None
    levels = Level.objects.order_by('order')

    if request.method == 'POST':
        level_id = request.POST.get('level')
        number = request.POST.get('number', 1)
        name = request.POST.get('name', '')
        is_active = request.POST.get('is_active') == 'on'

        data = {
            'level_id': level_id,
            'number': int(number),
            'name': name,
            'is_active': is_active,
        }

        if month:
            for k, v in data.items():
                setattr(month, k, v)
            month.save()
        else:
            Month.objects.create(**data)

        return redirect('/admin/months/')

    return render(request, 'panel/month_form.html', {'month': month, 'levels': levels})


@login_required(login_url='/admin/login/')
@staff_required
def month_delete(request, pk):
    month = get_object_or_404(Month, pk=pk)
    month.delete()
    return redirect('/admin/months/')
