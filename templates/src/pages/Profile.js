import React from 'react';
import '../styling/ProfilePage.css'; 
import { useLocation } from 'react-router-dom';

function capitalizeFirstLetter(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function Profile() {
    const location = useLocation();
    const { name, education } = location.state || {};  
    
    return (
        <nav className="profile-page">
            <div>
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 
                <h>&nbsp;&nbsp;&emsp;&emsp;&emsp;Profile</h>
                <br/>
                <br/>
                <p>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Name: <i>{capitalizeFirstLetter(name)}</i></p>
                <br/>
                <p>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Education: <i>{capitalizeFirstLetter(name)}</i></p>
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 
                <p>&nbsp;</p> 


            </div>
        </nav>
    );
}

export default Profile;