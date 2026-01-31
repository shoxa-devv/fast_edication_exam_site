from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import uuid
from datetime import datetime
from .models import Category, Question, ExamSession, Answer, AIUsage
from .ai_detector import AdvancedAIDetector

ai_detector = AdvancedAIDetector()


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'django': 'running'
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_categories(request):
    """Get all active categories"""
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    data = [{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'order': cat.order
    } for cat in categories]
    return JsonResponse({'success': True, 'categories': data})


@csrf_exempt
@require_http_methods(["GET"])
def get_questions(request):
    """Get questions for a specific category"""
    category_slug = request.GET.get('category', '')
    
    try:
        if category_slug:
            category = Category.objects.get(slug=category_slug, is_active=True)
            questions = Question.objects.filter(category=category, is_active=True).order_by('order', 'id')
        else:
            questions = Question.objects.filter(is_active=True).order_by('category', 'order', 'id')
        
        data = []
        for q in questions:
            question_data = {
                'id': q.id,
                'category': q.category.slug,
                'question_type': q.question_type,
                'question_text': q.question_text,
                'instructions': q.instructions,
                'min_words': q.min_words,
                'points': q.points,
            }
            
            if q.question_type == 'multiple_choice' or q.question_type == 'vocabulary':
                question_data['options'] = q.options or []
                question_data['correct_answer_index'] = q.correct_answer_index
            
            data.append(question_data)
        
        return JsonResponse({
            'success': True,
            'category': category_slug,
            'questions': data
        })
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def detect_ai(request):
    """Detect AI usage in text"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        question_id = data.get('questionId')
        category = data.get('category', 'writing')
        
        if not text or len(text) < 50:
            return JsonResponse({
                'success': True,
                'ai_used': False,
                'confidence': 0.0,
                'detected_patterns': []
            })
        
        result = ai_detector.detect(text)
        
        return JsonResponse({
            'success': True,
            'ai_used': result['is_ai_used'],
            'confidence': result['confidence'],
            'detected_patterns': result['patterns'],
            'questionId': question_id,
            'category': category,
            'text_length': len(text)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def ai_assist(request):
    """Get AI assistance for writing"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        current_text = data.get('currentText', '')
        question_id = data.get('questionId')
        
        suggestions = [
            f"You might want to add more details about {topic}.",
            f"Consider explaining the benefits and importance of {topic}.",
            f"You could mention how {topic} relates to your personal experience.",
            f"Try to provide specific examples related to {topic}.",
        ]
        
        import random
        suggestion = random.choice(suggestions)
        
        return JsonResponse({
            'success': True,
            'suggestion': suggestion,
            'ai_used': True,
            'questionId': question_id,
            'message': 'AI assistance provided. This will be marked in your results.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def submit_exam(request):
    """Submit exam results"""
    try:
        data = json.loads(request.body)
        session_id = str(uuid.uuid4())
        
        # Create exam session
        exam_session = ExamSession.objects.create(
            session_id=session_id,
            is_completed=True,
            completed_at=timezone.now()
        )
        
        answers_data = data.get('answers', {})
        ai_usage_data = data.get('aiUsage', {})
        categories = data.get('categories', [])
        
        total_score = 0
        max_score = 0
        ai_usage_summary = {}
        
        # Process answers
        for key, answer_value in answers_data.items():
            try:
                category_slug, question_id = key.split('_', 1)
                question_id = int(question_id)
                
                question = Question.objects.get(id=question_id, is_active=True)
                max_score += question.points
                
                # Check if answer is correct
                is_correct = None
                points_earned = 0
                
                if question.question_type in ['multiple_choice', 'vocabulary']:
                    if answer_value == question.correct_answer_index:
                        is_correct = True
                        points_earned = question.points
                        total_score += question.points
                # For translation and writing, we don't auto-grade
                
                Answer.objects.create(
                    exam_session=exam_session,
                    question=question,
                    answer_text=str(answer_value) if not isinstance(answer_value, int) else '',
                    answer_index=answer_value if isinstance(answer_value, int) else None,
                    is_correct=is_correct,
                    points_earned=points_earned
                )
            except (ValueError, Question.DoesNotExist) as e:
                continue
        
        # Process AI usage
        for key, usage_info in ai_usage_data.items():
            try:
                category_slug, question_id = key.split('_', 1)
                question_id = int(question_id)
                
                question = Question.objects.get(id=question_id, is_active=True)
                was_ai_used = usage_info.get('used', False)
                text = usage_info.get('text', '')
                
                if was_ai_used and text:
                    # Detect AI again for confidence
                    result = ai_detector.detect(text)
                    
                    AIUsage.objects.create(
                        exam_session=exam_session,
                        question=question,
                        was_ai_used=True,
                        confidence_score=result['confidence'],
                        detected_patterns=result['patterns'],
                        text_snippet=text[:500]  # Store snippet
                    )
                    
                    ai_usage_summary[key] = {
                        'category': category_slug,
                        'questionId': question_id,
                        'used': True,
                        'text': text[:200],
                        'confidence': result['confidence']
                    }
            except (ValueError, Question.DoesNotExist):
                continue
        
        exam_session.total_score = total_score
        exam_session.max_score = max_score
        exam_session.save()
        
        return JsonResponse({
            'success': True,
            'examId': session_id,
            'aiUsageSummary': ai_usage_summary,
            'totalAiUsed': len(ai_usage_summary),
            'score': {
                'total': total_score,
                'max': max_score,
                'percentage': round((total_score / max_score * 100) if max_score > 0 else 0, 2)
            },
            'message': 'Exam submitted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_exam_results(request, exam_id):
    """Get exam results by ID"""
    try:
        exam_session = ExamSession.objects.get(session_id=exam_id)
        
        answers = {}
        for answer in exam_session.answers.all():
            key = f"{answer.question.category.slug}_{answer.question.id}"
            answers[key] = {
                'answer_text': answer.answer_text,
                'answer_index': answer.answer_index,
                'is_correct': answer.is_correct,
                'points_earned': answer.points_earned
            }
        
        ai_usage = {}
        for ai in exam_session.ai_usage.filter(was_ai_used=True):
            key = f"{ai.question.category.slug}_{ai.question.id}"
            ai_usage[key] = {
                'used': True,
                'confidence': ai.confidence_score,
                'patterns': ai.detected_patterns,
                'text': ai.text_snippet
            }
        
        return JsonResponse({
            'success': True,
            'results': {
                'examId': exam_session.session_id,
                'startedAt': exam_session.started_at.isoformat(),
                'completedAt': exam_session.completed_at.isoformat() if exam_session.completed_at else None,
                'score': {
                    'total': exam_session.total_score,
                    'max': exam_session.max_score
                },
                'answers': answers,
                'aiUsage': ai_usage
            }
        })
    except ExamSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Exam not found'
        }, status=404)
