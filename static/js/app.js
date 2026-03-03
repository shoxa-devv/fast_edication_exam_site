/* ═══════════════════════════════════════════
   Fast Education — SPA Engine
   Flow: Register → Levels → Months → Exam → Results
   ═══════════════════════════════════════════ */
const API = '/api';
let studentId = null, studentName = '', teacherName = '';
let levels = [], currentLevel = null, currentMonth = null;
let cats = [], qs = [], ans = {};
let qi = 0, sec = 0, clock = null;
let completedSections = new Set();
let reviewData = null;
let lastSessionId = null;

const $ = id => document.getElementById(id);
const show = el => { el.classList.add('active'); el.removeAttribute('hidden'); };
const hide = el => { el.classList.remove('active'); el.setAttribute('hidden', ''); };
const swap = id => {
  document.querySelectorAll('.scene').forEach(s => s.classList.remove('active'));
  const el = $(id);
  if (el) el.classList.add('active');
};

/* ═══ Boot ═══ */
document.addEventListener('DOMContentLoaded', () => {
  const inps = ['inp-first', 'inp-last', 'inp-tfirst', 'inp-tlast'].map(id => $(id));
  const checkForm = () => {
    $('btn-register').disabled = !inps.every(i => i.value.trim().length >= 2);
  };
  inps.forEach(i => {
    i.addEventListener('input', checkForm);
    i.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !$('btn-register').disabled) doRegister();
    });
  });
  $('btn-register').addEventListener('click', doRegister);
  $('btn-back-levels').addEventListener('click', () => swap('v-levels'));
  $('nav-prev').addEventListener('click', () => go(qi - 1));
  $('nav-next').addEventListener('click', handleNext);
  $('nav-submit').addEventListener('click', submitExam);
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
    $('btn-register').textContent = 'Yuklanmoqda... / Загрузка...';
    const resp = await fetch(`${API}/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const text = await resp.text();
    let r;
    try { r = JSON.parse(text); } catch { r = { success: false, error: 'Server javob bermadi. BACKEND_URL o\'rnatilganmi? Netlify → Site configuration → Environment variables → BACKEND_URL = Django sayt manzili.' }; }
    if (r.success) {
      studentId = r.student_id;
      studentName = r.student_name;
      teacherName = r.teacher_name;
      await loadLevels();
    } else {
      alert(r.error || 'Xatolik yuz berdi / Произошла ошибка');
      $('btn-register').disabled = false;
      $('btn-register').innerHTML = "Boshlash / Начать";
    }
  } catch (e) {
    alert('Server bilan bog\'lanib bo\'lmadi / Ошибка соединения.\n\nNetlify: BACKEND_URL o\'rnating (Django sayt manzili).\nYoki Django backendni Railway/Render da ishga tushiring.');
    $('btn-register').disabled = false;
    $('btn-register').innerHTML = "Boshlash / Начать";
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
  } catch {
    alert('Darajalar yuklanmadi / Уровни не загружены');
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
        <div class="lc-name">${lv.name}</div>
        <div class="lc-desc">${lv.description || ''}</div>
        <div class="lc-footer">
          <span class="lc-meta">${lv.month_count} oy / мес.</span>
          <span class="lc-arrow">&rarr;</span>
        </div>
      </div>
    `;
    card.addEventListener('click', () => loadMonths(lv));
    grid.appendChild(card);
  });
}

/* ═══ 3. Months ═══ */
async function loadMonths(lv) {
  currentLevel = lv;
  try {
    const r = await (await fetch(`${API}/levels/${lv.slug}/months/`)).json();
    if (!r.success) { alert('Oylar yuklanmadi / Месяцы не загружены'); return; }
    renderMonths(r.level, r.months);
    swap('v-months');
    $('nav-user2').textContent = studentName;
  } catch {
    alert('Oylar yuklanmadi / Месяцы не загружены');
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
      <div class="mc-name">${m.name}</div>
      <div class="mc-stats">
        <span><b>${m.question_count}</b> savol / вопр.</span>
        <span><b>${m.vocab_count}</b> so'z / слов</span>
      </div>
      <div class="mc-btn">Boshlash / Начать</div>
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
      alert("Bu oy uchun testlar yo'q / Для этого месяца тестов нет");
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
    $('exam-badge').textContent = `${currentLevel.name} — ${month.name}`;
    $('user-lbl').textContent = studentName;
    buildDots();
    go(0);

    if (clock) clearInterval(clock);
    clock = setInterval(() => {
      sec++;
      $('timer-t').textContent =
        `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
    }, 1000);
  } catch {
    alert('Savollar yuklanmadi / Вопросы не загружены');
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
    completedSections.add(cur.category);
    showSectionComplete(cur.category_name, nxt);
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
      <h2>${catName} — tugadi! / завершён!</h2>
      <p>Keyingi bo'limga o'tamizmi? / Перейти к следующему разделу?</p>
      <div class="sd-list">${listHtml}</div>
      <button class="btn-primary" id="sd-continue">Davom etish / Продолжить</button>
    </div>
  `;

  document.body.appendChild(overlay);
  overlay.querySelector('#sd-continue').addEventListener('click', () => {
    overlay.remove();
    const ni = qs.indexOf(nextQ);
    if (ni >= 0) {
      buildDots();
      go(ni);
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
  const q = qs[i], k = String(q.id);
  const cqs = qs.filter(x => x.category === q.category);
  const pos = cqs.indexOf(q) + 1;
  const isLastInSection = pos === cqs.length;
  const isLastOverall = i === qs.length - 1;

  $('q-tag').textContent = q.category_name;
  $('q-num').textContent = `${pos} / ${cqs.length}`;
  $('bar-fill').style.width = `${((i + 1) / qs.length) * 100}%`;

  $('nav-prev').disabled = pos === 1;

  if (isLastOverall) {
    $('nav-next').hidden = true;
    $('nav-submit').hidden = false;
  } else if (isLastInSection) {
    $('nav-next').hidden = false;
    $('nav-next').textContent = "Tugatish / Завершить \u2192";
    $('nav-submit').hidden = true;
  } else {
    $('nav-next').hidden = false;
    $('nav-next').textContent = 'Keyingi / Далее \u2192';
    $('nav-submit').hidden = true;
  }

  const body = $('q-body');
  body.innerHTML = '';

  if (q.question_type === 'multiple_choice') {
    $('q-sub').textContent = 'To\'g\'ri javobni tanlang / Выберите правильный ответ:';
    $('q-title').textContent = q.question_text;
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'vocabulary') {
    $('q-sub').textContent = "So'z ma'nosini tanlang / Выберите значение слова:";
    $('q-title').textContent = '';
    const vw = document.createElement('div');
    vw.className = 'v-word';
    vw.innerHTML = `<h3>${q.question_text}</h3>`;
    body.appendChild(vw);
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'translation') {
    $('q-sub').textContent = (q.instructions || 'Ingliz tiliga tarjima qiling') + ' / Переведите на английский';
    $('q-title').textContent = '';
    const s = document.createElement('div');
    s.className = 't-source';
    s.innerHTML = `<p>${q.question_text}</p>`;
    body.appendChild(s);
    body.appendChild(makeTa(k, 3, 'Tarjimangizni yozing / Напишите перевод...'));
  } else if (q.question_type === 'writing') {
    $('q-sub').textContent = (q.instructions || 'Javobingizni yozing') + ' / Напишите ответ';
    $('q-title').textContent = q.question_text;
    body.appendChild(makeTa(k, 10, 'Yozishni boshlang / Начните писать...', true));
    const bar = document.createElement('div');
    bar.className = 'wbar';
    bar.innerHTML = `So'zlar / Слов: <b id="wc">${countW(ans[k] || '')}</b> / ${q.min_words} min`;
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
  if (!confirm("Imtihonni topshirasizmi? / Сдать экзамен?")) return;
  $('nav-submit').disabled = true;
  $('nav-submit').textContent = 'Yuborilmoqda... / Отправка...';
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
      showResults(r);
    } else {
      alert('Xatolik / Ошибка: ' + (r.error || ''));
      $('nav-submit').disabled = false;
      $('nav-submit').textContent = 'Topshirish / Сдать';
    }
  } catch {
    alert('Tarmoq xatosi / Ошибка сети');
    $('nav-submit').disabled = false;
    $('nav-submit').textContent = 'Topshirish / Сдать';
  }
}

/* ═══ Results ═══ */
function showResults(d) {
  swap('v-results');
  $('res-name').textContent =
    `${studentName} — ${currentLevel.name} / ${currentMonth.name}`;

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
        ansHtml = `<p class="rev-ans"><b>Javob / Ответ:</b> <span class="${ok ? 'rev-ok' : 'rev-your'}">${item.yourAnswer || 'Javob berilmadi / Нет ответа'}</span></p>`;
        if (!ok) {
          ansHtml += `<p class="rev-ans"><b>To'g'ri / Правильный:</b> <span class="rev-ok">${item.correctAnswer || ''}</span></p>`;
        }
      } else {
        const preview = (item.yourAnswer || 'Javob berilmadi / Нет ответа').substring(0, 300);
        ansHtml = `<p class="rev-ans"><b>Javob / Ответ:</b> <span style="color:var(--g700)">${preview}${preview.length >= 300 ? '...' : ''}</span></p>`;
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
