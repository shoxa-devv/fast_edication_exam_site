from django.db import models
from django.utils import timezone


class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Sayt logotipi")
    site_name = models.CharField(max_length=200, default='Fast Education')
    tagline = models.CharField(max_length=300, default='English Language Assessment Centre')
    certificate_bg = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Sertifikat fon rasmi")
    certificate_stamp = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Sertifikat muhri/shtampi")

    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ['first_name', 'last_name']
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def student_count(self):
        return self.students.count()


class Level(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default='#002147')
    icon = models.CharField(max_length=10, default='\U0001F4DA')
    image = models.ImageField(upload_to='levels/', blank=True, null=True, help_text="Daraja uchun rasm (admin paneldan o'zgartiring)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Daraja"
        verbose_name_plural = "Darajalar"

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        return self.questions.filter(is_active=True).count()


class Month(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='months')
    number = models.IntegerField()
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['level', 'number']
        ordering = ['level__order', 'number']
        verbose_name = "Oy"
        verbose_name_plural = "Oylar"

    def __str__(self):
        return f"{self.level.name} — {self.name}"

    @property
    def question_count(self):
        return self.questions.filter(is_active=True).count()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('translation', 'Translation'),
        ('writing', 'Writing'),
        ('vocabulary', 'Vocabulary'),
    ]

    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='questions')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='questions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    options = models.JSONField(default=list, blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    correct_answer_index = models.IntegerField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    min_words = models.IntegerField(default=0, help_text="Minimum words for writing questions")
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level__order', 'month__number', 'category__order', 'order', 'id']

    def __str__(self):
        return f"[{self.level.name}/{self.month.name}] {self.category.name}: {self.question_text[:60]}"


class VocabularyWord(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='vocabulary')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='vocabulary')
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=200, blank=True, help_text="O'zbek tilidagi tarjima")
    definition = models.TextField(blank=True)
    example_sentence = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level__order', 'month__number', 'order']
        verbose_name = "Vocabulary Word"
        verbose_name_plural = "Vocabulary Words"

    def __str__(self):
        return f"{self.word} — {self.level.name} / {self.month.name}"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ExamSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_sessions')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='exam_sessions')
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='exam_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    total_score = models.FloatField(default=0)
    max_score = models.FloatField(default=0)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Imtihon"
        verbose_name_plural = "Imtihonlar"

    def __str__(self):
        return f"{self.student.full_name} — {self.level.name} {self.month.name}"

    @property
    def percentage(self):
        if self.max_score > 0:
            return round((self.total_score / self.max_score) * 100, 1)
        return 0


class Answer(models.Model):
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    answer_index = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam_session', 'question']
        ordering = ['question__category__order', 'question__order']

    def __str__(self):
        return f"{self.exam_session.student.full_name} — Q{self.question.id}"
