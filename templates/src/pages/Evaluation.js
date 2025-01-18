import React from 'react';
import { useLocation } from 'react-router-dom';  // Import useLocation


const Evaluation = () => {
  // Retrieve state passed from the Form component
  const location = useLocation();
  const { name, education } = location.state || {};  // Destructure the state to get name and education

  return (
    <div>
      <h1>Evaluation</h1>
      {name && education ? (
        <div>
          <h2>Submitted Information</h2>
          <p><strong>Name:</strong> {name}</p>
          <p><strong>Education Level:</strong> {education}</p>
        </div>
      ) : (
        <p>No information submitted.</p>
      )}
    </div>
  );
};

export default Evaluation;