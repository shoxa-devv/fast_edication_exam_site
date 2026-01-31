from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Question, ExamSession, Answer, AIUsage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'question_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    def question_count(self, obj):
        count = obj.questions.count()
        url = reverse('admin:exams_question_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} questions</a>', url, count)
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'question_type', 'question_preview', 'points', 'is_active', 'created_at']
    list_filter = ['category', 'question_type', 'is_active', 'created_at']
    search_fields = ['question_text', 'instructions']
    list_editable = ['is_active', 'points']
    ordering = ['category', 'order', 'id']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'question_type', 'question_text', 'instructions')
        }),
        ('Answer Options', {
            'fields': ('options', 'correct_answer', 'correct_answer_index'),
            'description': 'For multiple choice: use options (list) and correct_answer_index. For others: use correct_answer (text).'
        }),
        ('Settings', {
            'fields': ('points', 'min_words', 'order', 'is_active')
        }),
    )

    def question_preview(self, obj):
        preview = obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
        return format_html('<span title="{}">{}</span>', obj.question_text, preview)
    question_preview.short_description = 'Question'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'answer_text', 'answer_index', 'is_correct', 'points_earned', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class AIUsageInline(admin.TabularInline):
    model = AIUsage
    extra = 0
    readonly_fields = ['question', 'was_ai_used', 'confidence_score', 'detected_patterns', 'detected_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_display', 'started_at', 'completed_at', 'is_completed', 'score_display', 'ai_usage_count']
    list_filter = ['is_completed', 'started_at', 'completed_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['session_id', 'started_at', 'total_score', 'max_score']
    inlines = [AnswerInline, AIUsageInline]
    date_hierarchy = 'started_at'
    ordering = ['-started_at']

    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'user', 'started_at', 'completed_at', 'is_completed')
        }),
        ('Scores', {
            'fields': ('total_score', 'max_score')
        }),
    )

    def user_display(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return 'Anonymous'
    user_display.short_description = 'User'

    def score_display(self, obj):
        if obj.max_score > 0:
            percentage = (obj.total_score / obj.max_score) * 100
            color = 'green' if percentage >= 70 else 'orange' if percentage >= 50 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f} / {:.1f} ({:.1f}%)</span>',
                color, obj.total_score, obj.max_score, percentage
            )
        return '-'
    score_display.short_description = 'Score'

    def ai_usage_count(self, obj):
        count = obj.ai_usage.filter(was_ai_used=True).count()
        if count > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ {} sections</span>',
                count
            )
        return format_html('<span style="color: green;">✓ No AI</span>')
    ai_usage_count.short_description = 'AI Usage'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['exam_session', 'question', 'answer_preview', 'is_correct', 'points_earned', 'created_at']
    list_filter = ['is_correct', 'question__category', 'created_at']
    search_fields = ['answer_text', 'exam_session__session_id', 'question__question_text']
    readonly_fields = ['exam_session', 'question', 'created_at']
    ordering = ['-created_at']

    def answer_preview(self, obj):
        text = obj.answer_text or f"Option {obj.answer_index}"
        preview = text[:50] + '...' if len(text) > 50 else text
        return preview
    answer_preview.short_description = 'Answer'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ['exam_session', 'question', 'was_ai_used', 'confidence_score', 'detected_at']
    list_filter = ['was_ai_used', 'question__category', 'detected_at']
    search_fields = ['exam_session__session_id', 'question__question_text', 'text_snippet']
    readonly_fields = ['exam_session', 'question', 'detected_at', 'detected_patterns']
    ordering = ['-detected_at']

    def has_add_permission(self, request, obj=None):
        return False


# Customize User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'exam_count', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']

    def exam_count(self, obj):
        count = obj.exam_sessions.count()
        if count > 0:
            url = reverse('admin:exams_examsession_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} exams</a>', url, count)
        return '0'
    exam_count.short_description = 'Exams'

    def get_inlines(self, request, obj):
        if obj:
            return []
        return []


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site
admin.site.site_header = "Fast Education Admin Panel"
admin.site.site_title = "Fast Education Admin"
admin.site.index_title = "Welcome to Fast Education Administration"
