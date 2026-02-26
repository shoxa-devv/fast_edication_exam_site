from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    SiteSettings, Teacher, Level, Month, Category, Question,
    VocabularyWord, Student, ExamSession, Answer
)


# ─── Site Settings (singleton) ───
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Sayt ma\'lumotlari', {
            'fields': ('site_name', 'tagline'),
        }),
        ('Rasmlar', {
            'fields': ('logo', 'logo_preview', 'certificate_bg', 'cert_bg_preview', 'certificate_stamp', 'cert_stamp_preview'),
            'description': 'Sayt logotipi va sertifikat rasmlarini yuklang.',
        }),
    )
    readonly_fields = ['logo_preview', 'cert_bg_preview', 'cert_stamp_preview']

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-width:120px;max-height:80px;border-radius:8px;border:1px solid #ddd;margin-top:4px">', obj.logo.url)
        return 'Rasm yuklanmagan'
    logo_preview.short_description = 'Logo ko\'rinishi'

    def cert_bg_preview(self, obj):
        if obj.certificate_bg:
            return format_html('<img src="{}" style="max-width:200px;max-height:120px;border-radius:8px;border:1px solid #ddd;margin-top:4px">', obj.certificate_bg.url)
        return 'Rasm yuklanmagan'
    cert_bg_preview.short_description = 'Sertifikat foni'

    def cert_stamp_preview(self, obj):
        if obj.certificate_stamp:
            return format_html('<img src="{}" style="max-width:100px;max-height:100px;border-radius:8px;border:1px solid #ddd;margin-top:4px">', obj.certificate_stamp.url)
        return 'Rasm yuklanmagan'
    cert_stamp_preview.short_description = 'Muhr ko\'rinishi'

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ─── Teacher ───
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'student_count_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['first_name', 'last_name']
    list_editable = ['is_active']

    def student_count_display(self, obj):
        count = obj.students.count()
        if count > 0:
            url = reverse('admin:exams_student_changelist') + f'?teacher__id__exact={obj.id}'
            return format_html('<a href="{}" style="font-weight:bold;color:#002147">{} ta talaba</a>', url, count)
        return '0'
    student_count_display.short_description = "Talabalar soni"


# ─── Level ───
@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'slug', 'order', 'image_preview', 'color_preview', 'question_count_display', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'order'),
        }),
        ('Ko\'rinish', {
            'fields': ('icon', 'color', 'image'),
            'description': 'Daraja uchun rasm yuklang. Rasm saytda daraja kartochkasida ko\'rsatiladi.',
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:35px;object-fit:cover;border-radius:4px;border:1px solid #ddd">',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Rasm'

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;border-radius:4px;background:{};border:1px solid #ddd"></span> {}',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'

    def question_count_display(self, obj):
        count = obj.questions.filter(is_active=True).count()
        url = reverse('admin:exams_question_changelist') + f'?level__id__exact={obj.id}'
        return format_html('<a href="{}">{} ta savol</a>', url, count)
    question_count_display.short_description = 'Savollar'


# ─── Month ───
@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'level', 'number', 'question_count_display', 'is_active']
    list_filter = ['level', 'is_active']
    list_editable = ['is_active']

    def question_count_display(self, obj):
        count = obj.questions.filter(is_active=True).count()
        return f'{count} ta savol'
    question_count_display.short_description = 'Savollar'


# ─── Category ───
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


# ─── Question ───
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'level', 'month', 'category', 'question_type', 'question_preview', 'points', 'order', 'is_active']
    list_filter = ['level', 'month__number', 'category', 'question_type', 'is_active']
    search_fields = ['question_text', 'instructions']
    list_editable = ['is_active', 'points', 'order']
    save_as = True
    ordering = ['level__order', 'month__number', 'category__order', 'order']

    fieldsets = (
        ('Daraja va Oy', {
            'fields': ('level', 'month'),
        }),
        ('Savol ma\'lumotlari', {
            'fields': ('category', 'question_type', 'question_text', 'instructions'),
            'classes': ('wide',),
        }),
        ('Javob variantlari', {
            'fields': ('options', 'correct_answer', 'correct_answer_index'),
            'description': 'Multiple choice/vocabulary: options (JSON list) va correct_answer_index (0 dan boshlab). Translation/writing: correct_answer (matn).',
            'classes': ('wide',),
        }),
        ('Sozlamalar', {
            'fields': ('points', 'min_words', 'order', 'is_active'),
        }),
    )

    def question_preview(self, obj):
        text = obj.question_text[:80]
        if len(obj.question_text) > 80:
            text += '...'
        return text
    question_preview.short_description = 'Savol'


# ─── Vocabulary Word ───
@admin.register(VocabularyWord)
class VocabularyWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'level', 'month', 'order', 'is_active']
    list_filter = ['level', 'month__number', 'is_active']
    search_fields = ['word', 'translation', 'definition']
    list_editable = ['order', 'is_active']
    ordering = ['level__order', 'month__number', 'order']

    fieldsets = (
        ('Daraja va Oy', {
            'fields': ('level', 'month'),
        }),
        ("So'z ma'lumotlari", {
            'fields': ('word', 'translation', 'definition', 'example_sentence'),
            'classes': ('wide',),
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active'),
        }),
    )


# ─── Student ───
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'teacher_display', 'exam_count', 'created_at']
    list_filter = ['teacher', 'created_at']
    search_fields = ['first_name', 'last_name', 'teacher__first_name', 'teacher__last_name']

    def teacher_display(self, obj):
        url = reverse('admin:exams_teacher_change', args=[obj.teacher.id])
        return format_html('<a href="{}" style="font-weight:bold">{}</a>', url, obj.teacher.full_name)
    teacher_display.short_description = "O'qituvchi"

    def exam_count(self, obj):
        count = obj.exam_sessions.count()
        if count > 0:
            url = reverse('admin:exams_examsession_changelist') + f'?student__id__exact={obj.id}'
            return format_html('<a href="{}">{} ta imtihon</a>', url, count)
        return '0'
    exam_count.short_description = 'Imtihonlar'


# ─── ExamSession with detailed answers ───
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question_display', 'category_display', 'answer_display', 'result_display', 'points_earned']
    fields = ['category_display', 'question_display', 'answer_display', 'result_display', 'points_earned']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def category_display(self, obj):
        return obj.question.category.name
    category_display.short_description = 'Bo\'lim'

    def question_display(self, obj):
        q = obj.question
        text = q.question_text[:100]
        qtype_colors = {
            'multiple_choice': '#6366F1',
            'vocabulary': '#14B8A6',
            'translation': '#F59E0B',
            'writing': '#EC407A',
        }
        color = qtype_colors.get(q.question_type, '#64748B')
        badge = format_html(
            '<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;color:#fff;background:{};margin-right:6px">{}</span>',
            color, q.get_question_type_display()
        )
        return format_html('{}{}', badge, text)
    question_display.short_description = 'Savol'

    def answer_display(self, obj):
        q = obj.question
        if q.question_type in ('multiple_choice', 'vocabulary'):
            if obj.answer_index is not None and q.options and obj.answer_index < len(q.options):
                ans = q.options[obj.answer_index]
            else:
                ans = 'Javob berilmadi'
            correct = ''
            if not obj.is_correct and q.correct_answer_index is not None and q.options:
                ci = q.correct_answer_index
                if ci < len(q.options):
                    correct = format_html(' <span style="color:#059669;font-weight:600">✓ {}</span>', q.options[ci])
            color = '#059669' if obj.is_correct else '#DC2626'
            return format_html('<span style="color:{}">{}</span>{}', color, ans, correct)
        else:
            text = obj.answer_text or 'Javob berilmadi'
            preview = text[:150]
            if len(text) > 150:
                preview += '...'
            return format_html('<span style="color:#334155">{}</span>', preview)
    answer_display.short_description = 'Javob'

    def result_display(self, obj):
        if obj.is_correct is True:
            return format_html('<span style="color:#059669;font-weight:700;font-size:16px">✓</span>')
        elif obj.is_correct is False:
            return format_html('<span style="color:#DC2626;font-weight:700;font-size:16px">✗</span>')
        return format_html('<span style="color:#94A3B8">—</span>')
    result_display.short_description = 'Natija'


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher_display', 'level', 'month', 'is_completed', 'score_display', 'percentage_bar', 'cert_link', 'started_at']
    list_filter = ['level', 'month__number', 'is_completed', 'started_at']
    search_fields = ['student__first_name', 'student__last_name', 'session_id']
    readonly_fields = ['session_id', 'started_at', 'total_score', 'max_score', 'certificate_preview']
    inlines = [AnswerInline]
    date_hierarchy = 'started_at'

    fieldsets = (
        ('Imtihon ma\'lumotlari', {
            'fields': ('student', 'level', 'month', 'session_id'),
        }),
        ('Natija', {
            'fields': ('is_completed', 'total_score', 'max_score', 'started_at', 'completed_at'),
        }),
        ('Sertifikat', {
            'fields': ('certificate_preview',),
            'description': 'Talabaning imtihon sertifikatini ko\'rish va chop etish',
        }),
    )

    def teacher_display(self, obj):
        return obj.student.teacher.full_name
    teacher_display.short_description = "O'qituvchi"

    def score_display(self, obj):
        if obj.max_score > 0:
            pct = obj.percentage
            color = '#059669' if pct >= 70 else '#D97706' if pct >= 50 else '#DC2626'
            score_text = f'{obj.total_score:.0f}/{obj.max_score:.0f} ({pct:.1f}%)'
            return format_html(
                '<span style="color:{};font-weight:bold">{}</span>',
                color, score_text
            )
        return '-'
    score_display.short_description = 'Ball'

    def percentage_bar(self, obj):
        if obj.max_score > 0:
            pct = obj.percentage
            color = '#059669' if pct >= 70 else '#D97706' if pct >= 50 else '#DC2626'
            return format_html(
                '<div style="width:100px;height:8px;background:#E2E8F0;border-radius:4px;overflow:hidden">'
                '<div style="width:{}%;height:100%;background:{};border-radius:4px"></div></div>',
                min(pct, 100), color
            )
        return '-'
    percentage_bar.short_description = 'Foiz'

    def cert_link(self, obj):
        if obj.is_completed:
            url = reverse('certificate', args=[obj.session_id])
            return format_html(
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;'
                'padding:4px 12px;background:#0F172A;color:#fff;border-radius:6px;font-size:11px;'
                'font-weight:700;text-decoration:none;letter-spacing:.3px">'
                '📄 Sertifikat</a>', url
            )
        return '-'
    cert_link.short_description = 'Sertifikat'

    def certificate_preview(self, obj):
        if obj.is_completed:
            url = reverse('certificate', args=[obj.session_id])
            return format_html(
                '<div style="margin:8px 0">'
                '<a href="{}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;'
                'padding:12px 24px;background:#0F172A;color:#fff;border-radius:10px;font-size:14px;'
                'font-weight:700;text-decoration:none;letter-spacing:.3px">'
                '📄 Sertifikatni ochish va chop etish</a>'
                '</div>', url
            )
        return 'Imtihon tugallanmagan'
    certificate_preview.short_description = 'Sertifikat'


# ─── Answer ───
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['exam_session', 'question_short', 'answer_preview', 'is_correct', 'points_earned']
    list_filter = ['is_correct', 'question__category', 'exam_session__level']
    search_fields = ['exam_session__student__first_name', 'question__question_text']
    readonly_fields = ['exam_session', 'question', 'created_at']

    def question_short(self, obj):
        return obj.question.question_text[:60]
    question_short.short_description = 'Savol'

    def answer_preview(self, obj):
        if obj.answer_index is not None:
            q = obj.question
            if q.options and obj.answer_index < len(q.options):
                return q.options[obj.answer_index]
        text = obj.answer_text or ''
        return text[:80] + ('...' if len(text) > 80 else '')
    answer_preview.short_description = 'Javob'

    def has_add_permission(self, request, obj=None):
        return False


# ─── Admin site customization ───
admin.site.site_header = "Fast Education — Admin Panel"
admin.site.site_title = "Fast Education Admin"
admin.site.index_title = "Boshqaruv paneli"
