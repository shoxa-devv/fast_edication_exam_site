import React, { useState } from 'react'
import './SectionStyles.css'

const TRANSLATION_QUESTIONS = [
  {
    id: 1,
    text: "Salom, qandaysiz?",
    hint: "Translate to English"
  },
  {
    id: 2,
    text: "Men universitetda o'qiyman.",
    hint: "Translate to English"
  },
  {
    id: 3,
    text: "Bu kitob juda qiziqarli.",
    hint: "Translate to English"
  },
  {
    id: 4,
    text: "Ertaga biz parkga boramiz.",
    hint: "Translate to English"
  },
  {
    id: 5,
    text: "Siz ingliz tilini yaxshi bilasizmi?",
    hint: "Translate to English"
  }
]

function TranslationSection({ onAnswer, answers, category }) {
  const [translations, setTranslations] = useState(
    TRANSLATION_QUESTIONS.reduce((acc, q) => {
      const key = `${category}_${q.id}`
      if (answers[key] !== undefined) {
        acc[q.id] = answers[key]
      } else {
        acc[q.id] = ''
      }
      return acc
    }, {})
  )

  const handleChange = (questionId, value) => {
    setTranslations(prev => ({
      ...prev,
      [questionId]: value
    }))
    onAnswer(questionId, value, category)
  }

  return (
    <div className="section-content">
      <div className="section-description">
        <p>Translate the following sentences from Uzbek to English.</p>
      </div>
      
      <div className="questions-container">
        {TRANSLATION_QUESTIONS.map((question) => (
          <div key={question.id} className="question-card">
            <div className="question-header">
              <span className="question-number">Question {question.id}</span>
              <span className="question-hint">{question.hint}</span>
            </div>
            <div className="translation-source">
              <p className="source-text">{question.text}</p>
            </div>
            <textarea
              className="translation-input"
              placeholder="Enter your translation here..."
              value={translations[question.id] || ''}
              onChange={(e) => handleChange(question.id, e.target.value)}
              rows={3}
            />
          </div>
        ))}
      </div>
    </div>
  )
}

export default TranslationSection
