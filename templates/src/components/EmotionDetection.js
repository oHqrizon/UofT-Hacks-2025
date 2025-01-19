import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styling/EmotionDetection.css';

const EmotionDetection = ({ onSessionEnd }) => {
    const [isActive, setIsActive] = useState(false);
    const [metrics, setMetrics] = useState(null);
    const [error, setError] = useState(null);
    const videoRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    const startDetection = async () => {
        try {
            setIsActive(true);
            
            // Start video stream
            if (videoRef.current) {
                videoRef.current.src = 'http://localhost:5000/video_feed';
            }
            
            // Start metrics polling
            metricsIntervalRef.current = setInterval(fetchMetrics, 1000);
            
        } catch (err) {
            setError(err.message);
            console.error('Error starting detection:', err);
        }
    };

    const stopDetection = async () => {
        try {
            await axios.post('http://localhost:5000/api/stop-session');
            setIsActive(false);
            if (metricsIntervalRef.current) {
                clearInterval(metricsIntervalRef.current);
            }
            if (videoRef.current) {
                videoRef.current.src = '';
            }
            if (onSessionEnd && metrics) {
                onSessionEnd({ final_metrics: metrics });
            }
        } catch (err) {
            console.error('Error stopping detection:', err);
        }
    };

    const fetchMetrics = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/metrics');
            if (response.data) {
                setMetrics(response.data);
            }
        } catch (err) {
            console.error('Error fetching metrics:', err);
        }
    };

    useEffect(() => {
        startDetection();
        return () => {
            if (metricsIntervalRef.current) {
                clearInterval(metricsIntervalRef.current);
            }
            if (videoRef.current) {
                videoRef.current.src = '';
            }
        };
    }, []);

    return (
        <div className="emotion-detection">
            {error && <div className="error">{error}</div>}
            <div className="video-container">
                <img ref={videoRef} alt="Video feed" />
                {isActive && (
                    <button className="stop-button" onClick={stopDetection}>
                        End Session
                    </button>
                )}
            </div>
            {metrics && (
                <div className="metrics">
                    <h3>Live Metrics:</h3>
                    <div className="metrics-grid">
                        <div className="metric-card">
                            <h4>Teaching Effectiveness</h4>
                            <p className="metric-value">{metrics.teaching_effectiveness}%</p>
                        </div>
                        <div className="metric-card">
                            <h4>Student Engagement</h4>
                            <p className="metric-value">{metrics.face_presence}%</p>
                        </div>
                        <div className="metric-card">
                            <h4>Positive Response</h4>
                            <p className="metric-value">{metrics.positive_emotions}%</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EmotionDetection; 