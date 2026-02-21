/* ═══════════════════════════════════════════
   Fast Education — Exam Engine v3
   Section transitions + Detailed review
   ═══════════════════════════════════════════ */
const API = '/api';
let cats = [], qs = [], ans = {}, aiMap = {};
let qi = 0, name = '', sec = 0, clock = null, aiT = {};
let completedSections = new Set();
let currentSectionIdx = 0;
let reviewData = null;

const $ = id => document.getElementById(id);
const show = el => { el.classList.add('on'); el.removeAttribute('hidden'); };
const hide = el => { el.classList.remove('on'); el.setAttribute('hidden',''); };
const swap = id => { document.querySelectorAll('.scene').forEach(s => { s.classList.remove('on'); }); show($(id)); };

const catIcons = {
  grammar:'<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>',
  vocabulary:'<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h10M7 12h10M7 17h6"/></svg>',
  translation:'<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/></svg>',
  writing:'<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>'
};

/* ─── boot ─── */
document.addEventListener('DOMContentLoaded', () => {
  const inp = $('inp-name'), btn = $('btn-go');
  inp.addEventListener('input', () => btn.disabled = inp.value.trim().length < 2);
  inp.addEventListener('keydown', e => { if (e.key === 'Enter' && !btn.disabled) goOverview(); });
  btn.addEventListener('click', goOverview);
  $('btn-begin').addEventListener('click', () => startSection(0));
  $('btn-continue').addEventListener('click', continueNextSection);
  $('nav-prev').addEventListener('click', () => go(qi - 1));
  $('nav-next').addEventListener('click', handleNext);
  $('nav-submit').addEventListener('click', submitExam);
  $('modal-close').addEventListener('click', () => hide($('review-modal')));
});

/* ─── 1 → Overview ─── */
async function goOverview() {
  name = $('inp-name').value.trim();
  try {
    const r1 = await (await fetch(`${API}/categories/`)).json();
    cats = r1.categories || [];
    qs = [];
    for (const c of cats) {
      const r2 = await (await fetch(`${API}/questions/?category=${c.slug}`)).json();
      (r2.questions || []).forEach(q => { q._c = c; qs.push(q); });
    }
  } catch { alert('Failed to load.'); return; }

  buildOverviewList($('ov-list'));
  $('ov-count').textContent = qs.length + ' questions total';
  swap('v-overview');
}

function buildOverviewList(wrap, doneSet) {
  wrap.innerHTML = '';
  cats.forEach(c => {
    const n = qs.filter(q => q._c.slug === c.slug).length;
    const isDone = doneSet && doneSet.has(c.slug);
    const d = document.createElement('div');
    d.className = 'ov-item' + (isDone ? ' sec-done' : '');
    if (isDone) d.className = 'sec-item done';
    else d.className = 'sec-item';
    const icon = isDone ? '✅' : (catIcons[c.slug] ? '' : '○');
    d.innerHTML = `<div class="sec-icon">${isDone ? '✅' : '○'}</div><span>${c.name}</span>`;
    wrap.appendChild(d);
  });
}

/* ─── Section start ─── */
function startSection(idx) {
  currentSectionIdx = idx;
  const sectionQs = getSectionQs(idx);
  
  // Find the global index of first question in this section
  const firstQ = sectionQs[0];
  const globalIdx = qs.indexOf(firstQ);
  
  swap('v-exam');
  $('user-lbl').textContent = name;
  buildDots();
  go(globalIdx);
  
  if (!clock) {
    clock = setInterval(() => {
      sec++;
      $('timer-t').textContent = `${String(Math.floor(sec/60)).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}`;
    }, 1000);
  }
}

function getSectionQs(idx) {
  if (idx >= cats.length) return [];
  return qs.filter(q => q._c.slug === cats[idx].slug);
}

/* ─── Handle Next (with section transition) ─── */
function handleNext() {
  const currentQ = qs[qi];
  const nextIdx = qi + 1;
  
  if (nextIdx >= qs.length) return;
  
  const nextQ = qs[nextIdx];
  
  // If we're moving to a different category → show Section Complete
  if (currentQ._c.slug !== nextQ._c.slug) {
    completedSections.add(currentQ._c.slug);
    showSectionComplete(currentQ._c);
  } else {
    go(nextIdx);
  }
}

function showSectionComplete(finishedCat) {
  $('sec-msg').textContent = `You've finished the ${finishedCat.name} section.`;
  buildOverviewList($('sec-list'), completedSections);
  swap('v-section');
}

function continueNextSection() {
  // Find the next section index
  const nextCatSlug = findNextUnfinishedSection();
  if (!nextCatSlug) {
    // All done — go to last question for submit
    swap('v-exam');
    go(qs.length - 1);
    return;
  }
  
  const nextCatIdx = cats.findIndex(c => c.slug === nextCatSlug);
  startSection(nextCatIdx);
}

function findNextUnfinishedSection() {
  for (const c of cats) {
    if (!completedSections.has(c.slug)) return c.slug;
  }
  return null;
}

/* ─── dots ─── */
function buildDots() {
  const w = $('dots-bar'); w.innerHTML = '';
  // Only show dots for current section
  const currentCat = qs[qi]?._c;
  if (!currentCat) return;
  
  const sectionQs = qs.filter(q => q._c.slug === currentCat.slug);
  sectionQs.forEach((q, i) => {
    const globalIdx = qs.indexOf(q);
    const d = document.createElement('button');
    d.className = 'dot';
    d.textContent = i + 1;
    d.onclick = () => go(globalIdx);
    w.appendChild(d);
  });
}

function syncDots() {
  const currentCat = qs[qi]?._c;
  if (!currentCat) return;
  
  const sectionQs = qs.filter(q => q._c.slug === currentCat.slug);
  const dots = $('dots-bar').querySelectorAll('.dot');
  
  sectionQs.forEach((q, i) => {
    if (!dots[i]) return;
    const globalIdx = qs.indexOf(q);
    const k = `${q._c.slug}_${q.id}`;
    dots[i].className = 'dot';
    if (globalIdx === qi) dots[i].classList.add('now');
    else if (ans[k] !== undefined && ans[k] !== '') dots[i].classList.add('done');
  });
}

/* ─── render question ─── */
function go(i) {
  if (i < 0 || i >= qs.length) return;
  
  // Check if jumping to different section
  if (qs[qi] && qs[i] && qs[qi]._c.slug !== qs[i]._c.slug) {
    buildDots();
  }
  
  qi = i;
  const q = qs[i], c = q._c, k = `${c.slug}_${q.id}`;
  const cqs = qs.filter(x => x._c.slug === c.slug);
  const posInCat = cqs.indexOf(q) + 1;
  const isLastInSection = posInCat === cqs.length;
  const isLastOverall = i === qs.length - 1;
  
  $('q-tag').textContent = `${c.name} · Question ${posInCat} of ${cqs.length}`;
  $('bar-fill').style.width = `${((i+1)/qs.length)*100}%`;
  
  // Nav buttons
  $('nav-prev').disabled = posInCat === 1;
  
  if (isLastOverall) {
    $('nav-next').hidden = true;
    $('nav-submit').hidden = false;
  } else if (isLastInSection) {
    $('nav-next').hidden = false;
    $('nav-next').textContent = 'Finish Section →';
    $('nav-submit').hidden = true;
  } else {
    $('nav-next').hidden = false;
    $('nav-next').textContent = 'Next →';
    $('nav-submit').hidden = true;
  }
  
  const body = $('q-body');
  body.innerHTML = '';

  if (q.question_type === 'multiple_choice') {
    $('q-sub').textContent = 'Choose the best option to complete the sentence:';
    $('q-title').textContent = q.question_text;
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'vocabulary') {
    $('q-sub').textContent = 'Select the correct definition for the word:';
    $('q-title').textContent = '';
    const vw = document.createElement('div'); vw.className = 'vword';
    vw.innerHTML = `<h3>${q.question_text}</h3>`;
    body.appendChild(vw);
    body.appendChild(makeOpts(q, k));
  } else if (q.question_type === 'translation') {
    $('q-sub').textContent = q.instructions || 'Translate to English';
    $('q-title').textContent = '';
    const s = document.createElement('div'); s.className = 'tsrc';
    s.innerHTML = `<p>${q.question_text}</p>`;
    body.appendChild(s);
    body.appendChild(makeTa(k, q, 3, 'Type your translation…'));
  } else if (q.question_type === 'writing') {
    $('q-sub').textContent = q.instructions || 'Write your response';
    $('q-title').textContent = q.question_text;
    if (aiMap[k]?.used) {
      const w = document.createElement('div'); w.className = 'ai-warn';
      w.textContent = '⚠️ AI usage detected.';
      body.appendChild(w);
    }
    body.appendChild(makeTa(k, q, 10, 'Start writing…', true));
    const bar = document.createElement('div'); bar.className = 'wbar';
    bar.innerHTML = `Words: <b id="wc">${countW(ans[k]||'')}</b> / ${q.min_words} min`;
    body.appendChild(bar);
  }

  // Rebuild dots if needed
  if (qi === i) {
    const currentDots = $('dots-bar').querySelectorAll('.dot');
    if (currentDots.length !== cqs.length) buildDots();
  }
  
  syncDots();
  $('q-card').style.animation = 'none'; void $('q-card').offsetWidth; $('q-card').style.animation = '';
  window.scrollTo({top:0,behavior:'smooth'});
}

function makeOpts(q, k) {
  const saved = ans[k];
  const d = document.createElement('div'); d.className = 'opts';
  (q.options||[]).forEach((o, oi) => {
    const el = document.createElement('div');
    el.className = 'opt' + (saved === oi ? ' picked' : '');
    el.innerHTML = `<input type="radio" name="qr" value="${oi}" ${saved===oi?'checked':''}><span>${o}</span>`;
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

function makeTa(k, q, rows, ph, big) {
  const ta = document.createElement('textarea');
  ta.className = 'ta' + (big ? ' big' : '');
  ta.rows = rows; ta.placeholder = ph; ta.value = ans[k] || '';
  ta.addEventListener('input', () => {
    ans[k] = ta.value;
    const wc = $('wc'); if (wc) wc.textContent = countW(ta.value);
    syncDots();
    debAI(k, ta.value, q.id, q._c.slug);
  });
  return ta;
}

function countW(t) { return t.trim().split(/\s+/).filter(w=>w).length; }

/* ─── AI ─── */
function debAI(k, text, qId, cat) { clearTimeout(aiT[k]); aiT[k] = setTimeout(() => doAI(k, text, qId, cat), 1500); }
async function doAI(k, text, qId, cat) {
  if (!text || text.length < 30) return;
  try {
    const r = await (await fetch(`${API}/detect-ai/`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text,questionId:qId,category:cat}) })).json();
    if (r.success && r.ai_used) aiMap[k] = {used:true,text,detection_type:r.detection_type||'generated'};
    else delete aiMap[k];
  } catch {}
}

/* ─── submit ─── */
async function submitExam() {
  if (!confirm('Submit your exam?')) return;
  $('nav-submit').disabled = true;
  try {
    const r = await (await fetch(`${API}/submit-exam/`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({answers:ans, aiUsage:aiMap, categories:cats.map(c=>c.slug), studentName:name})
    })).json();
    if (r.success) { clearInterval(clock); reviewData = r.review || []; showResults(r); }
    else { alert('Failed.'); $('nav-submit').disabled = false; }
  } catch { alert('Network error.'); $('nav-submit').disabled = false; }
}

/* ─── results ─── */
function showResults(d) {
  swap('v-results');
  $('res-name').textContent = name;
  const s = d.score||{};
  const correct = s.correct||0, total = s.total||0;
  const pct = total > 0 ? Math.round(correct/total*100) : 0;
  $('ring-val').textContent = pct+'%';
  $('ring').style.setProperty('--p', pct+'%');
  $('rs-correct').textContent = correct;
  $('rs-total').textContent = total;
  $('rs-time').textContent = `${String(Math.floor(sec/60)).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}`;

  // AI
  const sum = d.aiUsageSummary||{};
  if (Object.keys(sum).length > 0) {
    $('ai-box').removeAttribute('hidden');
    const list = $('ai-list'); list.innerHTML = '';
    const tm = {copy:'📋 Copied',translation:'🌐 AI Translation',generated:'🤖 AI Generated'};
    Object.values(sum).forEach(info => {
      const e = document.createElement('div'); e.className = 'ai-entry';
      e.innerHTML = `<h4>${(info.category||'').charAt(0).toUpperCase()+(info.category||'').slice(1)} — Q${info.questionId}</h4>
        <p class="ai-type">${tm[info.detection_type]||'🤖 AI'}</p>`;
      list.appendChild(e);
    });
  } else {
    $('clean-box').removeAttribute('hidden');
  }

  // Build review tabs
  const tabs = $('review-tabs');
  tabs.innerHTML = '';
  cats.forEach(c => {
    const catReview = (reviewData || []).filter(r => r.category === c.slug);
    if (catReview.length === 0) return;
    const btn = document.createElement('button');
    btn.className = 'rev-tab';
    btn.textContent = `${c.name} Review`;
    btn.addEventListener('click', () => openReview(c, catReview));
    tabs.appendChild(btn);
  });
}

/* ─── Review modal ─── */
function openReview(cat, items) {
  $('modal-title').textContent = `${cat.name} Review for ${name}`;
  $('modal-sub').textContent = 'A detailed review of your answers.';
  
  const body = $('modal-body');
  body.innerHTML = '';
  
  items.forEach((item, i) => {
    const isCorrect = item.isCorrect === true;
    const isWrong = item.isCorrect === false;
    const isManual = item.isCorrect === null;
    
    const div = document.createElement('div');
    div.className = 'rev-item' + (isCorrect ? ' correct' : isWrong ? ' wrong' : '');
    
    let iconHtml = '';
    if (isCorrect) iconHtml = '<div class="rev-icon ok">✓</div>';
    else if (isWrong) iconHtml = '<div class="rev-icon bad">✗</div>';
    else iconHtml = '<div class="rev-icon" style="background:rgba(255,255,255,.06);color:#64748b">—</div>';
    
    let instruction = '';
    if (item.questionType === 'multiple_choice') instruction = 'Choose the correct option';
    else if (item.questionType === 'vocabulary') instruction = 'Choose the correct definition';
    else if (item.questionType === 'translation') instruction = 'Translate to English';
    else if (item.questionType === 'writing') instruction = 'Essay';
    
    let answerHtml = '';
    if (item.questionType === 'multiple_choice' || item.questionType === 'vocabulary') {
      const yourAns = item.yourAnswer || 'No answer';
      const correctAns = item.correctAnswer || '';
      answerHtml = `
        <p class="rev-ans"><b>Your answer:</b> <span class="${isCorrect ? 'rev-correct-text' : 'rev-your'}">${yourAns}</span></p>
        ${!isCorrect ? `<p class="rev-ans"><b>Correct answer:</b> <span class="rev-correct-text">${correctAns}</span></p>` : ''}
      `;
    } else if (item.questionType === 'translation') {
      answerHtml = `<p class="rev-ans"><b>Your answer:</b> <span style="color:#cbd5e1">${item.yourAnswer || 'No answer'}</span></p>`;
    } else if (item.questionType === 'writing') {
      const preview = (item.yourAnswer || 'No answer').substring(0, 150);
      answerHtml = `<p class="rev-ans"><b>Your answer:</b> <span style="color:#cbd5e1">${preview}${preview.length >= 150 ? '…' : ''}</span></p>`;
    }
    
    div.innerHTML = `
      <div class="rev-head">${iconHtml}<span class="rev-q">${i+1}. "${item.questionText}"</span></div>
      <p class="rev-sub">${instruction}</p>
      ${answerHtml}
    `;
    body.appendChild(div);
  });
  
  show($('review-modal'));
}
