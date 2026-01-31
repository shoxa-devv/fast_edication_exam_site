import React, { useState } from 'react'
import './SectionStyles.css'

const GRAMMAR_QUESTIONS = [
  {
    id: 1,
    question: "Choose the correct form: I _____ to the store yesterday.",
    options: ["go", "went", "gone", "going"],
    correct: 1
  },
  {
    id: 2,
    question: "Which sentence is grammatically correct?",
    options: [
      "She don't like coffee.",
      "She doesn't like coffee.",
      "She not like coffee.",
      "She isn't like coffee."
    ],
    correct: 1
  },
  {
    id: 3,
    question: "Complete the sentence: If I _____ rich, I would travel the world.",
    options: ["am", "was", "were", "be"],
    correct: 2
  },
  {
    id: 4,
    question: "Choose the correct article: _____ apple a day keeps the doctor away.",
    options: ["A", "An", "The", "No article"],
    correct: 1
  },
  {
    id: 5,
    question: "Which is the correct past perfect form?",
    options: [
      "I had went to the store.",
      "I had go to the store.",
      "I had gone to the store.",
      "I have gone to the store."
    ],
    correct: 2
  }
]

function GrammarSection({ onAnswer, answers, category }) {
  const [selectedAnswers, setSelectedAnswers] = useState(
    GRAMMAR_QUESTIONS.reduce((acc, q) => {
      const key = `${category}_${q.id}`
      if (answers[key] !== undefined) {
        acc[q.id] = answers[key]
      }
      return acc
    }, {})
  )

  const handleSelect = (questionId, optionIndex) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: optionIndex
    }))
    onAnswer(questionId, optionIndex, category)
  }

  return (
    <div className="section-content">
      <div className="section-description">
        <p>Choose the correct answer for each grammar question.</p>
      </div>
      
      <div className="questions-container">
        {GRAMMAR_QUESTIONS.map((question) => (
          <div key={question.id} className="question-card">
            <div className="question-header">
              <span className="question-number">Question {question.id}</span>
            </div>
            <p className="question-text">{question.question}</p>
            <div className="options-container">
              {question.options.map((option, index) => (
                <label
                  key={index}
                  className={`option-label ${
                    selectedAnswers[question.id] === index ? 'selected' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name={`grammar_${question.id}`}
                    value={index}
                    checked={selectedAnswers[question.id] === index}
                    onChange={() => handleSelect(question.id, index)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default GrammarSection
