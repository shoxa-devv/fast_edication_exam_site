from django.core.management.base import BaseCommand
from exams.models import Category, Question


def load_data():
    """Load initial categories and questions"""
    # Create categories
    categories_data = [
        {'name': 'Grammar', 'slug': 'grammar', 'order': 1, 'description': 'Grammar questions'},
        {'name': 'Translation', 'slug': 'translation', 'order': 2, 'description': 'Translation from Uzbek to English'},
        {'name': 'Writing', 'slug': 'writing', 'order': 3, 'description': 'Essay writing'},
        {'name': 'Vocabulary', 'slug': 'vocabulary', 'order': 4, 'description': 'Vocabulary questions'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Created category: {category.name}")
    
    # Create sample questions
    grammar_cat = Category.objects.get(slug='grammar')
    translation_cat = Category.objects.get(slug='translation')
    writing_cat = Category.objects.get(slug='writing')
    vocabulary_cat = Category.objects.get(slug='vocabulary')
    
    questions_data = [
        # Grammar questions
        {
            'category': grammar_cat,
            'question_type': 'multiple_choice',
            'question_text': "Choose the correct form: I _____ to the store yesterday.",
            'options': ["go", "went", "gone", "going"],
            'correct_answer_index': 1,
            'points': 1,
            'order': 1
        },
        {
            'category': grammar_cat,
            'question_type': 'multiple_choice',
            'question_text': "Which sentence is grammatically correct?",
            'options': [
                "She don't like coffee.",
                "She doesn't like coffee.",
                "She not like coffee.",
                "She isn't like coffee."
            ],
            'correct_answer_index': 1,
            'points': 1,
            'order': 2
        },
        {
            'category': grammar_cat,
            'question_type': 'multiple_choice',
            'question_text': "Complete the sentence: If I _____ rich, I would travel the world.",
            'options': ["am", "was", "were", "be"],
            'correct_answer_index': 2,
            'points': 1,
            'order': 3
        },
        # Translation questions
        {
            'category': translation_cat,
            'question_type': 'translation',
            'question_text': "Salom, qandaysiz?",
            'instructions': 'Translate to English',
            'points': 2,
            'order': 1
        },
        {
            'category': translation_cat,
            'question_type': 'translation',
            'question_text': "Men universitetda o'qiyman.",
            'instructions': 'Translate to English',
            'points': 2,
            'order': 2
        },
        # Writing questions
        {
            'category': writing_cat,
            'question_type': 'writing',
            'question_text': "Describe your favorite hobby",
            'instructions': 'Write at least 100 words about your favorite hobby. Explain why you enjoy it and what you do.',
            'min_words': 100,
            'points': 10,
            'order': 1
        },
        {
            'category': writing_cat,
            'question_type': 'writing',
            'question_text': "Write about your future plans",
            'instructions': 'Describe your plans for the next 5 years. Include your career, education, and personal goals. Write at least 150 words.',
            'min_words': 150,
            'points': 10,
            'order': 2
        },
        # Vocabulary questions
        {
            'category': vocabulary_cat,
            'question_type': 'vocabulary',
            'question_text': "Eloquent",
            'options': [
                "Able to express ideas clearly and effectively",
                "Very quiet and shy",
                "Extremely angry",
                "Very tired"
            ],
            'correct_answer_index': 0,
            'points': 1,
            'order': 1
        },
        {
            'category': vocabulary_cat,
            'question_type': 'vocabulary',
            'question_text': "Benevolent",
            'options': [
                "Evil and harmful",
                "Kind and generous",
                "Very confused",
                "Extremely fast"
            ],
            'correct_answer_index': 1,
            'points': 1,
            'order': 2
        },
    ]
    
    for q_data in questions_data:
        question, created = Question.objects.get_or_create(
            category=q_data['category'],
            question_text=q_data['question_text'],
            defaults=q_data
        )
        if created:
            print(f"✓ Created question: {question.question_text[:50]}...")
    
    print("\n✅ Initial data loaded successfully!")


class Command(BaseCommand):
    help = 'Load initial categories and questions'

    def handle(self, *args, **options):
        load_data()
