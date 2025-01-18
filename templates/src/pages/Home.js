// // pages/Home.js
// import React from 'react';
import React, { useState } from 'react';
import '../styling/HomePage.css'; // Updated import path
import { useNavigate } from 'react-router-dom';


const Home = () => {
  const [name, setName] = useState('');
  const [education, setEducation] = useState('');
  const [responseData, setResponseData] = useState(null);

  const navigate = useNavigate();

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
        <nav> 
            <div className="home-page">
                    <p>&nbsp;</p>
                    <h1>Welcome to the Home Page</h1>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
                    <p1>This is the home page of the application.</p1>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
                    <p>&nbsp;</p>
            </div>
            <div className="form">
                <p>&nbsp;</p>
                <p>&nbsp;</p>
                <h1>Hop On Aboard, Captain!</h1>
                <h2>Submit Your Information</h2>
                <p>&nbsp;</p>
                <form onSubmit={handleSubmit}>
                    <div>
                    <label>
                        <p2>Name: &nbsp;</p2>
                        <input
                        type="text"
                        value={name}
                        onChange={handleNameChange}
                        required
                        />
                    </label>
                    </div>
                    <p>&nbsp;</p>
                    <div>
                    <label>
                        <p2>Education Level: &nbsp;</p2>
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
                    <p>&nbsp;</p>
                    <button className = "button" type="submit">Submit</button>
                    <p>&nbsp;</p>

                </form>

                {/* {responseData && (
                    <div className="response">
                      <p2>Submitted Data:<br/></p2>
                      <br/>
                      <p1>Name: {responseData.submitted_data.name}<br/></p1>
                      <p1>Education Level: {responseData.submitted_data.education}</p1>
                      <p>&nbsp;</p>
                      <p>&nbsp;</p>
                    </div>
                )} */}
            </div>
            
        </nav>
    );
    
}


export default Home;