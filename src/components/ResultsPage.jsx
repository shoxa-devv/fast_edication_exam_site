import React from 'react'
import { useNavigate } from 'react-router-dom'
import './ResultsPage.css'

function ResultsPage({ results }) {
  const navigate = useNavigate()

  // Check if AI was used in any section
  const aiUsedSections = []
  Object.keys(results.aiUsage || {}).forEach(key => {
    if (results.aiUsage[key]?.used) {
      const [category, questionId] = key.split('_')
      aiUsedSections.push({
        category: category.charAt(0).toUpperCase() + category.slice(1),
        questionId: parseInt(questionId),
        text: results.aiUsage[key].text
      })
    }
  })

  const hasAiUsage = aiUsedSections.length > 0

  const getCategoryName = (category) => {
    const names = {
      grammar: 'Grammar',
      translation: 'Translation',
      writing: 'Writing',
      vocabulary: 'Vocabulary'
    }
    return names[category] || category
  }

  const calculateScore = () => {
    // Simple scoring - in real app, compare with correct answers
    let totalQuestions = 0
    let answeredQuestions = 0
    
    results.categories.forEach(category => {
      Object.keys(results.answers).forEach(key => {
        if (key.startsWith(category)) {
          totalQuestions++
          if (results.answers[key] !== '' && results.answers[key] !== null && results.answers[key] !== undefined) {
            answeredQuestions++
          }
        }
      })
    })
    
    return {
      answered: answeredQuestions,
      total: totalQuestions,
      percentage: totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
    }
  }

  const score = calculateScore()

  return (
    <div className="results-page">
      <div className="results-container">
        <div className="results-header">
          <h1>Exam Results</h1>
          <p className="results-subtitle">Your exam has been completed</p>
        </div>

        <div className="score-section">
          <div className="score-card">
            <div className="score-circle">
              <div className="score-value">{score.percentage}%</div>
              <div className="score-label">Completion</div>
            </div>
            <div className="score-details">
              <p><strong>{score.answered}</strong> questions answered</p>
              <p>out of <strong>{score.total}</strong> total questions</p>
            </div>
          </div>
        </div>

        {hasAiUsage && (
          <div className="ai-usage-section">
            <div className="ai-usage-header">
              <div className="ai-usage-icon">⚠️</div>
              <h2>AI Usage Detected</h2>
            </div>
            <div className="ai-usage-warning">
              <p>
                <strong>AI assistance was detected</strong> in your exam responses. 
                The following sections contain AI-generated or AI-assisted content:
              </p>
            </div>
            
            <div className="ai-usage-list">
              {aiUsedSections.map((section, index) => (
                <div key={index} className="ai-usage-item">
                  <div className="ai-usage-badge">
                    <span className="ai-badge-icon">🤖</span>
                    <span className="ai-badge-text">AI Used</span>
                  </div>
                  <div className="ai-usage-details">
                    <h3>{section.category} - Question {section.questionId}</h3>
                    <div className="ai-usage-preview">
                      <p className="preview-label">Detected AI content:</p>
                      <div className="preview-text">
                        {section.text && section.text.length > 200 
                          ? section.text.substring(0, 200) + '...' 
                          : section.text}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="ai-usage-summary">
              <p>
                <strong>Total sections with AI usage:</strong> {aiUsedSections.length}
              </p>
              <p className="summary-note">
                Note: The use of AI assistance has been recorded and may affect your final grade.
              </p>
            </div>
          </div>
        )}

        {!hasAiUsage && (
          <div className="no-ai-section">
            <div className="no-ai-icon">✅</div>
            <h3>No AI Usage Detected</h3>
            <p>Your exam was completed without AI assistance.</p>
          </div>
        )}

        <div className="results-summary">
          <h3>Exam Summary</h3>
          <div className="summary-grid">
            {results.categories.map((category, index) => {
              const categoryAnswers = Object.keys(results.answers).filter(
                key => key.startsWith(category)
              )
              const answered = categoryAnswers.filter(
                key => results.answers[key] !== '' && 
                       results.answers[key] !== null && 
                       results.answers[key] !== undefined
              ).length
              
              return (
                <div key={index} className="summary-item">
                  <div className="summary-category">{getCategoryName(category)}</div>
                  <div className="summary-progress">
                    <div className="progress-bar-fill" style={{ width: `${(answered / categoryAnswers.length) * 100}%` }}></div>
                  </div>
                  <div className="summary-count">{answered} / {categoryAnswers.length}</div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="results-actions">
          <button onClick={() => navigate('/')} className="retake-button">
            Retake Exam
          </button>
          <button onClick={() => window.print()} className="print-button">
            Print Results
          </button>
        </div>
      </div>
    </div>
  )
}

export default ResultsPage
