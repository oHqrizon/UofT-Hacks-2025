import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';  // Import useNavigate

const Form = () => {
  const [name, setName] = useState('');
  const [education, setEducation] = useState('');
  
  const navigate = useNavigate();  // Initialize useNavigate hook

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handleEducationChange = (e) => {
    setEducation(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = {
      name: name,
      education: education
    };

    try {
      // Here we are submitting the form data to Flask
      const response = await fetch('http://127.0.0.1:5000/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      // After form submission, redirect to /evaluation and pass the data via state
      navigate('/evaluation', { state: { name: name, education: education } });
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className="form-container">
      <h2>Submit Your Information</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Name:
            <input
              type="text"
              value={name}
              onChange={handleNameChange}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Education Level:
            <select
              value={education}
              onChange={handleEducationChange}
              required
            >
              <option value="">Select Education Level</option>
              <option value="Elementary">Elementary</option>
              <option value="Middle">Middle School</option>
              <option value="Highschool">High School</option>
              <option value="University">University</option>
            </select>
          </label>
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default Form;
