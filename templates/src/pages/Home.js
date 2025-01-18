// // pages/Home.js
// import React from 'react';
import React, { useState } from 'react';
import './Home.css';
import { useNavigate } from 'react-router-dom';
// import backgroundImage from '../../public/images/cam_background.png';

const Home = () => {
  const [name, setName] = useState('');
  const [education, setEducation] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !education) {
      alert('Please fill in all fields');
      return;
    }

    // Navigate directly to evaluation page
    navigate('/evaluation', { 
      state: { name, education },
      replace: true
    });
  };

  return (
    <div className="home-container">
      <div className="form-container">
        <h1>Teaching Monitor</h1>
        <h2>Enhance Your Teaching Skills</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your name"
              required
            />
          </div>

          <div className="input-group">
            <label>Education Level</label>
            <select
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
    </div>
  );
};

export default Home;