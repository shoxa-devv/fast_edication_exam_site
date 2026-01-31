import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import ExamPage from './components/ExamPage'
import ResultsPage from './components/ResultsPage'
import './App.css'

function App() {
  const [examResults, setExamResults] = useState(null)

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/" 
            element={<ExamPage setExamResults={setExamResults} />} 
          />
          <Route 
            path="/results" 
            element={
              examResults ? (
                <ResultsPage results={examResults} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
