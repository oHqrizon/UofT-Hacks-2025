import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const EmotionDetection = () => {
    const [isActive, setIsActive] = useState(false);
    const [metrics, setMetrics] = useState(null);
    const [error, setError] = useState(null);
    const videoRef = useRef(null);
    const metricsIntervalRef = useRef(null);

    const startDetection = async () => {
        try {
            // Test camera first
            const testResponse = await axios.get('http://localhost:5000/api/test-camera');
            if (testResponse.data.status !== 'success') {
                throw new Error('Camera test failed');
            }

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
            await axios.post('http://localhost:5000/api/stop-emotion-detection');
            await axios.post('http://localhost:5000/api/cleanup');
            setIsActive(false);
            clearInterval(metricsIntervalRef.current);
            if (videoRef.current) {
                videoRef.current.src = '';
            }
        } catch (err) {
            console.error('Error stopping detection:', err);
        }
    };

    const fetchMetrics = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/metrics');
            setMetrics(response.data);
        } catch (err) {
            console.error('Error fetching metrics:', err);
        }
    };

    useEffect(() => {
        return () => {
            stopDetection();
        };
    }, []);

    return (
        <div>
            {error && <div className="error">{error}</div>}
            <div className="controls">
                <button onClick={isActive ? stopDetection : startDetection}>
                    {isActive ? 'Stop Detection' : 'Start Detection'}
                </button>
            </div>
            <div className="video-container">
                <img ref={videoRef} alt="Video feed" style={{width: '640px', height: '480px'}} />
            </div>
            {metrics && (
                <div className="metrics">
                    <h3>Metrics:</h3>
                    <p>Teaching Effectiveness: {metrics.teaching_effectiveness}%</p>
                    <p>Face Presence: {metrics.face_presence}%</p>
                    <p>Positive Emotions: {metrics.positive_emotions}%</p>
                </div>
            )}
        </div>
    );
};

export default EmotionDetection; 