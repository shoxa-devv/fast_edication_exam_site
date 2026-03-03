from django.core.management.base import BaseCommand
from exams.models import Level, Month, Category, Question, VocabularyWord


LEVELS = [
    ('Kids 1', 'kids1', 1, '#4CAF50', '\U0001F331', 'Bolalar uchun boshlang\'ich daraja / Начальный уровень для детей'),
    ('Kids 2', 'kids2', 2, '#66BB6A', '\U0001F33F', 'Bolalar uchun ikkinchi daraja / Второй уровень для детей'),
    ('Starter 1', 'starter1', 3, '#42A5F5', '\U0001F4D8', 'Yangi boshlovchilar uchun / Для начинающих'),
    ('Starter 2', 'starter2', 4, '#29B6F6', '\U0001F4D7', 'Boshlang\'ich bilim mustahkamlash / Закрепление начальных знаний'),
    ('A0', 'a0', 5, '#AB47BC', '\U0001F524', 'Boshlang\'ich daraja / Начальный уровень'),
    ('A1', 'a1', 6, '#7E57C2', '\U0001F4D6', 'Elementary daraja / Элементарный уровень'),
    ('A2', 'a2', 7, '#5C6BC0', '\U0001F4DA', 'Pre-Intermediate daraja / Ниже среднего уровня'),
    ('B1', 'b1', 8, '#FFA726', '\U0001F3AF', 'Intermediate daraja / Средний уровень'),
    ('B2 — IELTS Foundation', 'b2-ielts-foundation', 9, '#EF5350', '\U0001F3C6',
     'Upper-Intermediate / IELTS tayyorlov / Подготовка к IELTS'),
    ('C1 — IELTS Graduation', 'c1-ielts-graduation', 10, '#EC407A', '\U0001F393',
     'Advanced / IELTS yuqori daraja / Продвинутый уровень IELTS'),
    ('Intensive', 'intensive', 11, '#002147', '\U000026A1', 'Intensiv kurs — barcha darajalar / Интенсивный курс — все уровни'),
]

CATEGORIES = [
    ('Grammar', 'grammar', 1, 'Grammatika savollari / Вопросы по грамматике'),
    ('Vocabulary', 'vocabulary', 2, 'Lug\'at savollari / Вопросы по лексике'),
    ('Translation', 'translation', 3, 'Tarjima mashqlari / Упражнения по переводу'),
    ('Writing', 'writing', 4, 'Yozma ish / Письменная работа'),
]


def grammar_bank():
    """Grammar questions scaled by difficulty tier (0=easy, 1=medium, 2=hard)."""
    easy = [
        ("I _____ a student.", ["am", "is", "are", "be"], 0),
        ("She _____ to school every day.", ["go", "goes", "going", "went"], 1),
        ("They _____ playing now.", ["is", "are", "was", "am"], 1),
        ("This is _____ apple.", ["a", "an", "the", "---"], 1),
        ("He _____ a teacher.", ["is", "am", "are", "be"], 0),
        ("We _____ happy.", ["is", "are", "am", "be"], 1),
        ("_____ you like ice cream?", ["Do", "Does", "Is", "Are"], 0),
        ("The cat is _____ the table.", ["on", "at", "to", "in"], 0),
        ("She _____ two brothers.", ["have", "has", "had", "having"], 1),
        ("I can _____ English.", ["speak", "speaks", "speaking", "spoke"], 0),
        ("My name _____ John.", ["am", "is", "are", "be"], 1),
        ("There _____ a book on the table.", ["is", "are", "am", "be"], 0),
        ("I _____ not like coffee.", ["do", "does", "am", "is"], 0),
        ("She is _____ girl.", ["a", "an", "the", "---"], 0),
        ("How many books _____ you have?", ["do", "does", "is", "are"], 0),
    ]
    medium = [
        ("She _____ her homework yesterday.", ["do", "does", "did", "doing"], 2),
        ("He has been a doctor _____ 10 years.", ["for", "since", "from", "at"], 0),
        ("If I _____ you, I would study harder.", ["am", "was", "were", "be"], 2),
        ("The letter _____ by the secretary.", ["wrote", "was written", "written", "writing"], 1),
        ("I _____ already finished the project.", ["has", "have", "had", "having"], 1),
        ("She _____ to the store right now.", ["go", "goes", "is going", "went"], 2),
        ("By next year, I _____ graduated.", ["will have", "will", "have", "had"], 0),
        ("I look forward to _____ you.", ["see", "seeing", "saw", "seen"], 1),
        ("He suggested that she _____ early.", ["leave", "leaves", "left", "leaving"], 0),
        ("I have been _____ English for 5 years.", ["study", "studied", "studying", "studies"], 2),
        ("Neither Tom nor Jerry _____ here.", ["is", "are", "am", "were"], 0),
        ("Each student _____ a book.", ["have", "has", "having", "had"], 1),
        ("She is _____ than her sister.", ["tall", "taller", "tallest", "more tall"], 1),
        ("This is the _____ movie ever.", ["good", "better", "best", "most good"], 2),
        ("I don't have _____ money.", ["some", "any", "many", "few"], 1),
    ]
    hard = [
        ("Not only _____ smart, but also hardworking.", ["she is", "is she", "she was", "was she"], 1),
        ("Hardly _____ I arrived when it started raining.", ["have", "had", "did", "was"], 1),
        ("He speaks _____ he were the boss.", ["like", "as if", "so", "such"], 1),
        ("The sooner you start, the _____ you'll finish.", ["soon", "sooner", "soonest", "more soon"], 1),
        ("She denied _____ the window.", ["break", "breaking", "broke", "broken"], 1),
        ("Had I known, I _____ differently.", ["would act", "would have acted", "acted", "will act"], 1),
        ("Under no circumstances _____ leave early.", ["you should", "should you", "you can", "can you"], 1),
        ("So intense _____ the heat that we stayed inside.", ["is", "was", "were", "has been"], 1),
        ("The report needs _____.", ["rewrite", "rewriting", "rewrote", "rewritten"], 1),
        ("I'd rather you _____ smoke here.", ["don't", "didn't", "won't", "not"], 1),
        ("_____ the weather was bad, we went out.", ["Although", "Because", "So", "But"], 0),
        ("It's time we _____ home.", ["go", "went", "going", "gone"], 1),
        ("He avoided _____ to me.", ["talk", "talking", "talked", "to talk"], 1),
        ("She pretended _____ asleep.", ["be", "being", "to be", "been"], 2),
        ("I can't help _____ about the future.", ["worry", "worrying", "worried", "to worry"], 1),
    ]
    return easy, medium, hard


def vocab_bank():
    """Vocabulary questions scaled by difficulty."""
    easy = [
        ("Big", ["Large", "Small", "Tall", "Short"], 0),
        ("Happy", ["Joyful", "Sad", "Angry", "Tired"], 0),
        ("Fast", ["Quick", "Slow", "Heavy", "Light"], 0),
        ("Beautiful", ["Pretty", "Ugly", "Loud", "Quiet"], 0),
        ("Start", ["Begin", "End", "Stop", "Wait"], 0),
        ("Cold", ["Cool and low temperature", "Hot", "Warm", "Soft"], 0),
        ("Angry", ["Mad and upset", "Happy", "Calm", "Sleepy"], 0),
        ("Friend", ["A person you like", "Enemy", "Teacher", "Parent"], 0),
        ("Brave", ["Courageous", "Scared", "Lazy", "Weak"], 0),
        ("Kind", ["Nice and helpful", "Mean", "Rude", "Quiet"], 0),
    ]
    medium = [
        ("Eloquent", ["Fluent and persuasive", "Very quiet", "Angry", "Tired"], 0),
        ("Resilient", ["Able to recover quickly", "Very weak", "Stubborn", "Forgetful"], 0),
        ("Pragmatic", ["Dealing with things practically", "Emotional", "Idealistic", "Slow"], 0),
        ("Diligent", ["Hardworking and careful", "Lazy", "Fast", "Loud"], 1),
        ("Abundant", ["Existing in large quantities", "Scarce", "Small", "Old"], 0),
        ("Candid", ["Truthful and straightforward", "Dishonest", "Confused", "Anxious"], 0),
        ("Feasible", ["Possible and practical", "Impossible", "Imaginary", "Hard"], 0),
        ("Hostile", ["Unfriendly and aggressive", "Friendly", "Calm", "Peaceful"], 0),
        ("Keen", ["Eager and enthusiastic", "Lazy", "Bored", "Slow"], 0),
        ("Lucid", ["Clear and easy to understand", "Confusing", "Dark", "Mysterious"], 0),
    ]
    hard = [
        ("Ephemeral", ["Lasting a very short time", "Eternal", "Expensive", "Large"], 0),
        ("Ubiquitous", ["Found everywhere", "Rare", "Very old", "Small"], 0),
        ("Ambiguous", ["Open to more than one meaning", "Clear", "Simple", "Boring"], 0),
        ("Meticulous", ["Very careful about detail", "Careless", "Lazy", "Quick"], 0),
        ("Benevolent", ["Kind and generous", "Evil", "Confused", "Fast"], 0),
        ("Tenacious", ["Persistent and determined", "Lazy", "Weak", "Giving up"], 0),
        ("Impeccable", ["Without any faults", "Flawed", "Average", "Poor"], 0),
        ("Mitigate", ["Make less severe", "Worsen", "Increase", "Complicate"], 0),
        ("Plausible", ["Seeming reasonable", "Impossible", "Ridiculous", "Absurd"], 0),
        ("Ominous", ["Giving impression of bad things", "Cheerful", "Bright", "Happy"], 0),
    ]
    return easy, medium, hard


def translation_bank():
    """Translations by difficulty."""
    easy = [
        "Salom, qandaysiz?", "Men talabaman.", "Bu kitob.", "U o'qituvchi.",
        "Biz maktabga boramiz.", "Bugun yakshanba.", "Mening ismim Ahmad.",
        "U chiroyli qiz.", "Men choy ichaman.", "Ular futbol o'ynaydi.",
    ]
    medium = [
        "Men har kuni ertalab yuguraman.", "U juda aqlli talaba.",
        "Biz yangi uy sotib oldik.", "Bugun ob-havo juda yaxshi.",
        "Men do'stim bilan kinoga bordim.", "U shifokor bo'lishni xohlaydi.",
        "Mening oilam katta.", "U ingliz tilini o'rganyapti.",
        "Biz Toshkentda yashaymiz.", "Men kitob o'qishni yaxshi ko'raman.",
    ]
    hard = [
        "Agar men sizning o'rningizda bo'lganimda, ko'proq o'qigan bo'lardim.",
        "U universitetni tugatganidan keyin chet elga ketmoqchi.",
        "Hukumat ta'lim tizimini yaxshilash bo'yicha yangi dastur ishlab chiqdi.",
        "Texnologiyaning rivojlanishi kundalik hayotimizni tubdan o'zgartirdi.",
        "O'z-o'zini rivojlantirish muvaffaqiyatga erishishning asosiy omilidir.",
        "Atrof-muhitni muhofaza qilish har birimizning burchimizdir.",
        "Zamonaviy ta'lim tizimi talabalarning tanqidiy fikrlashini rivojlantirishga qaratilgan.",
        "Globallashuv jarayoni barcha mamlakatlarga ta'sir ko'rsatmoqda.",
        "Sun'iy intellektning kelajagi haqida turli fikrlar mavjud.",
        "Sog'lom turmush tarzi uzoq umr ko'rishning kalitidir.",
    ]
    return easy, medium, hard


def writing_bank():
    """Writing topics by difficulty."""
    easy = [
        ("My Family", "Write about your family. 50+ words. / Напишите о своей семье. 50+ слов."),
        ("My School", "Describe your school. 50+ words. / Опишите свою школу. 50+ слов."),
        ("My Hobby", "Write about your favorite hobby. 50+ words. / Напишите о своём хобби. 50+ слов."),
        ("My Best Friend", "Describe your best friend. 60+ words. / Опишите лучшего друга. 60+ слов."),
        ("My Favorite Food", "Write about your favorite food. 50+ words. / Напишите о любимой еде. 50+ слов."),
    ]
    medium = [
        ("The Importance of Education", "Write about why education is important. 100+ words. / Почему образование важно? 100+ слов."),
        ("My Future Plans", "Describe your plans for the next 5 years. 100+ words. / Опишите планы на 5 лет. 100+ слов."),
        ("Technology in Daily Life", "How has technology changed our lives? 100+ words. / Как технологии изменили нашу жизнь? 100+ слов."),
        ("My Favorite Book", "Write about a book that influenced you. 100+ words. / Напишите о книге, которая повлияла на вас. 100+ слов."),
        ("The Benefits of Reading", "Why is reading important? 100+ words. / Почему чтение важно? 100+ слов."),
    ]
    hard = [
        ("Climate Change", "Discuss causes and solutions of climate change. 150+ words. / Обсудите причины и решения изменения климата. 150+ слов."),
        ("AI and the Future", "Write about AI's impact on society. 150+ words. / Напишите о влиянии ИИ на общество. 150+ слов."),
        ("Online vs Traditional Education", "Compare and contrast. 150+ words. / Сравните онлайн и традиционное обучение. 150+ слов."),
        ("Globalization", "Discuss pros and cons of globalization. 150+ words. / Обсудите плюсы и минусы глобализации. 150+ слов."),
        ("The Role of Youth in Society", "How can young people make a difference? 150+ words. / Какую роль молодёжь играет в обществе? 150+ слов."),
    ]
    return easy, medium, hard


TIER_MAP = {
    'kids1': 0, 'kids2': 0, 'starter1': 0, 'starter2': 0,
    'a0': 0, 'a1': 1, 'a2': 1,
    'b1': 1, 'b2-ielts-foundation': 2,
    'c1-ielts-graduation': 2, 'intensive': 2,
}


def load_data():
    cats = {}
    for name, slug, order, desc in CATEGORIES:
        obj, created = Category.objects.get_or_create(
            slug=slug, defaults={'name': name, 'order': order, 'description': desc}
        )
        cats[slug] = obj
        if created:
            print(f"  + Category: {name}")

    lvl_objs = {}
    for name, slug, order, color, icon, desc in LEVELS:
        obj, created = Level.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name, 'order': order, 'color': color,
                'icon': icon, 'description': desc,
            }
        )
        lvl_objs[slug] = obj
        if created:
            print(f"  + Level: {name}")

    month_objs = {}
    for slug, lvl in lvl_objs.items():
        for num in range(1, 4):
            ru_months = {1: '1-месяц', 2: '2-месяц', 3: '3-месяц'}
            m, created = Month.objects.get_or_create(
                level=lvl, number=num,
                defaults={'name': f'{num}-oy / {ru_months[num]}'}
            )
            month_objs[(slug, num)] = m
            if created:
                print(f"  + Month: {lvl.name} — {num}-oy")

    existing = Question.objects.count()
    if existing >= 200:
        print(f"  i {existing} questions already exist, skipping question generation.")
        return

    print("  Loading questions for all levels...")

    g_easy, g_med, g_hard = grammar_bank()
    v_easy, v_med, v_hard = vocab_bank()
    t_easy, t_med, t_hard = translation_bank()
    w_easy, w_med, w_hard = writing_bank()

    grammar_tiers = [g_easy, g_med, g_hard]
    vocab_tiers = [v_easy, v_med, v_hard]
    trans_tiers = [t_easy, t_med, t_hard]
    write_tiers = [w_easy, w_med, w_hard]

    bulk = []
    for slug, lvl in lvl_objs.items():
        tier = TIER_MAP.get(slug, 0)

        for month_num in range(1, 4):
            month = month_objs[(slug, month_num)]

            gqs = grammar_tiers[tier]
            start = (month_num - 1) * 5 % len(gqs)
            for i in range(5):
                idx = (start + i) % len(gqs)
                text, opts, correct = gqs[idx]
                bulk.append(Question(
                    level=lvl, month=month, category=cats['grammar'],
                    question_type='multiple_choice',
                    question_text=text, options=opts, correct_answer_index=correct,
                    points=1, order=i + 1, is_active=True,
                ))

            vqs = vocab_tiers[tier]
            start = (month_num - 1) * 4 % len(vqs)
            for i in range(4):
                idx = (start + i) % len(vqs)
                word, opts, correct = vqs[idx]
                bulk.append(Question(
                    level=lvl, month=month, category=cats['vocabulary'],
                    question_type='vocabulary',
                    question_text=word, options=opts, correct_answer_index=correct,
                    points=1, order=i + 1, is_active=True,
                ))

            tqs = trans_tiers[tier]
            start = (month_num - 1) * 3 % len(tqs)
            for i in range(3):
                idx = (start + i) % len(tqs)
                text = tqs[idx]
                bulk.append(Question(
                    level=lvl, month=month, category=cats['translation'],
                    question_type='translation',
                    question_text=text, instructions='Ingliz tiliga tarjima qiling / Переведите на английский',
                    points=2, order=i + 1, is_active=True,
                ))

            wqs = write_tiers[tier]
            idx = (month_num - 1) % len(wqs)
            topic, instr = wqs[idx]
            min_w = 50 if tier == 0 else 100 if tier == 1 else 150
            bulk.append(Question(
                level=lvl, month=month, category=cats['writing'],
                question_type='writing',
                question_text=topic, instructions=instr,
                min_words=min_w, points=10, order=1, is_active=True,
            ))

    Question.objects.bulk_create(bulk, ignore_conflicts=True)
    total = Question.objects.count()
    print(f"\n  {total} questions loaded successfully!")
    print(f"  {Level.objects.count()} levels, {Month.objects.count()} months")


class Command(BaseCommand):
    help = 'Load initial levels, months, categories, and questions'

    def handle(self, *args, **options):
        load_data()
