import React, { useState } from 'react';
import EmotionDetection from '../components/EmotionDetection';
import '../styling/EvaluationPage.css';
import axios from 'axios';

function Evaluation() {
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [sessionResults, setSessionResults] = useState(null);
    const [showSubjectPrompt, setShowSubjectPrompt] = useState(true);
    const [subject, setSubject] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubjectSubmit = async (e) => {
        e.preventDefault();
        if (subject.trim()) {
            try {
                setIsLoading(true);
                
                // TEMPORARY: Skip camera test and just start transcription
                const response = await axios.post('http://localhost:5000/api/start-session', {
                    subject: subject
                });
                
                // Even if camera fails, proceed with session
                setShowSubjectPrompt(false);
                setIsSessionActive(true);
                setIsLoading(false);
            } catch (error) {
                console.error('Error starting session:', error);
                // TEMPORARY: Continue even if there's an error
                setShowSubjectPrompt(false);
                setIsSessionActive(true);
                setIsLoading(false);
            }
        }
    };

    const handleSessionEnd = async (results) => {
        try {
            // Stop session (stops both emotion detection and transcription)
            await axios.post('http://localhost:5000/api/stop-session');
            
            if (results && results.final_metrics) {
                setSessionResults(results);
                setIsSessionActive(false);
                setSubject('');
                setShowSubjectPrompt(false);
            }
        } catch (error) {
            console.error('Error stopping session:', error);
        }
    };

    return (
        <div className="evaluation-page">
            <div className="evaluation-container">
                <h2>Teaching Session Evaluation</h2>
                
                {showSubjectPrompt && !isLoading && !isSessionActive && !sessionResults && (
                    <div className="subject-prompt">
                        <h3>What subject will you be teaching?</h3>
                        <form onSubmit={handleSubjectSubmit}>
                            <input
                                type="text"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                placeholder="Enter subject (e.g., Mathematics, History)"
                                required
                            />
                            <button type="submit" className="start-button">
                                Begin Session
                            </button>
                        </form>
                    </div>
                )}

                {isLoading && (
                    <div className="loading-screen">
                        <div className="loading-spinner"></div>
                        <h3>Initializing Camera...</h3>
                        <p>Please wait while we set up your teaching session</p>
                    </div>
                )}

                {isSessionActive && !sessionResults && (
                    <EmotionDetection onSessionEnd={handleSessionEnd} />
                )}

                {sessionResults && !isSessionActive && !showSubjectPrompt && (
                    <div className="session-results">
                        <h3>Session Results</h3>
                        <div className="results-grid">
                            <div className="result-card">
                                <h4>Teaching Effectiveness</h4>
                                <p className="score">{sessionResults.final_metrics?.teaching_effectiveness}%</p>
                            </div>
                            <div className="result-card">
                                <h4>Student Engagement</h4>
                                <p className="score">{sessionResults.final_metrics?.face_presence}%</p>
                            </div>
                            <div className="result-card">
                                <h4>Positive Response</h4>
                                <p className="score">{sessionResults.final_metrics?.positive_emotions}%</p>
                            </div>
                        </div>
                        
                        <button 
                            className="start-button"
                            onClick={() => {
                                setSessionResults(null);
                                setShowSubjectPrompt(true);
                            }}
                        >
                            Start New Session
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Evaluation;
