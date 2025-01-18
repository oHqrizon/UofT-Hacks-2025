import React, { useState } from 'react';
import EmotionDetection from '../components/EmotionDetection';
import './Evaluation.css';

function Evaluation() {
    const [isSessionActive, setIsSessionActive] = useState(false);
    const [sessionResults, setSessionResults] = useState(null);

    return (
        <div className="evaluation-page">
            <div className="evaluation-container">
                <h2>Teaching Session Evaluation</h2>
                
                {!isSessionActive && !sessionResults && (
                    <div className="start-session">
                        <p>Start a new teaching session to evaluate your performance</p>
                        <button 
                            className="start-button"
                            onClick={() => setIsSessionActive(true)}
                        >
                            Start New Session
                        </button>
                    </div>
                )}

                {isSessionActive && (
                    <EmotionDetection 
                        onSessionEnd={(results) => {
                            setSessionResults(results);
                            setIsSessionActive(false);
                        }}
                    />
                )}

                {sessionResults && (
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
                                setIsSessionActive(true);
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
