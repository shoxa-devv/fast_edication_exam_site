/* ═══════════════════════════════════════════
   Fast Education — SPA Engine
   Flow: Register → Levels → Months → Exam → Results
   ═══════════════════════════════════════════ */
const API = '/api';
let studentId = null, studentName = '', teacherName = '';
let levels = [], currentLevel = null, currentMonth = null;
let months = [], currentLevelInfo = null;
let cats = [], qs = [], ans = {};
let qi = 0, sec = 0, clock = null;
let completedSections = new Set();
let reviewData = null;
let lastSessionId = null;
let currentLang = localStorage.getItem('fe_lang') || '';

const LANG_FLAGS = { uz: '🇺🇿', ru: '🇷🇺', en: '🇬🇧' };
const LANG_NAMES = { uz: "O'zbek", ru: 'Русский', en: 'English' };

const UI = {
  uz: {
    start: "Boshlash",
    loading: "Yuklanmoqda...",
    back: "Ortga",
    next: "Keyingi",
    prev: "Oldingi",
    submit: "Topshirish",
    reg_title: "Ro'yxatdan o'tish",
    reg_hint: "Imtihonni boshlash uchun ma'lumotlaringizni kiriting",
    name: "Ism",
    surname: "Familiya",
    teacher: "O'qituvchi",
    teacher_name: "O'qituvchi ismi",
    teacher_surname: "Familiyasi",
    pick_level: "Darajangizni tanlang",
    pick_level_hint: "Mos darajani tanlang va testlarni boshlang",
    pick_month: "Oy tanlang va testlarni boshlang",
    month_stats: "savol",
    word_stats: "so'z",
    exam_submit_confirm: "Imtihonni topshirasizmi?",
    results_title: "Natijalar",
    score_lbl: "Ball",
    correct_lbl: "To'g'ri",
    total_lbl: "Jami",
    time_lbl: "Vaqt",
    new_test: "Boshqa test",
    cert_btn: "Sertifikat",
    calculating: "Natijalarni hisoblayapmiz...",
    wait_hint: "Iltimos kutib turing",
    no_answer: "Javob berilmadi",
    correct_ans: "To'g'ri",
    your_ans: "Javob",
    name_placeholder: "Ismingiz",
    surname_placeholder: "Familiyangiz",
    teacher_name_placeholder: "O'qituvchi ismi",
    teacher_surname_placeholder: "O'qituvchi familiyasi",
    choose_answer: "To'g'ri javobni tanlang:",
    choose_word: "So'z ma'nosini tanlang:",
    translate: "Ingliz tiliga tarjima qiling",
    write_answer: "Javobingizni yozing",
    translate_placeholder: "Tarjimangizni yozing...",
    write_placeholder: "Yozishni boshlang...",
    words_label: "So'zlar",
    submitting: "Yuborilmoqda...",
    error: "Xatolik",
    no_tests: "Bu oy uchun testlar yo'q",
    levels_error: "Darajalar yuklanmadi",
    months_error: "Oylar yuklanmadi",
    questions_error: "Savollar yuklanmadi",
    network_error: "Server bilan bog'lanib bo'lmadi",
    month_label: "oy",
    select_language: "Tilni tanlang",
  },
  ru: {
    start: "Начать",
    loading: "Загрузка...",
    back: "Назад",
    next: "Далее",
    prev: "Назад",
    submit: "Сдать",
    reg_title: "Регистрация",
    reg_hint: "Введите данные для начала экзамена",
    name: "Имя",
    surname: "Фамилия",
    teacher: "Учитель",
    teacher_name: "Имя учителя",
    teacher_surname: "Фамилия",
    pick_level: "Выберите уровень",
    pick_level_hint: "Выберите подходящий уровень и начните тесты",
    pick_month: "Выберите месяц и начните тесты",
    month_stats: "вопр.",
    word_stats: "слов",
    exam_submit_confirm: "Сдать экзамен?",
    results_title: "Результаты",
    score_lbl: "Балл",
    correct_lbl: "Правильно",
    total_lbl: "Всего",
    time_lbl: "Время",
    new_test: "Новый тест",
    cert_btn: "Сертификат",
    calculating: "Результаты рассчитываются...",
    wait_hint: "Пожалуйста, подождите",
    no_answer: "Нет ответа",
    correct_ans: "Правильный",
    your_ans: "Ответ",
    name_placeholder: "Ваше имя",
    surname_placeholder: "Ваша фамилия",
    teacher_name_placeholder: "Имя учителя",
    teacher_surname_placeholder: "Фамилия учителя",
    choose_answer: "Выберите правильный ответ:",
    choose_word: "Выберите значение слова:",
    translate: "Переведите на английский",
    write_answer: "Напишите ответ",
    translate_placeholder: "Напишите перевод...",
    write_placeholder: "Начните писать...",
    words_label: "Слов",
    submitting: "Отправка...",
    error: "Ошибка",
    no_tests: "Для этого месяца тестов нет",
    levels_error: "Уровни не загружены",
    months_error: "Месяцы не загружены",
    questions_error: "Вопросы не загружены",
    network_error: "Ошибка соединения с сервером",
    month_label: "мес.",
    select_language: "Выберите язык",
  },
  en: {
    start: "Start",
    loading: "Loading...",
    back: "Back",
    next: "Next",
    prev: "Previous",
    submit: "Submit",
    reg_title: "Registration",
    reg_hint: "Enter your details to begin the exam",
    name: "First Name",
    surname: "Last Name",
    teacher: "Teacher",
    teacher_name: "Teacher's Name",
    teacher_surname: "Teacher's Surname",
    pick_level: "Choose Your Level",
    pick_level_hint: "Select the appropriate level and start the tests",
    pick_month: "Choose a month and start the tests",
    month_stats: "questions",
    word_stats: "words",
    exam_submit_confirm: "Submit the exam?",
    results_title: "Results",
    score_lbl: "Score",
    correct_lbl: "Correct",
    total_lbl: "Total",
    time_lbl: "Time",
    new_test: "New Test",
    cert_btn: "Certificate",
    calculating: "Calculating results...",
    wait_hint: "Please wait",
    no_answer: "No answer",
    correct_ans: "Correct",
    your_ans: "Answer",
    name_placeholder: "Your first name",
    surname_placeholder: "Your last name",
    teacher_name_placeholder: "Teacher's name",
    teacher_surname_placeholder: "Teacher's surname",
    choose_answer: "Choose the correct answer:",
    choose_word: "Choose the meaning of the word:",
    translate: "Translate into English",
    write_answer: "Write your answer",
    translate_placeholder: "Write your translation...",
    write_placeholder: "Start writing...",
    words_label: "Words",
    submitting: "Submitting...",
    error: "Error",
    no_tests: "No tests available for this month",
    levels_error: "Levels could not be loaded",
    months_error: "Months could not be loaded",
    questions_error: "Questions could not be loaded",
    network_error: "Could not connect to server",
    month_label: "months",
    select_language: "Select language",
  }
};

const $ = id => document.getElementById(id);
const show = el => { el.classList.add('active'); el.removeAttribute('hidden'); };
const hide = el => { el.classList.remove('active'); el.setAttribute('hidden', ''); };
const swap = id => {
  document.querySelectorAll('.scene').forEach(s => s.classList.remove('active'));
  const el = $(id);
  if (el) el.classList.add('active');
};

/* Helper: split bilingual backend text like "English text / Русский текст" */
/* Helper: split bilingual backend text like "English text / Russian text" */
function localizeText(text) {
  if (!text) return '';
  let res = text;
  const parts = text.split(' / ');
  if (parts.length > 1) {
    if (currentLang === 'ru') res = parts[parts.length - 1] || text;
    else res = parts[0] || text;
  }

  if (currentLang === 'en') {
    // 1. Manually translate common phrases from backend
    const translations = {
      "Bolalar uchun boshlang'ich daraja": "Elementary level for children",
      "Bolalar uchun ikkinchi daraja": "Second level for children",
      "Yangi boshlovchilar uchun": "For beginners",
      "Boshlang'ich bilim mustahkamlash": "Strengthening basic knowledge",
      "Boshlang'ich daraja": "Beginner level",
      "Elementary daraja": "Elementary level",
      "Pre-Intermediate daraja": "Pre-Intermediate level",
      "Intermediate daraja": "Intermediate level",
      "Upper-Intermediate daraja": "Upper-Intermediate level",
      "Advanced daraja": "Advanced level",
    };

    const trimmedRes = res.trim();
    if (translations[trimmedRes]) return translations[trimmedRes];

    // 2. Handle specific format for months "1-oy"
    const oyMatch = res.match(/^(\d+)-oy$/i);
    if (oyMatch) return `Month ${oyMatch[1]}`;

    // 3. Fallback replacements
    return res.replace(/daraja/gi, 'Level').replace(/uchun/gi, 'for');
  }

  return res;
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem('fe_lang', lang);
  updateUI();
  // Hide language overlay if it's visible
  const overlay = $('v-lang');
  if (overlay && !overlay.hasAttribute('hidden')) hide(overlay);
  // Update all lang switcher buttons
  updateLangSwitchers();
  saveState();
}

function updateLangSwitchers() {
  document.querySelectorAll('.lang-switcher-current').forEach(el => {
    el.innerHTML = `${LANG_FLAGS[currentLang]} ${LANG_NAMES[currentLang]} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>`;
  });
}

function updateUI() {
  const t = UI[currentLang];
  // Header Info
  const userLbl = $('user-lbl');
  if (userLbl) userLbl.textContent = studentName || '';
  const examBadge = $('exam-badge');
  if (examBadge && currentLevel && currentMonth) {
    const monthLabel = localizeText(currentMonth.name) || `${currentMonth.number}-${t.month_label}`;
    examBadge.textContent = `${localizeText(currentLevel.name)} — ${monthLabel}`;
  }

  // Registration
  const vReg = document.querySelector('#v-register');
  if (vReg) {
    vReg.querySelector('h2').innerHTML = t.reg_title;
    vReg.querySelector('.form-hint').innerHTML = t.reg_hint;
  }
  document.querySelector('label[for=inp-first]').innerText = t.name;
  document.querySelector('label[for=inp-last]').innerText = t.surname;
  document.querySelector('label[for=inp-tfirst]').innerText = t.teacher_name;
  document.querySelector('label[for=inp-tlast]').innerText = t.teacher_surname;
  document.querySelector('.form-sep').innerHTML = t.teacher;
  $('inp-first').placeholder = t.name_placeholder;
  $('inp-last').placeholder = t.surname_placeholder;
  $('inp-tfirst').placeholder = t.teacher_name_placeholder;
  $('inp-tlast').placeholder = t.teacher_surname_placeholder;
  const regBtn = $('btn-register');
  const regSpan = regBtn.querySelector('span');
  if (regSpan) regSpan.innerText = t.start;

  // Levels
  document.querySelector('#v-levels h1').innerText = t.pick_level;
  document.querySelector('#v-levels p').innerText = t.pick_level_hint;
  $('btn-back-levels').innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7" /></svg> ${t.back}`;

  // Months
  document.querySelector('#v-months p').innerText = t.pick_month;

  // Exam
  $('nav-prev').innerText = `← ${t.prev}`;
  $('nav-next').innerText = `${t.next} →`;
  $('nav-submit').innerText = t.submit;

  // Results
  document.querySelector('#v-results h1').innerText = t.results_title;
  $('ring').querySelector('.ring-lbl').innerText = t.score_lbl;
  document.querySelector('#rs-correct').nextElementSibling.innerText = t.correct_lbl;
  document.querySelector('#rs-total').nextElementSibling.innerText = t.total_lbl;
  document.querySelector('#rs-time').nextElementSibling.innerText = t.time_lbl;
  $('btn-cert').innerText = `📄 ${t.cert_btn}`;
  document.querySelector('button[onclick="location.reload()"]').innerText = t.new_test;

  // Loading
  const vLoad = $('v-loading-res');
  if (vLoad) {
    vLoad.querySelector('h3').innerText = t.calculating;
    vLoad.querySelector('p').innerText = t.wait_hint;
  }

  // Re-render current scene content if necessary
  const activeScene = document.querySelector('.scene.active')?.id;
  if (activeScene === 'v-levels' && levels.length > 0) renderLevels();
  if (activeScene === 'v-months' && months.length > 0) renderMonths(currentLevelInfo, months);
  if (activeScene === 'v-exam' && qs.length > 0) go(qi);
}

/* ═══ Boot ═══ */
document.addEventListener('DOMContentLoaded', () => {
  // No language overlay — default to 'uz' if not saved
  if (!currentLang || !UI[currentLang]) {
    currentLang = 'uz';
    localStorage.setItem('fe_lang', 'uz');
  }
  // Always hide overlay (it's not needed anymore)
  const langOverlay = $('v-lang');
  if (langOverlay) hide(langOverlay);

  initLangSwitchers();
  loadState();

  const inps = ['inp-first', 'inp-last', 'inp-tfirst', 'inp-tlast'].map(id => $(id));
  const checkForm = () => {
    $('btn-register').disabled = !inps.every(i => i && i.value.trim().length >= 2);
  };
  inps.forEach(i => i && i.addEventListener('input', checkForm));
  $('btn-register').addEventListener('click', doRegister);
  $('btn-back-levels').addEventListener('click', () => {
    swap('v-levels');
    saveState();
  });
  $('nav-next').addEventListener('click', handleNext);
  $('nav-prev').addEventListener('click', () => { if (qi > 0) go(qi - 1); });
  $('nav-submit').addEventListener('click', () => {
    if (confirm(UI[currentLang].exam_submit_confirm)) submitExam();
  });
});

function initLangSwitchers() {
  // Setup lang switcher dropdowns
  document.querySelectorAll('.lang-switcher').forEach(sw => {
    const btn = sw.querySelector('.lang-switcher-current');
    const menu = sw.querySelector('.lang-switcher-menu');
    if (!btn || !menu) return;
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Close all other open menus
      document.querySelectorAll('.lang-switcher-menu.open').forEach(m => {
        if (m !== menu) m.classList.remove('open');
      });
      menu.classList.toggle('open');
    });
    menu.querySelectorAll('button').forEach(langBtn => {
      langBtn.addEventListener('click', () => {
        setLang(langBtn.dataset.lang);
        menu.classList.remove('open');
      });
    });
  });

  // Close menus when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('.lang-switcher-menu.open').forEach(m => m.classList.remove('open'));
  });
}

function saveState() {
  const currentScene = document.querySelector('.scene.active')?.id || 'v-register';
  // Don't save if it's the loading or results screen (usually better to reset or stay)
  if (currentScene === 'v-loading-res' || currentScene === 'v-results') return;

  const state = {
    scene: currentScene,
    studentName,
    currentLevel,
    currentMonth,
    qs,
    ans,
    qi,
    sec,
    cats,
    completedSections: Array.from(completedSections || [])
  };
  localStorage.setItem('fe_state', JSON.stringify(state));
}

function startTimer() {
  if (clock) clearInterval(clock);
  clock = setInterval(() => {
    sec++;
    $('timer-t').textContent =
      `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
    saveState(); // Save time progress
  }, 1000);
}

async function loadState() {
  const saved = localStorage.getItem('fe_state');
  if (!saved) {
    updateUI();
    updateLangSwitchers();
    return;
  }

  try {
    const s = JSON.parse(saved);
    studentName = s.studentName;
    currentLevel = s.currentLevel;
    currentMonth = s.currentMonth;
    qs = s.qs || [];
    ans = s.ans || {};
    qi = s.qi || 0;
    sec = s.sec || 0;
    cats = s.cats || [];
    completedSections = new Set(s.completedSections || []);

    updateUI();
    updateLangSwitchers();

    if (s.scene === 'v-exam' && qs.length > 0) {
      swap('v-exam');
      buildDots();
      go(qi);
      startTimer();
    } else if (s.scene === 'v-months' && currentLevel) {
      // Re-fetch months to ensure data is fresh
      await loadMonths(currentLevel);
    } else if (s.scene === 'v-levels' && studentName) {
      // Re-fetch levels to ensure data is fresh
      await loadLevels();
    } else {
      swap(s.scene || 'v-register');
    }
  } catch (e) {
    console.error("Failed to load state", e);
    localStorage.removeItem('fe_state'); // Clear corrupted state
    updateUI();
    updateLangSwitchers();
    swap('v-register'); // Go to registration on error
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const mc = $('modal-close');
  if (mc) mc.addEventListener('click', () => hide($('review-modal')));
});

/* ═══ 1. Register ═══ */
async function doRegister() {
  const body = {
    first_name: $('inp-first').value.trim(),
    last_name: $('inp-last').value.trim(),
    teacher_first_name: $('inp-tfirst').value.trim(),
    teacher_last_name: $('inp-tlast').value.trim(),
  };
  try {
    $('btn-register').disabled = true;
    $('btn-register').textContent = UI[currentLang].loading;
    const resp = await fetch(`${API}/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const text = await resp.text();
    let r;
    try { r = JSON.parse(text); } catch { r = { success: false, error: 'Server error' }; }
    if (r.success) {
      studentId = r.student_id;
      studentName = r.student_name;
      teacherName = r.teacher_name;
      saveState();
      await loadLevels();
    } else {
      alert(r.error || UI[currentLang].error);
      $('btn-register').disabled = false;
      $('btn-register').querySelector('span').innerText = UI[currentLang].start;
    }
  } catch (e) {
    alert(UI[currentLang].network_error);
    $('btn-register').disabled = false;
    $('btn-register').innerHTML = UI[currentLang].start;
  }
}

/* ═══ 2. Levels ═══ */
async function loadLevels() {
  try {
    const r = await (await fetch(`${API}/levels/`)).json();
    levels = r.levels || [];
    renderLevels();
    swap('v-levels');
    $('nav-user').textContent = studentName;
    saveState();
  } catch {
    alert(UI[currentLang].levels_error);
  }
}

function renderLevels() {
  const grid = $('levels-grid');
  grid.innerHTML = '';
  levels.forEach((lv, i) => {
    const card = document.createElement('div');
    card.className = 'level-card';
    card.style.animationDelay = `${i * .06}s`;
    const imgSrc = lv.image_url || `/static/images/levels/${lv.slug}.jpg`;
    card.innerHTML = `
      <div class="lc-img-wrap">
        <img class="lc-img" src="${imgSrc}" alt="${lv.name}" loading="lazy"
             onerror="this.style.display='none'">
        <div class="lc-badge">${lv.icon}</div>
      </div>
      <div class="lc-body">
        <div class="lc-name">${localizeText(lv.name)}</div>
        <div class="lc-desc">${localizeText(lv.description)}</div>
        <div class="lc-footer">
          <span class="lc-meta">${lv.month_count} ${UI[currentLang].month_label}</span>
          <span class="lc-arrow">&rarr;</span>
        </div>
      </div>
    `;
    card.addEventListener('click', () => loadMonths(lv));
    grid.appendChild(card);
  });
}

/* ═══ 3. Months ═══ */
async function loadMonths(level) {
  currentLevel = level;
  try {
    const r = await (await fetch(`${API}/levels/${level.slug}/months/`)).json();
    if (!r.success) { alert(UI[currentLang].months_error); return; }
    months = r.months || [];
    currentLevelInfo = r.level;
    renderMonths(currentLevelInfo, months);
    swap('v-months');
    $('nav-user2').textContent = studentName;
    saveState();
  } catch {
    alert(UI[currentLang].months_error);
  }
}

function renderMonths(levelInfo, months) {
  $('month-level-name').textContent = levelInfo.name;
  $('month-icon').textContent = currentLevel.icon;
  $('month-icon').style.background = currentLevel.color + '15';

  const grid = $('months-grid');
  grid.innerHTML = '';
  months.forEach((m, i) => {
    const card = document.createElement('div');
    card.className = 'month-card';
    card.style.animationDelay = `${i * .08}s`;
    card.innerHTML = `
      <div class="mc-num">${m.number}</div>
      <div class="mc-name">${localizeText(m.name)}</div>
      <div class="mc-stats">
        <span><b>${m.question_count}</b> ${UI[currentLang].month_stats}</span>
        <span><b>${m.vocab_count}</b> ${UI[currentLang].word_stats}</span>
      </div>
      <div class="mc-btn">${UI[currentLang].start}</div>
    `;
    card.addEventListener('click', () => startExam(m));
    grid.appendChild(card);
  });
}

/* ═══ 4. Start Exam ═══ */
async function startExam(month) {
  currentMonth = month;
  try {
    const r = await (await fetch(
      `${API}/levels/${currentLevel.slug}/months/${month.number}/questions/`
    )).json();
    if (!r.success || !r.questions.length) {
      alert(UI[currentLang].no_tests);
      return;
    }
    cats = r.categories || [];
    qs = r.questions;
    ans = {};
    qi = 0;
    sec = 0;
    completedSections = new Set();
    reviewData = null;

    swap('v-exam');
    const monthLabel = localizeText(month.name) || `${month.number}-${UI[currentLang].month_label}`;
    $('exam-badge').textContent = `${currentLevel.name} — ${monthLabel}`;
    $('user-lbl').textContent = studentName;
    buildDots();
    go(0);

    startTimer();
    saveState();
  } catch {
    alert(UI[currentLang].questions_error);
  }
}

/* ═══ Dots ═══ */
function buildDots() {
  const w = $('dots-bar');
  w.innerHTML = '';
  const curCat = qs[qi]?.category;
  if (!curCat) return;
  const sqs = qs.filter(q => q.category === curCat);
  sqs.forEach((q, i) => {
    const gi = qs.indexOf(q);
    const d = document.createElement('button');
    d.className = 'dot';
    d.textContent = i + 1;
    d.onclick = () => go(gi);
    w.appendChild(d);
  });
}

function syncDots() {
  const curCat = qs[qi]?.category;
  if (!curCat) return;
  const sqs = qs.filter(q => q.category === curCat);
  const dots = $('dots-bar').querySelectorAll('.dot');
  sqs.forEach((q, i) => {
    if (!dots[i]) return;
    const gi = qs.indexOf(q);
    const k = String(q.id);
    dots[i].className = 'dot';
    if (gi === qi) dots[i].classList.add('now');
    else if (ans[k] !== undefined && ans[k] !== '') dots[i].classList.add('done');
  });
}

/* ═══ Handle Next ═══ */
function handleNext() {
  const cur = qs[qi];
  const ni = qi + 1;
  if (ni >= qs.length) return;
  const nxt = qs[ni];

  if (cur.category !== nxt.category) {
    // completedSections.add(cur.category); // Option to skip overlay
    // showSectionComplete(cur.category_name, nxt);
    go(ni);
  } else {
    go(ni);
  }
}

function showSectionComplete(catName, nextQ) {
  const overlay = document.createElement('div');
  overlay.className = 'section-done-overlay';

  let listHtml = '';
  const allCats = [...new Set(qs.map(q => q.category))];
  allCats.forEach(slug => {
    const name = qs.find(q => q.category === slug)?.category_name || slug;
    const done = completedSections.has(slug);
    listHtml += `<div class="sd-item ${done ? 'done' : ''}">
      <span class="sd-icon">${done ? '&#10003;' : '&#9675;'}</span> ${name}
    </div>`;
  });

  overlay.innerHTML = `
    <div class="section-done-card">
      <h2>${catName} — ${currentLang === 'en' ? 'completed!' : currentLang === 'ru' ? 'завершён!' : 'tugadi!'}</h2>
      <p>${currentLang === 'en' ? 'Continue to the next section?' : currentLang === 'ru' ? 'Перейти к следующему разделу?' : "Keyingi bo'limga o'tamizmi?"}</p>
      <div class="sd-list">${listHtml}</div>
      <button class="btn-primary" id="sd-continue">${currentLang === 'en' ? 'Continue' : currentLang === 'ru' ? 'Продолжить' : 'Davom etish'}</button>
    </div>
  `;

  document.body.appendChild(overlay);
  overlay.querySelector('#sd-continue').addEventListener('click', () => {
    overlay.remove();
    const ni = qs.indexOf(nextQ);
    if (ni >= 0) {
      buildDots();
      go(ni);
      saveState();
    }
  });
}

/* ═══ Render Question ═══ */
function go(i) {
  if (i < 0 || i >= qs.length) return;

  if (qs[qi] && qs[i] && qs[qi].category !== qs[i].category) {
    buildDots();
  }

  qi = i;
  saveState();
  const q = qs[i], k = String(q.id);
  const cqs = qs.filter(x => x.category === q.category);
  const pos = cqs.indexOf(q) + 1;
  const isLastInSection = pos === cqs.length;
  const isLastOverall = i === qs.length - 1;

  $('q-tag').textContent = q.category_name;
  $('q-num').textContent = `${pos} / ${cqs.length}`;
  $('bar-fill').style.width = `${((i + 1) / qs.length) * 100}%`;

  $('nav-prev').disabled = pos === 1;

  const navNext = $('nav-next');
  const navSubmit = $('nav-submit');

  if (isLastOverall || q.question_type === 'writing') {
    navNext.hidden = true;
    navNext.style.display = 'none';
    navSubmit.hidden = false;
    navSubmit.style.display = 'inline-block';
  } else {
    navNext.hidden = false;
    navNext.style.display = 'inline-block';
    navNext.textContent = `${UI[currentLang].next} \u2192`;
    navSubmit.hidden = true;
    navSubmit.style.display = 'none';
  }

  const body = $('q-body');
  body.innerHTML = '';

  if (q.question_type === 'multiple_choice') {
    $('q-sub').textContent = UI[currentLang].choose_answer;
    $('q-title').textContent = q.question_text;
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'vocabulary') {
    $('q-sub').textContent = UI[currentLang].choose_word;
    $('q-title').textContent = '';
    const vw = document.createElement('div');
    vw.className = 'v-word';
    vw.innerHTML = `<h3>${q.question_text}</h3>`;
    body.appendChild(vw);
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'translation') {
    $('q-sub').textContent = localizeText(q.instructions) || UI[currentLang].translate;
    $('q-title').textContent = '';
    const s = document.createElement('div');
    s.className = 't-source';
    s.innerHTML = `<p>${q.question_text}</p>`;
    body.appendChild(s);
    body.appendChild(makeTa(k, 3, UI[currentLang].translate_placeholder));
  } else if (q.question_type === 'writing') {
    $('q-sub').textContent = localizeText(q.instructions) || UI[currentLang].write_answer;
    $('q-title').textContent = q.question_text;
    body.appendChild(makeTa(k, 10, UI[currentLang].write_placeholder, true));
    const bar = document.createElement('div');
    bar.className = 'wbar';
    bar.innerHTML = `${UI[currentLang].words_label}: <b id="wc">${countW(ans[k] || '')}</b> / ${q.min_words} min`;
    body.appendChild(bar);
  }

  const curDots = $('dots-bar').querySelectorAll('.dot');
  if (curDots.length !== cqs.length) buildDots();

  syncDots();
  $('q-card').style.animation = 'none';
  void $('q-card').offsetWidth;
  $('q-card').style.animation = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function makeOpts(q, k) {
  const saved = ans[k];
  const d = document.createElement('div');
  d.className = 'opts';
  (q.options || []).forEach((o, oi) => {
    const el = document.createElement('div');
    el.className = 'opt' + (saved === oi ? ' picked' : '');
    const rid = `q${q.id}_o${oi}`;
    el.innerHTML = `<input type="radio" name="qr_${q.id}" id="${rid}" value="${oi}" ${saved === oi ? 'checked' : ''}>
      <label for="${rid}">${o}</label>`;
    el.addEventListener('click', () => {
      ans[k] = oi;
      d.querySelectorAll('.opt').forEach(x => x.classList.remove('picked'));
      el.classList.add('picked');
      el.querySelector('input').checked = true;
      syncDots();
      saveState();
    });
    d.appendChild(el);
  });
  return d;
}

let aiCheckTimer = null;
function makeTa(k, rows, ph, big) {
  const wrap = document.createElement('div');
  const ta = document.createElement('textarea');
  ta.className = 'ta' + (big ? ' big' : '');
  ta.rows = rows;
  ta.placeholder = ph;
  ta.value = ans[k] || '';

  const aiTag = document.createElement('div');
  aiTag.className = 'ai-indicator';
  aiTag.id = `ai-tag-${k}`;
  aiTag.hidden = true;

  ta.addEventListener('input', () => {
    ans[k] = ta.value;
    const wc = $('wc');
    if (wc) wc.textContent = countW(ta.value);
    syncDots();
    saveState();

    clearTimeout(aiCheckTimer);
    if (ta.value.trim().length > 40) {
      aiCheckTimer = setTimeout(() => runAiCheck(ta.value, aiTag), 800);
    } else {
      aiTag.hidden = true;
    }
  });

  wrap.appendChild(ta);
  wrap.appendChild(aiTag);
  return wrap;
}

async function runAiCheck(text, tag) {
  try {
    const r = await (await fetch(`${API}/check-ai/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })).json();
    if (r.success && r.score > 0) {
      tag.hidden = false;
      const cls = r.score >= 70 ? 'ai-high' : r.score >= 40 ? 'ai-mid' : 'ai-low';
      tag.className = `ai-indicator ${cls}`;
      tag.innerHTML = `<span class="ai-icon">${r.score >= 40 ? '&#9888;' : '&#10003;'}</span>
        <span>${r.label} (${r.score}%)</span>
        ${r.reasons.length ? '<span class="ai-detail">' + r.reasons.join(', ') + '</span>' : ''}`;
    } else {
      tag.hidden = true;
    }
  } catch { tag.hidden = true; }
}

function countW(t) { return t.trim().split(/\s+/).filter(w => w).length; }

/* ═══ Submit ═══ */
async function submitExam() {
  if (!confirm(UI[currentLang].exam_submit_confirm)) return;
  $('nav-submit').disabled = true;
  $('nav-submit').textContent = UI[currentLang].submitting;
  try {
    const r = await (await fetch(`${API}/submit-exam/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        level_slug: currentLevel.slug,
        month_number: currentMonth.number,
        answers: ans,
      }),
    })).json();
    if (r.success) {
      clearInterval(clock);
      reviewData = r.review || [];
      lastSessionId = r.session_id || null;

      // SHOW ANIMATION FOR 2 SECONDS
      hide($('v-exam'));
      show($('v-loading-res'));

      let progress = 0;
      const duration = 2000; // 2 seconds total
      const interval = 20;   // Update every 20ms
      const steps = duration / interval;
      const increment = 100 / steps;

      const counter = setInterval(() => {
        progress += increment;
        if (progress >= 100) {
          progress = 100;
          clearInterval(counter);
          setTimeout(() => {
            hide($('v-loading-res'));
            localStorage.removeItem('fe_state');
            showResults(r);
          }, 200); // 0.2s pause at 100%
        }
        $('rl-pct').textContent = Math.round(progress) + '%';
      }, interval);
    } else {
      alert(UI[currentLang].error + ': ' + (r.error || ''));
      $('nav-submit').disabled = false;
      $('nav-submit').textContent = UI[currentLang].submit;
    }
  } catch {
    alert(UI[currentLang].network_error);
    $('nav-submit').disabled = false;
    $('nav-submit').textContent = UI[currentLang].submit;
  }
}

/* ═══ Results ═══ */
function showResults(d) {
  swap('v-results');
  const monthLabel = localizeText(currentMonth.name) || `${currentMonth.number}-${UI[currentLang].month_label}`;
  $('res-name').textContent = `${studentName} — ${currentLevel.name} / ${monthLabel}`;

  const s = d.score || {};
  const correct = s.correct || 0, total = s.total || 0;
  const pct = total > 0 ? Math.round(correct / total * 100) : 0;

  $('ring-val').textContent = pct + '%';
  $('ring').style.setProperty('--p', pct + '%');
  $('rs-correct').textContent = correct;
  $('rs-total').textContent = total;
  $('rs-time').textContent =
    `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;

  const tabs = $('review-tabs');
  tabs.innerHTML = '';
  const area = $('review-area');
  area.innerHTML = '';

  const catSlugs = [...new Set((reviewData || []).map(r => r.category))];
  let activeTab = catSlugs[0] || null;

  function renderSection(slug) {
    activeTab = slug;
    tabs.querySelectorAll('.rev-tab').forEach(t => t.classList.remove('active'));
    const activeBtn = tabs.querySelector(`[data-cat="${slug}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    area.innerHTML = '';
    const items = reviewData.filter(r => r.category === slug);
    items.forEach((item, i) => {
      const ok = item.isCorrect === true;
      const bad = item.isCorrect === false;
      const div = document.createElement('div');
      div.className = 'rev-item' + (ok ? ' correct' : bad ? ' wrong' : '');

      let icon = '';
      if (ok) icon = '<div class="rev-icon ok">&#10003;</div>';
      else if (bad) icon = '<div class="rev-icon bad">&#10007;</div>';
      else icon = '<div class="rev-icon na">&mdash;</div>';

      let ansHtml = '';
      if (item.questionType === 'multiple_choice' || item.questionType === 'vocabulary') {
        ansHtml = `<p class="rev-ans"><b>${UI[currentLang].your_ans}:</b> <span class="${ok ? 'rev-ok' : 'rev-your'}">${item.yourAnswer || UI[currentLang].no_answer}</span></p>`;
        if (!ok) {
          ansHtml += `<p class="rev-ans"><b>${UI[currentLang].correct_ans}:</b> <span class="rev-ok">${item.correctAnswer || ''}</span></p>`;
        }
      } else {
        const fullText = item.yourAnswer || UI[currentLang].no_answer;
        ansHtml = `<p class="rev-ans"><b>${UI[currentLang].your_ans}:</b> <span style="color:var(--g700)">${fullText}</span></p>`;
        if (item.aiCheck && item.aiCheck.score >= 40) {
          const ac = item.aiCheck;
          const acCls = ac.score >= 70 ? 'ai-high' : 'ai-mid';
          ansHtml += `<div class="ai-badge ${acCls}">&#9888; ${ac.label} (${ac.score}%)${ac.reasons.length ? ' — ' + ac.reasons.join(', ') : ''}</div>`;
        }
      }

      div.innerHTML = `
        <div class="rev-head">${icon}<span class="rev-q">${i + 1}. ${item.questionText}</span></div>
        ${ansHtml}
      `;
      area.appendChild(div);
    });
  }

  catSlugs.forEach((slug, idx) => {
    const items = reviewData.filter(r => r.category === slug);
    if (!items.length) return;
    const name = items[0].categoryName;
    const correctCount = items.filter(r => r.isCorrect === true).length;
    const totalCount = items.filter(r => r.isCorrect !== null && r.isCorrect !== undefined).length;

    const btn = document.createElement('button');
    btn.className = 'rev-tab' + (idx === 0 ? ' active' : '');
    btn.setAttribute('data-cat', slug);
    btn.innerHTML = `${name} <span class="rev-tab-score">${totalCount > 0 ? correctCount + '/' + totalCount : ''}</span>`;
    btn.addEventListener('click', () => renderSection(slug));
    tabs.appendChild(btn);
  });

  if (activeTab) renderSection(activeTab);
}

function openCert() {
  if (lastSessionId) {
    window.open(`/certificate/${lastSessionId}/`, '_blank');
  }
}
