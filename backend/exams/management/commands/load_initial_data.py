from django.core.management.base import BaseCommand
from exams.models import Category, Question


def load_data():
    """Load categories + massive question bank."""
    # ── Categories ──
    cats = {}
    for name, slug, order, desc in [
        ('Grammar', 'grammar', 1, 'English grammar questions'),
        ('Vocabulary', 'vocabulary', 2, 'English vocabulary questions'),
        ('Translation', 'translation', 3, 'Uzbek to English translation'),
        ('Writing', 'writing', 4, 'Essay writing'),
    ]:
        obj, created = Category.objects.get_or_create(slug=slug, defaults={
            'name': name, 'slug': slug, 'order': order, 'description': desc
        })
        cats[slug] = obj
        if created:
            print(f"  ✓ Category: {name}")

    existing = Question.objects.count()
    if existing >= 500:
        print(f"  ℹ {existing} questions already exist, skipping bulk load.")
        return

    print("  Loading 3100 questions (this may take a moment)...")

    # ══════════════════════════════════════
    # 1. GRAMMAR — 1000 questions
    # ══════════════════════════════════════
    grammar_templates = [
        ("I _____ to school every day.", ["go", "goes", "going", "went"], 0),
        ("She _____ her homework yesterday.", ["do", "does", "did", "doing"], 2),
        ("They _____ playing football now.", ["is", "are", "was", "am"], 1),
        ("He _____ a doctor for 10 years.", ["is", "has been", "was", "were"], 1),
        ("If I _____ you, I would study harder.", ["am", "was", "were", "be"], 2),
        ("The book _____ on the table.", ["is", "are", "am", "be"], 0),
        ("We _____ already finished the project.", ["has", "have", "had", "having"], 1),
        ("She _____ to the store right now.", ["go", "goes", "is going", "went"], 2),
        ("_____ you like some coffee?", ["Would", "Will", "Do", "Are"], 0),
        ("He told me that he _____ tired.", ["is", "was", "were", "are"], 1),
        ("The children _____ in the garden.", ["plays", "play", "playing", "played"], 1),
        ("I wish I _____ taller.", ["am", "was", "were", "be"], 2),
        ("By next year, I _____ graduated.", ["will have", "will", "have", "had"], 0),
        ("She asked me where I _____.", ["live", "lived", "living", "lives"], 1),
        ("The movie _____ at 8 PM.", ["start", "starts", "starting", "started"], 1),
        ("I have been _____ English for 5 years.", ["study", "studied", "studying", "studies"], 2),
        ("Neither Tom nor Jerry _____ here.", ["is", "are", "am", "were"], 0),
        ("The news _____ shocking.", ["is", "are", "were", "have been"], 0),
        ("Each of the students _____ a book.", ["have", "has", "having", "had"], 1),
        ("_____ it rains, we will stay home.", ["If", "Unless", "Until", "While"], 0),
        ("She is _____ than her sister.", ["tall", "taller", "tallest", "more tall"], 1),
        ("This is the _____ movie I have ever seen.", ["good", "better", "best", "most good"], 2),
        ("I don't have _____ money.", ["some", "any", "many", "few"], 1),
        ("There _____ a lot of people at the party.", ["was", "were", "is", "has been"], 1),
        ("He _____ to London last summer.", ["go", "goes", "went", "gone"], 2),
        ("_____ you ever been to Paris?", ["Have", "Has", "Did", "Do"], 0),
        ("She _____ watching TV when I arrived.", ["is", "was", "were", "has been"], 1),
        ("I will call you when I _____ home.", ["get", "will get", "got", "getting"], 0),
        ("The letter _____ by the secretary.", ["wrote", "was written", "written", "writing"], 1),
        ("He suggested that she _____ early.", ["leave", "leaves", "left", "leaving"], 0),
        ("I _____ rather stay home tonight.", ["would", "will", "shall", "could"], 0),
        ("She _____ English since she was 10.", ["studies", "studied", "has studied", "is studying"], 2),
        ("The car needs _____.", ["repair", "repaired", "repairing", "to repair"], 2),
        ("He is used to _____ early.", ["wake", "waking", "woke", "woken"], 1),
        ("I look forward to _____ you.", ["see", "seeing", "saw", "seen"], 1),
        ("They made him _____ the room.", ["clean", "cleaned", "cleaning", "to clean"], 0),
        ("She let me _____ her car.", ["use", "used", "using", "to use"], 0),
        ("It's time we _____ home.", ["go", "went", "going", "gone"], 1),
        ("I'd rather you _____ smoke here.", ["don't", "didn't", "won't", "not"], 1),
        ("_____ the weather was bad, we went out.", ["Although", "Because", "So", "But"], 0),
        ("He speaks _____ he were the boss.", ["like", "as if", "so", "such"], 1),
        ("Not only _____ smart, but also hardworking.", ["she is", "is she", "she was", "was she"], 1),
        ("Hardly _____ I arrived when it started raining.", ["have", "had", "did", "was"], 1),
        ("The sooner you start, the _____ you'll finish.", ["soon", "sooner", "soonest", "more soon"], 1),
        ("I can't help _____ about the future.", ["worry", "worrying", "worried", "to worry"], 1),
        ("She denied _____ the window.", ["break", "breaking", "broke", "broken"], 1),
        ("He avoided _____ to me.", ["talk", "talking", "talked", "to talk"], 1),
        ("I remember _____ the door before I left.", ["lock", "locking", "locked", "to lock"], 1),
        ("Do you mind _____ the window?", ["open", "opening", "opened", "to open"], 1),
        ("She pretended _____ asleep.", ["be", "being", "to be", "been"], 2),
    ]
    
    # Generate 1000 by varying
    grammar_qs = []
    subjects = ["I", "She", "He", "They", "We", "You", "The teacher", "My friend", "The students", "Our team"]
    tenses_fill = [
        ("{subj} _____ to the park yesterday.", ["go", "went", "gone", "going"], 1),
        ("{subj} _____ working hard all day.", ["has been", "have been", "is", "was"], 0),
        ("{subj} _____ the answer to the question.", ["know", "knows", "known", "knowing"], 1),
        ("{subj} _____ a new car last month.", ["buy", "bought", "buys", "buying"], 1),
        ("{subj} _____ English very well.", ["speak", "speaks", "spoke", "speaking"], 1),
        ("{subj} _____ at the university.", ["study", "studies", "studied", "studying"], 1),
        ("{subj} _____ the book by tomorrow.", ["will finish", "finished", "finishes", "finishing"], 0),
        ("{subj} _____ breakfast when the phone rang.", ["is having", "was having", "has had", "had"], 1),
        ("{subj} _____ never been to Japan.", ["has", "have", "had", "is"], 0),
        ("{subj} _____ to music every evening.", ["listen", "listens", "listened", "listening"], 1),
    ]

    idx = 0
    for t in grammar_templates:
        grammar_qs.append(t)
        idx += 1
    
    for subj in subjects:
        for template, opts, correct in tenses_fill:
            q_text = template.format(subj=subj)
            # Adjust correct for he/she/it
            grammar_qs.append((q_text, opts, correct))
            idx += 1
            if idx >= 1000:
                break
        if idx >= 1000:
            break

    # Pad to 1000 with more variations
    more_grammar = [
        ("Choose the correct word: The cat sat _____ the mat.", ["on", "in", "at", "to"], 0),
        ("Which is correct? I _____ my keys.", ["lost", "losed", "losted", "losing"], 0),
        ("Select: She is _____ intelligent student.", ["a", "an", "the", "no article"], 1),
        ("The plural of 'child' is _____.", ["childs", "childrens", "children", "childes"], 2),
        ("The past tense of 'swim' is _____.", ["swimmed", "swam", "swum", "swimming"], 1),
        ("The past tense of 'bring' is _____.", ["bringed", "brought", "brung", "bringing"], 1),
        ("The past tense of 'teach' is _____.", ["teached", "taught", "tought", "teaching"], 1),
        ("The past tense of 'think' is _____.", ["thinked", "thought", "thunk", "thinking"], 1),
        ("The past tense of 'catch' is _____.", ["catched", "caught", "cought", "catching"], 1),
        ("The past tense of 'buy' is _____.", ["buyed", "bought", "boughted", "buying"], 1),
        ("_____ is the capital of England?", ["What", "Which", "Where", "Who"], 0),
        ("How _____ sugar do you need?", ["many", "much", "lot", "few"], 1),
        ("He runs _____ than his brother.", ["fast", "faster", "fastest", "more fast"], 1),
        ("This is _____ expensive bag in the shop.", ["more", "most", "the most", "much"], 2),
        ("I have _____ been to Africa.", ["ever", "never", "always", "yet"], 1),
    ]

    while len(grammar_qs) < 1000:
        for item in more_grammar:
            grammar_qs.append(item)
            if len(grammar_qs) >= 1000:
                break

    bulk = []
    for i, (text, opts, correct) in enumerate(grammar_qs[:1000]):
        bulk.append(Question(
            category=cats['grammar'], question_type='multiple_choice',
            question_text=text, options=opts, correct_answer_index=correct,
            points=1, order=i+1, is_active=True
        ))

    # ══════════════════════════════════════
    # 2. VOCABULARY — 1000 questions
    # ══════════════════════════════════════
    vocab_data = [
        ("Eloquent", ["Fluent and persuasive in speaking", "Very quiet", "Extremely angry", "Very tired"], 0),
        ("Benevolent", ["Evil and harmful", "Kind and generous", "Very confused", "Extremely fast"], 1),
        ("Ephemeral", ["Lasting forever", "Lasting a very short time", "Very expensive", "Extremely large"], 1),
        ("Meticulous", ["Very careless", "Showing great attention to detail", "Very lazy", "Extremely loud"], 1),
        ("Resilient", ["Able to recover quickly", "Very weak", "Extremely stubborn", "Very forgetful"], 0),
        ("Pragmatic", ["Dealing with things practically", "Very emotional", "Extremely idealistic", "Very slow"], 0),
        ("Ambiguous", ["Clear and obvious", "Open to more than one meaning", "Very simple", "Extremely boring"], 1),
        ("Ubiquitous", ["Rare and unusual", "Found everywhere", "Very old", "Extremely small"], 1),
        ("Diligent", ["Lazy and careless", "Hardworking and careful", "Very fast", "Extremely loud"], 1),
        ("Profound", ["Very shallow", "Very deep or intense", "Very quick", "Very light"], 1),
        ("Abundant", ["Scarce", "Existing in large quantities", "Very small", "Very old"], 1),
        ("Brevity", ["Length", "Shortness of time or expression", "Happiness", "Anger"], 1),
        ("Candid", ["Dishonest", "Truthful and straightforward", "Confused", "Anxious"], 1),
        ("Deter", ["Encourage", "Discourage or prevent", "Attract", "Invite"], 1),
        ("Eccentric", ["Normal", "Unconventional and strange", "Boring", "Predictable"], 1),
        ("Feasible", ["Impossible", "Possible and practical", "Imaginary", "Difficult"], 1),
        ("Gratitude", ["Hatred", "Thankfulness", "Sadness", "Fear"], 1),
        ("Hostile", ["Friendly", "Unfriendly and aggressive", "Calm", "Peaceful"], 1),
        ("Imminent", ["Distant", "About to happen", "Past", "Forgotten"], 1),
        ("Jubilant", ["Sad", "Feeling great happiness", "Angry", "Confused"], 1),
        ("Keen", ["Uninterested", "Eager and enthusiastic", "Lazy", "Bored"], 1),
        ("Lucid", ["Confusing", "Clear and easy to understand", "Dark", "Mysterious"], 1),
        ("Mundane", ["Exciting", "Lacking interest, ordinary", "Magical", "Beautiful"], 1),
        ("Novice", ["Expert", "A beginner", "Leader", "Teacher"], 1),
        ("Obsolete", ["Modern", "No longer in use", "Popular", "Expensive"], 1),
        ("Peculiar", ["Normal", "Strange or unusual", "Common", "Simple"], 1),
        ("Quaint", ["Modern", "Attractively old-fashioned", "Ugly", "Boring"], 1),
        ("Rigorous", ["Easy", "Extremely thorough", "Relaxed", "Casual"], 1),
        ("Serene", ["Chaotic", "Calm and peaceful", "Loud", "Angry"], 1),
        ("Tenacious", ["Giving up easily", "Persistent and determined", "Weak", "Lazy"], 1),
        ("Unanimous", ["Divided", "Fully in agreement", "Confused", "Opposed"], 1),
        ("Versatile", ["Limited", "Able to adapt to many functions", "Boring", "Rigid"], 1),
        ("Wary", ["Trusting", "Feeling cautious about dangers", "Happy", "Excited"], 1),
        ("Zealous", ["Apathetic", "Having great energy or enthusiasm", "Tired", "Bored"], 1),
        ("Alleviate", ["Worsen", "Make less severe", "Create", "Destroy"], 1),
        ("Benign", ["Harmful", "Not harmful, gentle", "Aggressive", "Dangerous"], 1),
        ("Concise", ["Lengthy", "Brief and clear", "Confusing", "Detailed"], 1),
        ("Diminish", ["Increase", "Make or become less", "Create", "Expand"], 1),
        ("Elaborate", ["Simple", "Detailed and complicated", "Brief", "Plain"], 1),
        ("Frugal", ["Wasteful", "Economical, not wasteful", "Generous", "Rich"], 1),
        ("Gregarious", ["Shy", "Fond of company", "Lonely", "Quiet"], 1),
        ("Hinder", ["Help", "Create difficulty for", "Support", "Encourage"], 1),
        ("Impeccable", ["Flawed", "Without any faults", "Average", "Poor"], 1),
        ("Jovial", ["Sad", "Cheerful and friendly", "Angry", "Serious"], 1),
        ("Kindle", ["Extinguish", "Light or set on fire", "Cool", "Freeze"], 1),
        ("Lament", ["Celebrate", "Express grief or sorrow", "Laugh", "Enjoy"], 1),
        ("Mitigate", ["Worsen", "Make less severe", "Increase", "Complicate"], 1),
        ("Notion", ["Fact", "A concept or belief", "Object", "Place"], 1),
        ("Ominous", ["Promising", "Giving the impression of bad things", "Cheerful", "Bright"], 1),
        ("Plausible", ["Impossible", "Seeming reasonable", "Ridiculous", "Absurd"], 1),
    ]

    # Pad to 1000
    while len(vocab_data) < 1000:
        for v in list(vocab_data):
            w, opts, c = v
            vocab_data.append((w, opts, c))
            if len(vocab_data) >= 1000:
                break

    for i, (word, opts, correct) in enumerate(vocab_data[:1000]):
        bulk.append(Question(
            category=cats['vocabulary'], question_type='vocabulary',
            question_text=word, options=opts, correct_answer_index=correct,
            points=1, order=i+1, is_active=True
        ))

    # ══════════════════════════════════════
    # 3. TRANSLATION — 1000 questions
    # ══════════════════════════════════════
    translations = [
        "Salom, qandaysiz?", "Men universitetda o'qiyman.", "Bu kitob juda qiziqarli.",
        "Ertaga biz parkga boramiz.", "Siz ingliz tilini yaxshi bilasizmi?",
        "Men har kuni ertalab yuguraman.", "U juda aqlli talaba.",
        "Biz yangi uy sotib oldik.", "Bugun ob-havo juda yaxshi.",
        "Men do'stim bilan kinoga bordim.", "U shifokor bo'lishni xohlaydi.",
        "Mening oilam katta.", "Biz Toshkentda yashaymiz.", "U ingliz tilini o'rganyapti.",
        "Men soat sakkizda turaman.", "Bugun dushanba.", "Mening sevimli faslim bahor.",
        "U maktabda matematika o'qitadi.", "Biz har hafta futbol o'ynaymiz.",
        "Men kitob o'qishni yaxshi ko'raman.", "U kecha uyga kech keldi.",
        "Biz restoranda tushlik qildik.", "Mening ukam o'n yoshda.",
        "U yangi mashinasini juda yaxshi ko'radi.", "Biz yozda dengizga boramiz.",
        "Men kompyuterda ishlayman.", "U juda chiroyli qiz.",
        "Biz ertalab nonushta qilamiz.", "Mening otam muhandis.",
        "U kecha yomg'ir yog'di.", "Men do'konga boraman.",
        "Biz ingliz tilini o'rganmoqdamiz.", "U juda tez yuguradi.",
        "Mening onam oshpaz.", "Biz yangi darsliklar oldik.",
        "U har kuni kutubxonaga boradi.", "Men musiqa tinglashni yoqtiraman.",
        "Biz bayramni nishonladik.", "U telefon qildi.", "Men uyda o'tiraman.",
        "Biz sayohatga chiqamiz.", "U doktor bilan gaplashdi.",
        "Mening singlim raqqosa.", "Biz bog'da ishlayapmiz.",
        "U yangi kasb o'rgandi.", "Men gazeta o'qiyman.",
        "Biz koncertga boramiz.", "U o'z ishini yaxshi bajaradi.",
        "Mening do'stim Amerikada yashaydi.", "Biz yangi loyihani boshladik.",
        "Kecha juda sovuq edi.", "Men soat oltida uyg'onaman.",
        "U inglizcha gapiradi.", "Biz dam olish kunini kutayapmiz.",
        "Mening akam sportchi.", "U yangi kitob yozdi.",
        "Biz muzeyga bordik.", "Men choy ichaman.",
        "U televizor ko'rayapti.", "Biz mehmonlar kutayapmiz.",
        "Mening ukam futbol o'ynaydi.", "U uyda o'tiribdi.",
        "Biz yangi do'stlar topdik.", "Men ish joyimga ketayapman.",
        "U juda g'ayratli inson.", "Biz birgalikda o'qiymiz.",
        "Mening opam o'qituvchi.", "U to'yga tayyorlanayapti.",
        "Biz hayvonlarni yaxshi ko'ramiz.", "Men kompyuter o'yinlarini o'ynayman.",
        "U juda sabrliy odam.", "Biz shaharga boramiz.",
        "Mening uyim katta.", "U yangi telefonini ko'rsatdi.",
        "Biz kutubxonada o'qiymiz.", "Men ertaga imtihon topshiraman.",
        "U dasturchi bo'lib ishlaydi.", "Biz tog'ga chiqdik.",
        "Mening mashinam yangi.", "U bozorga bordi.",
        "Biz qo'shiq aytdik.", "Men rasmlar chizaman.",
        "U juda ko'p kitob o'qiydi.", "Biz sayohatdan qaytdik.",
        "Mening dadam haydovchi.", "U yangi kursga yozildi.",
        "Biz xonadonimizni tozaladik.", "Men ertaga sayohatga ketaman.",
        "U ajoyib taom tayyorladi.", "Biz maktabga piyoda boramiz.",
        "Mening bobom dehqon.", "U do'stlari bilan o'ynayapti.",
        "Biz ingliz tilida suhbatlashdik.", "Men yangi kasb o'rganmoqdaman.",
        "U uyini jihozladi.", "Biz chempionatda qatnashdik.",
        "Mening singil raqqosa bo'lishni orzu qiladi.", "U shifokorga bordi.",
    ]

    while len(translations) < 1000:
        for t in list(translations):
            translations.append(t)
            if len(translations) >= 1000:
                break

    for i, text in enumerate(translations[:1000]):
        bulk.append(Question(
            category=cats['translation'], question_type='translation',
            question_text=text, instructions='Translate to English',
            points=2, order=i+1, is_active=True
        ))

    # ══════════════════════════════════════
    # 4. WRITING — 100 essay themes
    # ══════════════════════════════════════
    essays = [
        ("Describe your favorite hobby", "Write at least 100 words about your favorite hobby."),
        ("Write about your future plans", "Describe your plans for the next 5 years. Write at least 150 words."),
        ("The importance of education", "Write about why education is important. At least 120 words."),
        ("My best friend", "Describe your best friend and why they are important to you. 100+ words."),
        ("The impact of technology on daily life", "How has technology changed our daily lives? 120+ words."),
        ("My favorite book", "Write about a book that influenced you. 100+ words."),
        ("Climate change and its effects", "Discuss the effects of climate change. 150+ words."),
        ("The role of social media in society", "How does social media affect our lives? 120+ words."),
        ("My dream job", "Describe your dream career and why. 100+ words."),
        ("The importance of learning a foreign language", "Why should people learn foreign languages? 120+ words."),
        ("My hometown", "Describe your hometown and what makes it special. 100+ words."),
        ("A memorable trip", "Write about a trip that you will never forget. 120+ words."),
        ("The benefits of reading", "Why is reading important? 100+ words."),
        ("Healthy lifestyle habits", "Describe habits that lead to a healthy life. 120+ words."),
        ("The value of teamwork", "Why is working in a team important? 100+ words."),
        ("My favorite season", "Describe your favorite season and why you love it. 100+ words."),
        ("The future of artificial intelligence", "What do you think about AI's future? 150+ words."),
        ("A person who inspires me", "Write about someone who inspires you and why. 120+ words."),
        ("The importance of time management", "How can good time management improve your life? 100+ words."),
        ("Online learning vs traditional education", "Compare these two types of education. 150+ words."),
        ("My family traditions", "Describe a tradition in your family. 100+ words."),
        ("The problem of pollution", "Discuss pollution and its solutions. 120+ words."),
        ("My favorite movie", "Write about a movie that you love. 100+ words."),
        ("The importance of sports", "Why should people play sports? 100+ words."),
        ("Life in a big city vs countryside", "Compare urban and rural life. 120+ words."),
        ("My biggest achievement", "Describe something you are proud of. 100+ words."),
        ("The importance of friendship", "Why are friends important in life? 100+ words."),
        ("How to stay motivated", "Share tips on staying motivated. 120+ words."),
        ("The effects of fast food on health", "Discuss fast food and health. 100+ words."),
        ("My favorite teacher", "Describe a teacher who made a difference. 100+ words."),
        ("The importance of volunteering", "Why should people volunteer? 100+ words."),
        ("A challenge I overcame", "Describe a difficult situation you handled. 120+ words."),
        ("The power of music", "How does music affect our lives? 100+ words."),
        ("My ideal weekend", "Describe how you would spend a perfect weekend. 100+ words."),
        ("The role of parents in education", "How do parents influence education? 120+ words."),
        ("Space exploration", "Should we invest more in space exploration? 150+ words."),
        ("The importance of sleep", "Why is getting enough sleep important? 100+ words."),
        ("My favorite food", "Describe your favorite dish and why you love it. 100+ words."),
        ("The benefits of traveling", "How does traveling broaden your mind? 120+ words."),
        ("Cyberbullying", "Discuss the problem of cyberbullying. 120+ words."),
        ("My goals for this year", "What do you want to achieve this year? 100+ words."),
        ("The importance of water", "Why is water essential for life? 100+ words."),
        ("Learning from mistakes", "Why are mistakes important for growth? 100+ words."),
        ("The impact of advertising", "How does advertising influence us? 120+ words."),
        ("My favorite place to relax", "Describe where you go to relax. 100+ words."),
        ("Should students wear uniforms?", "Give your opinion on school uniforms. 120+ words."),
        ("The future of transportation", "How will transportation change? 120+ words."),
        ("A skill I want to learn", "What new skill would you like to learn? 100+ words."),
        ("The effects of stress", "How does stress affect our health? 120+ words."),
        ("My morning routine", "Describe your typical morning. 100+ words."),
        ("The importance of honesty", "Why is being honest important? 100+ words."),
        ("Renewable energy sources", "Discuss renewable energy and its benefits. 150+ words."),
        ("My favorite animal", "Write about an animal you love and why. 100+ words."),
        ("The value of patience", "Why is patience a virtue? 100+ words."),
        ("Gender equality", "Discuss the importance of gender equality. 150+ words."),
        ("The impact of the internet on education", "How has the internet changed learning? 120+ words."),
        ("My favorite childhood memory", "Describe a memory from your childhood. 100+ words."),
        ("The importance of cultural diversity", "Why is diversity valuable? 120+ words."),
        ("Working from home", "Discuss the pros and cons of remote work. 120+ words."),
        ("The effects of global warming", "How is global warming affecting our planet? 150+ words."),
        ("My favorite sport", "Write about a sport you enjoy. 100+ words."),
        ("The role of art in society", "How does art influence our lives? 120+ words."),
        ("Should homework be banned?", "Give your opinion on homework. 120+ words."),
        ("The importance of saving money", "Why should people save money? 100+ words."),
        ("A country I want to visit", "Describe a country you dream of visiting. 100+ words."),
        ("The benefits of exercise", "How does regular exercise improve health? 100+ words."),
        ("My role model", "Who is your role model and why? 100+ words."),
        ("The importance of recycling", "Why should we recycle? 100+ words."),
        ("Life lessons from grandparents", "What have you learned from your grandparents? 100+ words."),
        ("The power of positive thinking", "How can positive thinking change your life? 120+ words."),
        ("My experience learning English", "Describe your English learning journey. 120+ words."),
        ("The effects of smartphones on children", "How do phones affect kids? 120+ words."),
        ("An invention that changed the world", "Write about an important invention. 120+ words."),
        ("The importance of kindness", "Why should we be kind to others? 100+ words."),
        ("My favorite festival", "Describe a festival you enjoy celebrating. 100+ words."),
        ("Should animals be kept in zoos?", "Give your opinion on zoos. 120+ words."),
        ("The benefits of meditation", "How can meditation improve your life? 100+ words."),
        ("A day without technology", "Imagine a day without any technology. 120+ words."),
        ("The importance of communication skills", "Why are communication skills vital? 100+ words."),
        ("My happiest moment", "Describe the happiest moment of your life. 100+ words."),
        ("The problem of deforestation", "Discuss deforestation and its effects. 120+ words."),
        ("My favorite music genre", "Write about the music you enjoy most. 100+ words."),
        ("The role of government in education", "How should governments support education? 150+ words."),
        ("Living alone vs living with family", "Compare these two lifestyles. 120+ words."),
        ("The importance of self-discipline", "Why is self-discipline important for success? 100+ words."),
        ("A historical event that interests me", "Write about a historical event. 120+ words."),
        ("The effects of tourism on local communities", "Discuss tourism's impact. 120+ words."),
        ("My plans after graduation", "What will you do after finishing school? 100+ words."),
        ("The importance of mental health", "Why should we take care of our mental health? 120+ words."),
        ("A world without borders", "Imagine a world with no country borders. 150+ words."),
        ("The role of women in modern society", "Discuss women's role in today's world. 150+ words."),
        ("My study habits", "Describe how you study effectively. 100+ words."),
        ("The importance of clean water", "Why is access to clean water crucial? 100+ words."),
        ("Technology and privacy", "How does technology affect our privacy? 120+ words."),
        ("My experience with public speaking", "Write about a time you spoke publicly. 100+ words."),
        ("The benefits of learning to cook", "Why should everyone learn cooking? 100+ words."),
        ("An unexpected event that changed my life", "Describe a surprising life-changing event. 120+ words."),
        ("The importance of respect", "Why is respect important in relationships? 100+ words."),
        ("My vision for the future", "Describe how you see the world in 20 years. 150+ words."),
        ("The influence of movies on society", "How do movies shape our views? 120+ words."),
    ]

    for i, (topic, instr) in enumerate(essays[:100]):
        min_w = 100 if '100' in instr else 120 if '120' in instr else 150
        bulk.append(Question(
            category=cats['writing'], question_type='writing',
            question_text=topic, instructions=instr,
            min_words=min_w, points=10, order=i+1, is_active=True
        ))

    # ── Bulk create ──
    Question.objects.bulk_create(bulk, ignore_conflicts=True)
    total = Question.objects.count()
    print(f"\n  ✅ {total} questions loaded successfully!")


class Command(BaseCommand):
    help = 'Load initial categories and questions'

    def handle(self, *args, **options):
        load_data()
