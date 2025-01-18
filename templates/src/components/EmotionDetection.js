import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './EmotionDetection.css';

const EmotionDetection = ({ onSessionEnd }) => {
    const [isActive, setIsActive] = useState(false);
    const [metrics, setMetrics] = useState(null);
    const [error, setError] = useState(null);
    const videoRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    const startDetection = async () => {
        try {
            // Start emotion detection
            await axios.post('http://localhost:5000/api/start-emotion-detection');
            setIsActive(true);
            
            // Start video stream
            if (videoRef.current) {
                videoRef.current.src = 'http://localhost:5000/api/video-feed';
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
            const response = await axios.post('http://localhost:5000/api/stop-emotion-detection');
            const finalResults = response.data;
            await axios.post('http://localhost:5000/api/cleanup');
            setIsActive(false);
            if (metricsIntervalRef.current) {
                clearInterval(metricsIntervalRef.current);
            }
            if (videoRef.current) {
                videoRef.current.src = '';
            }
            if (onSessionEnd && finalResults) {
                onSessionEnd(finalResults);
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

    // Start detection automatically when component mounts
    useEffect(() => {
        const initializeDetection = async () => {
            try {
                await startDetection();
            } catch (err) {
                console.error('Failed to initialize detection:', err);
                setError('Failed to start camera. Please try again.');
            }
        };

        initializeDetection();

        // Cleanup function
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