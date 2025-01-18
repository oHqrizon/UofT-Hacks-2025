import React from 'react';
import '../styling/ProfilePage.css'; 
import { useLocation } from 'react-router-dom';

function Profile() {
    const location = useLocation();
    const { name, education } = location.state || {};  // Destructure the state to get name and education
    
    return (
        <nav className="profile-page">
            <div>
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 
                <h>&ensp;&emsp;&emsp;Profile</h>
                <br/>
                <br/>
                <p>&emsp;&emsp;&emsp;&emsp;Name: {name}</p>
                <br/>
                <p>&emsp;&emsp;&emsp;&emsp;Education: {education}</p>
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 


            </div>
        </nav>
    );
}

export default Profile;