from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Category, Question, ExamSession, Answer, AIUsage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'question_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']
    actions = ['activate_categories', 'deactivate_categories']

    def question_count(self, obj):
        count = obj.questions.count()
        url = reverse('admin:exams_question_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}" style="font-weight: bold; color: #417690;">{} questions</a>', url, count)
    question_count.short_description = 'Questions'

    @admin.action(description='Activate selected categories')
    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} categories activated.', messages.SUCCESS)

    @admin.action(description='Deactivate selected categories')
    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} categories deactivated.', messages.SUCCESS)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'question_type', 'question_preview', 'points', 'order', 'is_active', 'actions_column']
    list_filter = ['category', 'question_type', 'is_active', 'created_at']
    search_fields = ['question_text', 'instructions']
    list_editable = ['is_active', 'points', 'order']
    ordering = ['category', 'order', 'id']
    actions = ['activate_questions', 'deactivate_questions', 'duplicate_questions']
    save_as = True
    save_as_continue = True
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'question_type', 'question_text', 'instructions'),
            'classes': ('wide',)
        }),
        ('Answer Options', {
            'fields': ('options', 'correct_answer', 'correct_answer_index'),
            'description': 'For multiple choice/vocabulary: use options (JSON list) and correct_answer_index (0-based). For translation/writing: use correct_answer (text).',
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('points', 'min_words', 'order', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    def question_preview(self, obj):
        preview = obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
        color = '#417690' if obj.is_active else '#999'
        return format_html(
            '<span style="color: {};" title="{}">{}</span>',
            color, obj.question_text, preview
        )
    question_preview.short_description = 'Question'

    def actions_column(self, obj):
        edit_url = reverse('admin:exams_question_change', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px;">Edit</a>',
            edit_url
        )
    actions_column.short_description = 'Actions'

    @admin.action(description='Activate selected questions')
    def activate_questions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} questions activated.', messages.SUCCESS)

    @admin.action(description='Deactivate selected questions')
    def deactivate_questions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} questions deactivated.', messages.SUCCESS)

    @admin.action(description='Duplicate selected questions')
    def duplicate_questions(self, request, queryset):
        count = 0
        for question in queryset:
            question.pk = None
            question.question_text = f"{question.question_text} (Copy)"
            question.is_active = False
            question.save()
            count += 1
        self.message_user(request, f'{count} questions duplicated.', messages.SUCCESS)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'answer_text', 'answer_index', 'is_correct', 'points_earned', 'created_at']
    can_delete = False
    can_add = False

    def has_add_permission(self, request, obj=None):
        return False


class AIUsageInline(admin.TabularInline):
    model = AIUsage
    extra = 0
    readonly_fields = ['question', 'was_ai_used', 'confidence_score', 'detected_patterns', 'detected_at']
    can_delete = False
    can_add = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_display', 'started_at', 'completed_at', 'is_completed', 'score_display', 'ai_usage_count', 'view_details']
    list_filter = ['is_completed', 'started_at', 'completed_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['session_id', 'started_at', 'total_score', 'max_score']
    inlines = [AnswerInline, AIUsageInline]
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    actions = ['mark_completed', 'mark_incomplete']

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
            return format_html('<a href="{}" style="font-weight: bold;">{}</a>', url, obj.user.username)
        return format_html('<span style="color: #999;">Anonymous</span>')
    user_display.short_description = 'User'

    def score_display(self, obj):
        if obj.max_score > 0:
            percentage = (obj.total_score / obj.max_score) * 100
            if percentage >= 70:
                color = '#28a745'
            elif percentage >= 50:
                color = '#ffc107'
            else:
                color = '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold; font-size: 14px;">{:.1f} / {:.1f} ({:.1f}%)</span>',
                color, obj.total_score, obj.max_score, percentage
            )
        return '-'
    score_display.short_description = 'Score'

    def ai_usage_count(self, obj):
        count = obj.ai_usage.filter(was_ai_used=True).count()
        if count > 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold; background: #fff3cd; padding: 3px 8px; border-radius: 3px;">⚠️ {} sections</span>',
                count
            )
        return format_html('<span style="color: #28a745; font-weight: bold;">✓ No AI</span>')
    ai_usage_count.short_description = 'AI Usage'

    def view_details(self, obj):
        url = reverse('admin:exams_examsession_change', args=[obj.id])
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px;">View</a>',
            url
        )
    view_details.short_description = 'Details'

    @admin.action(description='Mark selected as completed')
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_completed=True, completed_at=timezone.now())
        self.message_user(request, f'{updated} sessions marked as completed.', messages.SUCCESS)

    @admin.action(description='Mark selected as incomplete')
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(is_completed=False, completed_at=None)
        self.message_user(request, f'{updated} sessions marked as incomplete.', messages.SUCCESS)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['exam_session', 'question', 'answer_preview', 'is_correct', 'points_earned', 'created_at']
    list_filter = ['is_correct', 'question__category', 'created_at']
    search_fields = ['answer_text', 'exam_session__session_id', 'question__question_text']
    readonly_fields = ['exam_session', 'question', 'created_at']
    ordering = ['-created_at']

    def answer_preview(self, obj):
        text = obj.answer_text or f"Option {obj.answer_index}"
        preview = text[:60] + '...' if len(text) > 60 else text
        return preview
    answer_preview.short_description = 'Answer'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ['exam_session', 'question', 'was_ai_used', 'confidence_display', 'detected_at']
    list_filter = ['was_ai_used', 'question__category', 'detected_at']
    search_fields = ['exam_session__session_id', 'question__question_text', 'text_snippet']
    readonly_fields = ['exam_session', 'question', 'detected_at', 'detected_patterns', 'text_snippet']
    ordering = ['-detected_at']

    def confidence_display(self, obj):
        if obj.was_ai_used:
            color = '#dc3545' if obj.confidence_score > 0.7 else '#ffc107'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
                color, obj.confidence_score
            )
        return format_html('<span style="color: #28a745;">No AI</span>')
    confidence_display.short_description = 'Confidence'

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
            return format_html('<a href="{}" style="font-weight: bold; color: #417690;">{} exams</a>', url, count)
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
