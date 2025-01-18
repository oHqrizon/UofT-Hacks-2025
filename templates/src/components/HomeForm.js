import React, { useState } from 'react';

const Form = () => {
  const [name, setName] = useState('');
  const [education, setEducation] = useState('');
  const [responseData, setResponseData] = useState(null);

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
      const response = await fetch('http://127.0.0.1:5000/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      setResponseData(data);  // Store the response data to display it
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

      {responseData && (
        <div className="response">
          <h3>Submitted Data:</h3>
          <p>Name: {responseData.submitted_data.name}</p>
          <p>Education Level: {responseData.submitted_data.education}</p>
        </div>
      )}
    </div>
  );
};

export default Form;