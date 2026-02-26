from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import json
import uuid
import re
import math
from .models import (
    SiteSettings, Teacher, Level, Month, Category, Question,
    VocabularyWord, Student, ExamSession, Answer
)


AI_PHRASES = [
    'it is important to note', 'it is worth noting', 'in conclusion',
    'furthermore', 'moreover', 'additionally', 'in today\'s world',
    'in today\'s society', 'plays a crucial role', 'plays a vital role',
    'it is essential to', 'on the other hand', 'in summary',
    'as a result', 'consequently', 'nevertheless', 'nonetheless',
    'in light of', 'with regard to', 'in terms of',
    'it can be argued', 'one could argue', 'it goes without saying',
    'last but not least', 'to sum up', 'all in all',
    'taking everything into consideration', 'from my perspective',
    'in my opinion', 'first and foremost', 'significantly',
    'fundamentally', 'transforming how', 'rapidly shaping',
    'undeniably', 'indispensable', 'paramount', 'multifaceted',
    'delve into', 'tapestry', 'landscape of',
    'navigating the', 'ever-evolving', 'harness the power',
    'pave the way', 'shed light on', 'foster a sense of',
    'a testament to', 'serves as a', 'it is imperative',
    'encompasses a wide range', 'strikes a balance',
    'holistic approach', 'nuanced understanding',
    'artificial intelligence is rapidly', 'the future of humanity',
    'from healthcare to education', 'transforming how people',
    'intelligent machines', 'reshaping the way',
    'revolutionizing', 'pivotal role', 'profound impact',
]

AI_PHRASES_UZ = [
    'shuni ta\'kidlash kerak', 'bugungi kunda', 'xulosa qilib aytganda',
    'bundan tashqari', 'shuningdek', 'qo\'shimcha ravishda',
    'zamonaviy dunyoda', 'muhim rol o\'ynaydi', 'hal qiluvchi ahamiyatga ega',
    'boshqa tomondan', 'natijada', 'shunga qaramay',
    'fikrimcha', 'eng avvalo', 'sezilarli darajada',
    'o\'z navbatida', 'shubhasiz', 'ta\'kidlash joiz',
    'yakunlab aytganda', 'umuman olganda',
]


def detect_ai_text(text):
    if not text or len(text.strip()) < 30:
        return {'is_ai': False, 'score': 0, 'reasons': []}

    text_lower = text.lower().strip()
    words = text_lower.split()
    word_count = len(words)
    if word_count < 10:
        return {'is_ai': False, 'score': 0, 'reasons': []}

    score = 0
    reasons = []

    # 1. Check AI-typical phrases (EN + UZ)
    phrase_hits = 0
    for phrase in AI_PHRASES + AI_PHRASES_UZ:
        if phrase in text_lower:
            phrase_hits += 1
    if phrase_hits >= 3:
        score += 35
        reasons.append(f'{phrase_hits} ta AI-tipik ibora topildi')
    elif phrase_hits >= 2:
        score += 20
        reasons.append(f'{phrase_hits} ta AI-tipik ibora topildi')
    elif phrase_hits >= 1:
        score += 8

    # 2. Sentence uniformity (AI writes very uniform sentence lengths)
    sentences = re.split(r'[.!?]+', text_lower)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if len(sentences) >= 3:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        cv = std_dev / avg_len if avg_len > 0 else 0
        if cv < 0.25 and avg_len > 8:
            score += 20
            reasons.append('Gaplar uzunligi juda bir xil (AI belgisi)')
        elif cv < 0.35 and avg_len > 10:
            score += 10

    # 3. Excessive transition words
    transitions = ['however', 'moreover', 'furthermore', 'additionally',
                   'consequently', 'nevertheless', 'therefore', 'thus',
                   'hence', 'meanwhile', 'subsequently', 'accordingly',
                   'biroq', 'shuningdek', 'bundan tashqari', 'natijada',
                   'shuning uchun', 'demak', 'binobarin']
    trans_count = sum(1 for t in transitions if t in text_lower)
    trans_ratio = trans_count / max(len(sentences), 1)
    if trans_ratio > 0.5 and trans_count >= 3:
        score += 15
        reasons.append(f"{trans_count} ta bog'lovchi so'z (ko'p)")
    elif trans_ratio > 0.3 and trans_count >= 2:
        score += 8

    # 4. Paragraph structure too perfect (similar paragraph lengths)
    paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 20]
    if len(paragraphs) >= 3:
        p_lens = [len(p.split()) for p in paragraphs]
        p_avg = sum(p_lens) / len(p_lens)
        p_var = sum((l - p_avg) ** 2 for l in p_lens) / len(p_lens)
        p_cv = math.sqrt(p_var) / p_avg if p_avg > 0 else 0
        if p_cv < 0.2:
            score += 15
            reasons.append('Paragraflar uzunligi juda bir xil')

    # 5. High vocabulary diversity with long words (AI uses complex vocab)
    unique_words = set(re.findall(r'[a-zA-Z]+', text_lower))
    long_words = [w for w in unique_words if len(w) > 10]
    if len(long_words) > word_count * 0.08 and word_count > 30:
        score += 12
        reasons.append(f"{len(long_words)} ta murakkab so'z ishlatilgan")

    # 6. Too few spelling/grammar mistakes (humans make errors)
    if word_count > 50:
        contractions = text.count("'") + text.count("'")
        casual_markers = sum(1 for w in words if w in ['ok', 'yeah', 'gonna', 'wanna', 'kinda', 'ya', 'lol', 'btw'])
        if contractions == 0 and casual_markers == 0:
            score += 8

    # 7. Numbered/lettered list patterns (AI loves lists)
    list_patterns = len(re.findall(r'(?:^|\n)\s*(?:\d+[\.\)]\s|[a-z][\.\)]\s|[-•]\s)', text))
    if list_patterns >= 3 and word_count > 40:
        score += 10
        reasons.append(f"{list_patterns} ta ro'yxat element topildi")

    score = min(score, 100)
    is_ai = score >= 40

    return {
        'is_ai': is_ai,
        'score': score,
        'reasons': reasons,
        'label': 'AI yozgan' if score >= 70 else 'AI ishlatilgan bo\'lishi mumkin' if score >= 40 else 'Inson yozgan',
    }


@csrf_exempt
@require_http_methods(["POST"])
def register_student(request):
    try:
        data = json.loads(request.body)
        first = data.get('first_name', '').strip()
        last = data.get('last_name', '').strip()
        t_first = data.get('teacher_first_name', '').strip()
        t_last = data.get('teacher_last_name', '').strip()

        if not all([first, last, t_first, t_last]):
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)

        teacher, _ = Teacher.objects.get_or_create(
            first_name=t_first, last_name=t_last,
            defaults={'is_active': True}
        )
        student = Student.objects.create(
            first_name=first, last_name=last, teacher=teacher
        )
        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'student_name': student.full_name,
            'teacher_name': teacher.full_name,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_levels(request):
    levels = Level.objects.filter(is_active=True)
    data = [{
        'id': lv.id,
        'name': lv.name,
        'slug': lv.slug,
        'description': lv.description,
        'color': lv.color,
        'icon': lv.icon,
        'order': lv.order,
        'image_url': lv.image.url if lv.image else None,
        'month_count': lv.months.filter(is_active=True).count(),
    } for lv in levels]
    return JsonResponse({'success': True, 'levels': data})


@csrf_exempt
@require_http_methods(["GET"])
def get_months(request, level_slug):
    try:
        level = Level.objects.get(slug=level_slug, is_active=True)
        months = level.months.filter(is_active=True).order_by('number')
        data = [{
            'id': m.id,
            'number': m.number,
            'name': m.name,
            'question_count': Question.objects.filter(
                level=level, month=m, is_active=True
            ).count(),
            'vocab_count': VocabularyWord.objects.filter(
                level=level, month=m, is_active=True
            ).count(),
        } for m in months]
        return JsonResponse({
            'success': True,
            'level': {
                'id': level.id, 'name': level.name,
                'slug': level.slug, 'color': level.color, 'icon': level.icon,
            },
            'months': data,
        })
    except Level.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Level not found'}, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def get_questions(request, level_slug, month_number):
    try:
        level = Level.objects.get(slug=level_slug, is_active=True)
        month = Month.objects.get(level=level, number=month_number, is_active=True)

        questions = Question.objects.filter(
            level=level, month=month, is_active=True
        ).select_related('category').order_by('category__order', 'order')

        cats = []
        seen = set()
        for q in questions:
            if q.category.slug not in seen:
                seen.add(q.category.slug)
                cats.append({
                    'id': q.category.id,
                    'name': q.category.name,
                    'slug': q.category.slug,
                })

        questions_data = []
        for q in questions:
            qd = {
                'id': q.id,
                'category': q.category.slug,
                'category_name': q.category.name,
                'question_type': q.question_type,
                'question_text': q.question_text,
                'instructions': q.instructions,
                'min_words': q.min_words,
                'points': q.points,
            }
            if q.question_type in ('multiple_choice', 'vocabulary'):
                qd['options'] = q.options or []
                qd['correct_answer_index'] = q.correct_answer_index
            questions_data.append(qd)

        return JsonResponse({
            'success': True,
            'level': {'name': level.name, 'slug': level.slug, 'color': level.color},
            'month': {'number': month.number, 'name': month.name},
            'categories': cats,
            'questions': questions_data,
        })
    except (Level.DoesNotExist, Month.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def get_vocabulary(request, level_slug, month_number):
    try:
        level = Level.objects.get(slug=level_slug, is_active=True)
        month = Month.objects.get(level=level, number=month_number, is_active=True)
        vocab = VocabularyWord.objects.filter(
            level=level, month=month, is_active=True
        ).order_by('order')
        data = [{
            'id': v.id,
            'word': v.word,
            'translation': v.translation,
            'definition': v.definition,
            'example': v.example_sentence,
        } for v in vocab]
        return JsonResponse({'success': True, 'vocabulary': data})
    except (Level.DoesNotExist, Month.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def check_ai(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        result = detect_ai_text(text)
        return JsonResponse({'success': True, **result})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def submit_exam(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        level_slug = data.get('level_slug')
        month_number = data.get('month_number')
        answers_data = data.get('answers', {})

        student = Student.objects.get(id=student_id)
        level = Level.objects.get(slug=level_slug)
        month = Month.objects.get(level=level, number=month_number)

        session_id = str(uuid.uuid4())
        exam = ExamSession.objects.create(
            student=student,
            level=level,
            month=month,
            session_id=session_id,
            is_completed=True,
            completed_at=timezone.now(),
        )

        total_score = 0
        max_score = 0

        for key, answer_value in answers_data.items():
            try:
                question_id = int(key)
                question = Question.objects.get(id=question_id, is_active=True)
                max_score += question.points

                is_correct = None
                points_earned = 0

                if question.question_type in ['multiple_choice', 'vocabulary']:
                    if (question.correct_answer_index is not None
                            and answer_value == question.correct_answer_index):
                        is_correct = True
                        points_earned = question.points
                        total_score += question.points
                    else:
                        is_correct = False

                ai_result = None
                if question.question_type in ['writing', 'translation'] and isinstance(answer_value, str):
                    ai_result = detect_ai_text(answer_value)

                Answer.objects.create(
                    exam_session=exam,
                    question=question,
                    answer_text=str(answer_value) if not isinstance(answer_value, int) else '',
                    answer_index=answer_value if isinstance(answer_value, int) else None,
                    is_correct=is_correct,
                    points_earned=points_earned,
                )
            except (ValueError, Question.DoesNotExist):
                continue

        exam.total_score = total_score
        exam.max_score = max_score
        exam.save()

        review = []
        for ans in exam.answers.select_related(
            'question', 'question__category'
        ).order_by('question__category__order', 'question__order'):
            q = ans.question
            item = {
                'questionId': q.id,
                'category': q.category.slug,
                'categoryName': q.category.name,
                'questionType': q.question_type,
                'questionText': q.question_text,
                'isCorrect': ans.is_correct,
            }
            if q.question_type in ('multiple_choice', 'vocabulary'):
                item['options'] = q.options or []
                item['correctIndex'] = q.correct_answer_index
                ci = q.correct_answer_index
                item['correctAnswer'] = (
                    q.options[ci]
                    if q.options and ci is not None and ci < len(q.options)
                    else ''
                )
                ai_idx = ans.answer_index
                item['yourAnswer'] = (
                    q.options[ai_idx]
                    if ai_idx is not None and q.options and ai_idx < len(q.options)
                    else 'No answer'
                )
                item['yourIndex'] = ai_idx
            else:
                item['yourAnswer'] = ans.answer_text or 'No answer'
                if q.question_type in ('writing', 'translation') and ans.answer_text:
                    item['aiCheck'] = detect_ai_text(ans.answer_text)
            review.append(item)

        correct_count = exam.answers.filter(is_correct=True).count()
        total_gradable = exam.answers.filter(
            question__question_type__in=['multiple_choice', 'vocabulary']
        ).count()

        return JsonResponse({
            'success': True,
            'examId': session_id,
            'score': {
                'correct': correct_count,
                'total': total_gradable,
                'points': total_score,
                'maxPoints': max_score,
                'percentage': round(
                    (correct_count / total_gradable * 100) if total_gradable > 0 else 0, 1
                ),
            },
            'review': review,
            'session_id': session_id,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def certificate_view(request, session_id):
    exam = get_object_or_404(ExamSession, session_id=session_id, is_completed=True)
    answers = exam.answers.select_related('question', 'question__category').order_by(
        'question__category__order', 'question__order'
    )

    categories_data = {}
    for ans in answers:
        cat = ans.question.category.name
        if cat not in categories_data:
            categories_data[cat] = {'correct': 0, 'total': 0, 'slug': ans.question.category.slug}
        if ans.question.question_type in ('multiple_choice', 'vocabulary'):
            categories_data[cat]['total'] += 1
            if ans.is_correct:
                categories_data[cat]['correct'] += 1

    settings_obj = SiteSettings.load()
    logo_url = settings_obj.logo.url if settings_obj.logo else '/static/images/logo.png'
    stamp_url = settings_obj.certificate_stamp.url if settings_obj.certificate_stamp else None

    pct = exam.percentage
    if pct >= 90:
        band_score = 9.0
    elif pct >= 80:
        band_score = 8.0
    elif pct >= 70:
        band_score = 7.0
    elif pct >= 60:
        band_score = 6.0
    elif pct >= 50:
        band_score = 5.0
    elif pct >= 40:
        band_score = 4.0
    elif pct >= 25:
        band_score = 3.0
    else:
        band_score = 2.0

    level_label = 'Beginner'
    if band_score >= 8:
        level_label = 'Expert'
    elif band_score >= 7:
        level_label = 'Advanced'
    elif band_score >= 6:
        level_label = 'Upper-Intermediate'
    elif band_score >= 5:
        level_label = 'Intermediate'
    elif band_score >= 4:
        level_label = 'Pre-Intermediate'
    elif band_score >= 3:
        level_label = 'Elementary'

    return render(request, 'certificate.html', {
        'exam': exam,
        'student': exam.student,
        'level': exam.level,
        'month': exam.month,
        'categories': categories_data,
        'percentage': pct,
        'band_score': band_score,
        'level_label': level_label,
        'logo_url': logo_url,
        'stamp_url': stamp_url,
        'answers': answers,
    })
