// // pages/Home.js
// import React from 'react';
import React, { useState } from 'react';
import './Home.css';
import { useNavigate } from 'react-router-dom';
import backgroundImage from '../styling/images/cam_background.png';

const Home = () => {
  const [name, setName] = useState('');
  const [education, setEducation] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // First, validate the form
    if (!name || !education) {
      alert('Please fill in all fields');
      return;
    }

    try {
      // Send data to backend
      const response = await fetch('http://127.0.0.1:5000/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, education }),
      });

      if (response.ok) {
        // Immediately navigate to evaluation page
        navigate('/evaluation', { 
          state: { name, education },
          replace: true  // This prevents going back to the form
        });
      } else {
        // If server response wasn't ok, still navigate but show warning
        console.warn('Server response was not ok, but continuing navigation');
        navigate('/evaluation', { 
          state: { name, education },
          replace: true
        });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      // Even if there's an error with the backend, still navigate
      navigate('/evaluation', { 
        state: { name, education },
        replace: true
      });
    }
  };

  return (
    <div 
      className="home-container" 
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(26, 35, 126, 0.8) 0%, rgba(13, 71, 161, 0.8) 100%), url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      <div className="form-container">
        <div className="title-container">
          <h1>Teaching Monitor</h1>
          <h2>Enhance Your Teaching Skills</h2>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Enter your name"
            />
          </div>

          <div className="input-group">
            <label htmlFor="education">Education Level</label>
            <select
              id="education"
              value={education}
              onChange={(e) => setEducation(e.target.value)}
              required
            >
              <option value="">Select Education Level</option>
              <option value="Elementary">Elementary</option>
              <option value="Middle">Middle School</option>
              <option value="Highschool">High School</option>
              <option value="University">University</option>
            </select>
          </div>

          <button type="submit" className="submit-button">
            Start Journey
          </button>
        </form>
      </div>
      <div className="floating-elements">
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className="floating-element"
            style={{
              left: `${Math.random() * 100}%`,
              width: `${Math.random() * 50 + 20}px`,
              height: `${Math.random() * 50 + 20}px`,
              animationDelay: `${Math.random() * 20}s`,
              animationDuration: `${Math.random() * 20 + 10}s`
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default Home;