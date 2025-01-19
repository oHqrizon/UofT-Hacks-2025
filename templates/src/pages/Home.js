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
      <div className="text-wrapper">
        <div className="text-container-top">
          <div className="input-group">
            <label> Cognspective is a platform designed to help users develop a deeper understanding of concepts by teaching them from various perspectives. </label>
          </div>
        </div>

        <div className="text-container-bottom-left">
          <div className="input-group">
            <label > By explaining a topic at different educational levels, users are encouraged to fully grasp the material, as teaching others requires a thorough comprehension of the subject. </label>
          </div>
        </div>

        <div className="text-container-bottom-right">
          <div className="input-group">
            <label > This approach not only reinforces the user's knowledge but also enhances their ability to communicate complex ideas in simpler terms, fostering both mastery of the content and effective teaching skills. </label>
          </div>

        </div>

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