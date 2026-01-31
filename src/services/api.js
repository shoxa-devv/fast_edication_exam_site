const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

export const api = {
  // Detect AI usage in text
  async detectAI(text, questionId, category = 'writing') {
    try {
      const response = await fetch(`${API_BASE_URL}/detect-ai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          questionId,
          category
        })
      })
      return await response.json()
    } catch (error) {
      console.error('AI detection error:', error)
      return { success: false, error: error.message }
    }
  },

  // Get AI assistance
  async getAIAssist(topic, currentText, questionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-assist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          currentText,
          questionId
        })
      })
      return await response.json()
    } catch (error) {
      console.error('AI assist error:', error)
      return { success: false, error: error.message }
    }
  },

  // Submit exam
  async submitExam(examData) {
    try {
      const response = await fetch(`${API_BASE_URL}/submit-exam`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(examData)
      })
      return await response.json()
    } catch (error) {
      console.error('Submit exam error:', error)
      return { success: false, error: error.message }
    }
  },

  // Get exam results
  async getExamResults(examId) {
    try {
      const response = await fetch(`${API_BASE_URL}/exam-results/${examId}`)
      return await response.json()
    } catch (error) {
      console.error('Get results error:', error)
      return { success: false, error: error.message }
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      return await response.json()
    } catch (error) {
      return { status: 'unhealthy', error: error.message }
    }
  }
}
