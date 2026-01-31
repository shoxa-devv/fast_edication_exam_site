from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Exam categories: Grammar, Translation, Writing, Vocabulary"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """Questions for exams"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('translation', 'Translation'),
        ('writing', 'Writing'),
        ('vocabulary', 'Vocabulary'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    options = models.JSONField(default=list, blank=True, null=True)  # For multiple choice
    correct_answer = models.TextField(blank=True, null=True)  # Can be index or text
    correct_answer_index = models.IntegerField(null=True, blank=True)  # For multiple choice
    instructions = models.TextField(blank=True)
    min_words = models.IntegerField(default=0, help_text="Minimum words for writing questions")
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'id']

    def __str__(self):
        return f"{self.category.name} - {self.question_text[:50]}"


class ExamSession(models.Model):
    """User exam sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions', null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    total_score = models.FloatField(default=0)
    max_score = models.FloatField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Exam {self.session_id} - {self.user.username if self.user else 'Anonymous'}"


class Answer(models.Model):
    """User answers to questions"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    answer_index = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam_session', 'question']
        ordering = ['question__category', 'question__order']

    def __str__(self):
        return f"{self.exam_session.session_id} - {self.question}"


class AIUsage(models.Model):
    """Track AI usage in exam sessions"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='ai_usage')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    was_ai_used = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)
    detected_patterns = models.JSONField(default=list, blank=True)
    text_snippet = models.TextField(blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam_session', 'question']

    def __str__(self):
        return f"AI Usage - {self.exam_session.session_id} - Q{self.question.id}"
