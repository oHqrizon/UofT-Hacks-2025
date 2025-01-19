// // pages/Home.js
// import React from 'react';
import React, { useState } from 'react';
import '../styling/Home.css';
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
      <div className="title-section">
        <h1>Cognspective</h1>
        <h2>Enhance YOUR learning.</h2>
      </div>

      <div className="form-container">
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
          <label>Your Education Level</label>
          <select
            value={education}
            onChange={(e) => setEducation(e.target.value)}
            required
          >
            <option value="">Select Education Level</option>
            <option value="Elementary">Elementary</option>
            <option value="Middle School">Middle School</option>
            <option value="High school">High School</option>
            <option value="University">University</option>
          </select>
        </div>

        <button type="submit" className="submit-button" onClick={handleSubmit}>
          Continue to Evaluation
        </button>
      </div>
    </div>
  );
};

export default Home;