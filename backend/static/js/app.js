// API Base URL
const API_BASE_URL = '/api';

// Global state
let categories = [];
let currentCategoryIndex = 0;
let questions = {};
let answers = {};
let aiUsage = {};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
});

async function initializeApp() {
    try {
        // Load categories
        const categoriesResponse = await fetch(`${API_BASE_URL}/categories/`);
        const categoriesData = await categoriesResponse.json();
        categories = categoriesData.categories || [];
        
        // Load questions for each category
        for (const category of categories) {
            const questionsResponse = await fetch(`${API_BASE_URL}/questions/?category=${category.slug}`);
            const questionsData = await questionsResponse.json();
            questions[category.slug] = questionsData.questions || [];
        }
        
        // Hide loading, show exam
        document.getElementById('loading-screen').style.display = 'none';
        document.getElementById('exam-page').style.display = 'block';
        
        // Initialize progress bar
        initializeProgressBar();
        
        // Load first category
        loadCategory(0);
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to load exam. Please refresh the page.');
    }
}

function initializeProgressBar() {
    const progressBar = document.getElementById('progress-bar');
    progressBar.innerHTML = '';
    
    categories.forEach((cat, index) => {
        const step = document.createElement('div');
        step.className = 'progress-step';
        if (index === 0) step.classList.add('active');
        
        step.innerHTML = `
            <div class="step-number">${index + 1}</div>
            <div class="step-label">${cat.name}</div>
        `;
        progressBar.appendChild(step);
    });
}

function loadCategory(index) {
    if (index < 0 || index >= categories.length) return;
    
    currentCategoryIndex = index;
    const category = categories[index];
    
    // Update UI
    document.getElementById('category-title').textContent = category.name;
    document.getElementById('current-category').textContent = index + 1;
    document.getElementById('total-categories').textContent = categories.length;
    
    // Update progress bar
    document.querySelectorAll('.progress-step').forEach((step, i) => {
        step.classList.remove('active', 'completed');
        if (i === index) step.classList.add('active');
        else if (i < index) step.classList.add('completed');
    });
    
    // Update navigation buttons
    document.getElementById('prev-button').disabled = index === 0;
    document.getElementById('next-button').style.display = index === categories.length - 1 ? 'none' : 'block';
    document.getElementById('submit-button').style.display = index === categories.length - 1 ? 'block' : 'none';
    
    // Load questions
    renderQuestions(category.slug);
}

function renderQuestions(categorySlug) {
    const container = document.getElementById('section-container');
    const categoryQuestions = questions[categorySlug] || [];
    
    container.innerHTML = '';
    
    categoryQuestions.forEach((question, qIndex) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card';
        
        const key = `${categorySlug}_${question.id}`;
        const savedAnswer = answers[key];
        const savedAiUsage = aiUsage[key];
        
        if (question.question_type === 'multiple_choice' || question.question_type === 'vocabulary') {
            questionCard.innerHTML = `
                <div class="question-header">
                    <span class="question-number">Question ${qIndex + 1}</span>
                </div>
                <p class="question-text">${question.question_text}</p>
                <div class="options-container">
                    ${question.options.map((option, optIndex) => `
                        <label class="option-label ${savedAnswer === optIndex ? 'selected' : ''}">
                            <input type="radio" name="q_${question.id}" value="${optIndex}" 
                                   ${savedAnswer === optIndex ? 'checked' : ''}
                                   onchange="handleAnswer('${key}', ${optIndex})">
                            <span class="option-text">${option}</span>
                        </label>
                    `).join('')}
                </div>
            `;
        } else if (question.question_type === 'translation') {
            questionCard.innerHTML = `
                <div class="question-header">
                    <span class="question-number">Question ${qIndex + 1}</span>
                </div>
                <p class="question-text" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    ${question.question_text}
                </p>
                <p style="color: #666; margin-bottom: 15px;">${question.instructions}</p>
                <textarea class="translation-input" rows="3" 
                          placeholder="Enter your translation here..."
                          onchange="handleAnswer('${key}', this.value)">${savedAnswer || ''}</textarea>
            `;
        } else if (question.question_type === 'writing') {
            const isAiUsed = savedAiUsage?.used || false;
            questionCard.innerHTML = `
                <div class="question-header">
                    <span class="question-number">Question ${qIndex + 1}</span>
                    ${isAiUsed ? '<span class="ai-badge" style="background: #ff9800; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">AI Detected</span>' : ''}
                </div>
                <h3 style="color: #333; font-size: 20px; margin-bottom: 10px;">${question.question_text}</h3>
                <p style="color: #666; margin-bottom: 20px;">${question.instructions}</p>
                <div class="writing-tools">
                    <button class="ai-assist-button" onclick="handleAiAssist('${key}', ${question.id}, '${question.question_text}')">
                        Get AI Assistance
                    </button>
                    <div style="color: #666; font-size: 14px;">
                        Words: <span id="word-count-${question.id}">0</span> / ${question.min_words} minimum
                    </div>
                </div>
                <textarea class="writing-input" rows="12" 
                          placeholder="Start writing your essay here..."
                          oninput="handleWritingChange('${key}', ${question.id}, this.value)">${savedAnswer || ''}</textarea>
                ${isAiUsed ? '<div class="ai-warning">⚠️ AI assistance has been detected in your writing. This will be reported in your results.</div>' : ''}
            `;
            
            // Update word count
            updateWordCount(question.id, savedAnswer || '');
        }
        
        container.appendChild(questionCard);
    });
}

function handleAnswer(key, value) {
    answers[key] = value;
}

async function handleWritingChange(key, questionId, value) {
    answers[key] = value;
    updateWordCount(questionId, value);
    
    // Detect AI usage
    if (value.length > 50) {
        try {
            const response = await fetch(`${API_BASE_URL}/detect-ai/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: value,
                    questionId: questionId,
                    category: 'writing'
                })
            });
            const result = await response.json();
            if (result.success && result.ai_used) {
                aiUsage[key] = { used: true, text: value };
                // Reload current category to show AI badge
                loadCategory(currentCategoryIndex);
            }
        } catch (error) {
            console.error('AI detection error:', error);
        }
    }
}

function updateWordCount(questionId, text) {
    const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;
    const element = document.getElementById(`word-count-${questionId}`);
    if (element) {
        element.textContent = wordCount;
    }
}

async function handleAiAssist(key, questionId, topic) {
    const currentText = answers[key] || '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai-assist/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: topic,
                currentText: currentText,
                questionId: questionId
            })
        });
        const result = await response.json();
        
        if (result.success) {
            const enhancedText = currentText + (currentText ? '\n\n' : '') + `[AI Enhanced: ${result.suggestion}]`;
            answers[key] = enhancedText;
            aiUsage[key] = { used: true, text: enhancedText };
            
            // Reload to show updated text and AI badge
            loadCategory(currentCategoryIndex);
        }
    } catch (error) {
        console.error('AI assist error:', error);
        alert('Failed to get AI assistance. Please try again.');
    }
}

function nextCategory() {
    if (currentCategoryIndex < categories.length - 1) {
        loadCategory(currentCategoryIndex + 1);
    }
}

function prevCategory() {
    if (currentCategoryIndex > 0) {
        loadCategory(currentCategoryIndex - 1);
    }
}

async function submitExam() {
    if (!confirm('Are you sure you want to submit your exam? You cannot change your answers after submission.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/submit-exam/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                answers: answers,
                aiUsage: aiUsage,
                categories: categories.map(c => c.slug)
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showResults(result);
        } else {
            alert('Failed to submit exam. Please try again.');
        }
    } catch (error) {
        console.error('Submit error:', error);
        alert('Failed to submit exam. Please try again.');
    }
}

function showResults(data) {
    document.getElementById('exam-page').style.display = 'none';
    document.getElementById('results-page').style.display = 'block';
    
    // Calculate scores
    const totalQuestions = Object.keys(answers).length;
    const answeredQuestions = Object.values(answers).filter(a => a !== '' && a !== null && a !== undefined).length;
    const percentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
    
    // Update score display
    document.getElementById('score-percentage').textContent = `${percentage}%`;
    document.getElementById('answered-count').textContent = answeredQuestions;
    document.getElementById('total-questions').textContent = totalQuestions;
    
    // Show AI usage if any
    const aiUsageSummary = data.aiUsageSummary || {};
    const aiCount = Object.keys(aiUsageSummary).length;
    
    if (aiCount > 0) {
        document.getElementById('ai-usage-section').style.display = 'block';
        document.getElementById('no-ai-section').style.display = 'none';
        document.getElementById('ai-count').textContent = aiCount;
        
        const aiList = document.getElementById('ai-usage-list');
        aiList.innerHTML = '';
        
        Object.entries(aiUsageSummary).forEach(([key, info]) => {
            const item = document.createElement('div');
            item.className = 'ai-usage-item';
            item.innerHTML = `
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span style="font-size: 32px;">🤖</span>
                    <div style="flex: 1;">
                        <h3 style="color: #333; margin-bottom: 10px;">${info.category.charAt(0).toUpperCase() + info.category.slice(1)} - Question ${info.questionId}</h3>
                        <p style="color: #666; font-size: 14px;">Confidence: ${(info.confidence * 100).toFixed(1)}%</p>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 13px; color: #666;">
                            ${info.text.substring(0, 200)}${info.text.length > 200 ? '...' : ''}
                        </div>
                    </div>
                </div>
            `;
            aiList.appendChild(item);
        });
    } else {
        document.getElementById('ai-usage-section').style.display = 'none';
        document.getElementById('no-ai-section').style.display = 'block';
    }
}

// Event listeners
document.getElementById('next-button').addEventListener('click', nextCategory);
document.getElementById('prev-button').addEventListener('click', prevCategory);
document.getElementById('submit-button').addEventListener('click', submitExam);
