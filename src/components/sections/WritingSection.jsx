import React, { useState, useRef } from 'react'
import { api } from '../../services/api'
import './SectionStyles.css'

const WRITING_QUESTIONS = [
  {
    id: 1,
    topic: "Describe your favorite hobby",
    instructions: "Write at least 100 words about your favorite hobby. Explain why you enjoy it and what you do.",
    minWords: 100
  },
  {
    id: 2,
    topic: "Write about your future plans",
    instructions: "Describe your plans for the next 5 years. Include your career, education, and personal goals. Write at least 150 words.",
    minWords: 150
  }
]

function WritingSection({ onAnswer, onAiUsage, answers, aiUsage, category }) {
  const [writings, setWritings] = useState(
    WRITING_QUESTIONS.reduce((acc, q) => {
      const key = `${category}_${q.id}`
      if (answers[key] !== undefined) {
        acc[q.id] = answers[key]
      } else {
        acc[q.id] = ''
      }
      return acc
    }, {})
  )

  const [aiAssistActive, setAiAssistActive] = useState({})
  const [aiSuggestions, setAiSuggestions] = useState({})
  const textareaRefs = useRef({})

  const detectAiUsage = async (text, questionId) => {
    // Call Python backend API for AI detection
    if (!text || text.length < 50) {
      return false
    }
    
    try {
      const result = await api.detectAI(text, questionId, category)
      return result.success && result.ai_used
    } catch (error) {
      console.error('AI detection error:', error)
      // Fallback to simple detection if API fails
      return text.includes('[AI Enhanced') || text.includes('[AI Assisted')
    }
  }

  const handleChange = async (questionId, value) => {
    setWritings(prev => ({
      ...prev,
      [questionId]: value
    }))
    onAnswer(questionId, value, category)

    // Detect AI usage in real-time using Python backend
    if (value.length > 50) {
      const isAiUsed = await detectAiUsage(value, questionId)
      onAiUsage(questionId, isAiUsed, value)
    } else {
      onAiUsage(questionId, false, value)
    }
  }

  const handleAiAssist = async (questionId) => {
    const currentText = writings[questionId] || ''
    const question = WRITING_QUESTIONS.find(q => q.id === questionId)
    const topic = question?.topic || ''
    
    setAiAssistActive(prev => ({ ...prev, [questionId]: true }))

    try {
      // Call Python backend API for AI assistance
      const result = await api.getAIAssist(topic, currentText, questionId)
      
      if (result.success) {
        setAiSuggestions(prev => ({
          ...prev,
          [questionId]: result.suggestion
        }))
        
        // Mark as AI used
        const enhancedText = currentText + (currentText ? '\n\n' : '') + `[AI Enhanced: ${result.suggestion}]`
        await handleChange(questionId, enhancedText)
        onAiUsage(questionId, true, enhancedText)
      } else {
        console.error('AI assist failed:', result.error)
        setAiAssistActive(prev => ({ ...prev, [questionId]: false }))
      }
    } catch (error) {
      console.error('AI assist error:', error)
      setAiAssistActive(prev => ({ ...prev, [questionId]: false }))
    }
  }

  const getWordCount = (text) => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length
  }

  return (
    <div className="section-content">
      <div className="section-description">
        <p>Write essays on the following topics. You can use AI assistance, but it will be detected and reported.</p>
      </div>
      
      <div className="questions-container">
        {WRITING_QUESTIONS.map((question) => {
          const wordCount = getWordCount(writings[question.id] || '')
          const isAiUsed = aiUsage[`${category}_${question.id}`]?.used || false
          
          return (
            <div key={question.id} className="question-card writing-card">
              <div className="question-header">
                <span className="question-number">Question {question.id}</span>
                {isAiUsed && (
                  <span className="ai-badge">AI Detected</span>
                )}
              </div>
              <h3 className="writing-topic">{question.topic}</h3>
              <p className="writing-instructions">{question.instructions}</p>
              
              <div className="writing-tools">
                <button
                  className="ai-assist-button"
                  onClick={() => handleAiAssist(question.id)}
                  disabled={aiAssistActive[question.id]}
                >
                  {aiAssistActive[question.id] ? 'AI Assisting...' : 'Get AI Assistance'}
                </button>
                <div className="word-count">
                  Words: {wordCount} / {question.minWords} minimum
                </div>
              </div>

              {aiSuggestions[question.id] && (
                <div className="ai-suggestion">
                  <strong>AI Suggestion:</strong> {aiSuggestions[question.id]}
                </div>
              )}

              <textarea
                ref={el => textareaRefs.current[question.id] = el}
                className="writing-input"
                placeholder="Start writing your essay here..."
                value={writings[question.id] || ''}
                onChange={(e) => handleChange(question.id, e.target.value)}
                rows={12}
              />

              {isAiUsed && (
                <div className="ai-warning">
                  ⚠️ AI assistance has been detected in your writing. This will be reported in your results.
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default WritingSection
