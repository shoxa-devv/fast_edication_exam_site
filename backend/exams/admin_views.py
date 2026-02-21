"""Custom admin panel views — fully built from scratch."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from .models import Category, Question, ExamSession, Answer, AIUsage
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
        error = 'Invalid credentials or not an admin.'
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
        'total_users': User.objects.count(),
        'recent_exams': ExamSession.objects.order_by('-started_at')[:10],
        'ai_flagged': ExamSession.objects.filter(ai_usage__was_ai_used=True).distinct().count(),
    }
    return render(request, 'panel/dashboard.html', ctx)


@login_required(login_url='/admin/login/')
@staff_required
def questions_list(request):
    cat_filter = request.GET.get('category', '')
    qs = Question.objects.select_related('category').order_by('category__order', 'order', 'id')
    if cat_filter:
        qs = qs.filter(category__slug=cat_filter)
    categories = Category.objects.order_by('order')
    return render(request, 'panel/questions.html', {
        'questions': qs, 'categories': categories, 'current_cat': cat_filter
    })


@login_required(login_url='/admin/login/')
@staff_required
def question_edit(request, pk=None):
    question = get_object_or_404(Question, pk=pk) if pk else None
    categories = Category.objects.order_by('order')

    if request.method == 'POST':
        cat_id = request.POST.get('category')
        q_type = request.POST.get('question_type')
        q_text = request.POST.get('question_text', '')
        instructions = request.POST.get('instructions', '')
        correct_idx = request.POST.get('correct_answer_index')
        points = request.POST.get('points', 1)
        min_words = request.POST.get('min_words', 0)
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'

        # Build options from form
        options = []
        for i in range(6):
            opt = request.POST.get(f'option_{i}', '').strip()
            if opt:
                options.append(opt)

        data = {
            'category_id': cat_id,
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
        'question': question, 'categories': categories
    })


@login_required(login_url='/admin/login/')
@staff_required
def question_delete(request, pk):
    q = get_object_or_404(Question, pk=pk)
    q.delete()
    return redirect('/panel/questions/')


@login_required(login_url='/admin/login/')
@staff_required
def exams_list(request):
    exams = ExamSession.objects.order_by('-started_at')
    return render(request, 'panel/exams.html', {'exams': exams})


@login_required(login_url='/admin/login/')
@staff_required
def exam_detail(request, pk):
    exam = get_object_or_404(ExamSession, pk=pk)
    answers = exam.answers.select_related('question', 'question__category').order_by('question__category__order', 'question__order')
    ai = exam.ai_usage.filter(was_ai_used=True)
    return render(request, 'panel/exam_detail.html', {'exam': exam, 'answers': answers, 'ai_usage': ai})


@login_required(login_url='/admin/login/')
@staff_required
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    user_data = []
    for u in users:
        exam_count = ExamSession.objects.filter(user=u).count()
        user_data.append({'user': u, 'exam_count': exam_count})
    return render(request, 'panel/users.html', {'users': user_data})


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
