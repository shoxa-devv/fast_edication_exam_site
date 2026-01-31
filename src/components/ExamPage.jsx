import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import GrammarSection from './sections/GrammarSection'
import TranslationSection from './sections/TranslationSection'
import WritingSection from './sections/WritingSection'
import VocabularySection from './sections/VocabularySection'
import './ExamPage.css'

const CATEGORIES = [
  { id: 'grammar', name: 'Grammar', component: GrammarSection },
  { id: 'translation', name: 'Translation', component: TranslationSection },
  { id: 'writing', name: 'Writing', component: WritingSection },
  { id: 'vocabulary', name: 'Vocabulary', component: VocabularySection },
]

function ExamPage({ setExamResults }) {
  const [currentCategory, setCurrentCategory] = useState(0)
  const [answers, setAnswers] = useState({})
  const [aiUsage, setAiUsage] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // Simulate initialization
    setTimeout(() => setIsLoading(false), 1000)
  }, [])

  const handleAnswer = (questionId, answer, category) => {
    setAnswers(prev => ({
      ...prev,
      [`${category}_${questionId}`]: answer
    }))
  }

  const handleAiUsage = (questionId, used, text) => {
    setAiUsage(prev => ({
      ...prev,
      [`writing_${questionId}`]: { used, text }
    }))
  }

  const handleNext = () => {
    if (currentCategory < CATEGORIES.length - 1) {
      setCurrentCategory(prev => prev + 1)
    }
  }

  const handlePrevious = () => {
    if (currentCategory > 0) {
      setCurrentCategory(prev => prev - 1)
    }
  }

  const handleSubmit = async () => {
    const results = {
      answers,
      aiUsage,
      categories: CATEGORIES.map(cat => cat.id),
      timestamp: new Date().toISOString()
    }
    
    // Submit to Python backend
    try {
      const { api } = await import('../services/api')
      const submitResult = await api.submitExam(results)
      if (submitResult.success) {
        results.examId = submitResult.examId
        results.aiUsageSummary = submitResult.aiUsageSummary
      }
    } catch (error) {
      console.error('Failed to submit to backend:', error)
    }
    
    setExamResults(results)
    navigate('/results')
  }

  const CurrentSection = CATEGORIES[currentCategory].component
  const isLastCategory = currentCategory === CATEGORIES.length - 1
  const isFirstCategory = currentCategory === 0

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Initializing...</p>
      </div>
    )
  }

  return (
    <div className="exam-page">
      <div className="exam-header">
        <h1>English Language Exam</h1>
        <div className="progress-bar">
          {CATEGORIES.map((cat, index) => (
            <div
              key={cat.id}
              className={`progress-step ${index === currentCategory ? 'active' : ''} ${index < currentCategory ? 'completed' : ''}`}
            >
              <div className="step-number">{index + 1}</div>
              <div className="step-label">{cat.name}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="exam-content">
        <div className="category-header">
          <h2>{CATEGORIES[currentCategory].name}</h2>
          <span className="category-counter">
            {currentCategory + 1} / {CATEGORIES.length}
          </span>
        </div>

        <div className="section-container">
          <CurrentSection
            onAnswer={handleAnswer}
            onAiUsage={handleAiUsage}
            answers={answers}
            aiUsage={aiUsage}
            category={CATEGORIES[currentCategory].id}
          />
        </div>

        <div className="exam-navigation">
          <button
            onClick={handlePrevious}
            disabled={isFirstCategory}
            className="nav-button prev-button"
          >
            Previous
          </button>
          {isLastCategory ? (
            <button
              onClick={handleSubmit}
              className="nav-button submit-button"
            >
              Submit Exam
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="nav-button next-button"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ExamPage
