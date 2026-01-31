import React, { useState } from 'react'
import './SectionStyles.css'

const VOCABULARY_QUESTIONS = [
  {
    id: 1,
    word: "Eloquent",
    options: [
      "Able to express ideas clearly and effectively",
      "Very quiet and shy",
      "Extremely angry",
      "Very tired"
    ],
    correct: 0
  },
  {
    id: 2,
    word: "Benevolent",
    options: [
      "Evil and harmful",
      "Kind and generous",
      "Very confused",
      "Extremely fast"
    ],
    correct: 1
  },
  {
    id: 3,
    word: "Ephemeral",
    options: [
      "Lasting forever",
      "Lasting for a very short time",
      "Very expensive",
      "Extremely large"
    ],
    correct: 1
  },
  {
    id: 4,
    word: "Meticulous",
    options: [
      "Very careless",
      "Showing great attention to detail",
      "Very lazy",
      "Extremely loud"
    ],
    correct: 1
  },
  {
    id: 5,
    word: "Resilient",
    options: [
      "Able to recover quickly from difficulties",
      "Very weak",
      "Extremely stubborn",
      "Very forgetful"
    ],
    correct: 0
  }
]

function VocabularySection({ onAnswer, answers, category }) {
  const [selectedAnswers, setSelectedAnswers] = useState(
    VOCABULARY_QUESTIONS.reduce((acc, q) => {
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
        <p>Choose the correct definition for each vocabulary word.</p>
      </div>
      
      <div className="questions-container">
        {VOCABULARY_QUESTIONS.map((question) => (
          <div key={question.id} className="question-card vocabulary-card">
            <div className="question-header">
              <span className="question-number">Question {question.id}</span>
            </div>
            <div className="vocabulary-word">
              <h3>{question.word}</h3>
            </div>
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
                    name={`vocabulary_${question.id}`}
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

export default VocabularySection
