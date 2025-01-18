// src/NavigationBar.js
import React from 'react';
import '../styling/NavigationBar.css'; // Updated import path
// Import Font Awesome icons
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faInfoCircle, faEnvelope, faUser } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';

function NavigationBar() {
    return (
        <nav className="navigation-bar">
            <div className="logo-title">
                <img src="path/to/logo.png" alt="Logo" className="logo" />
                <span className="title">My Website</span>
            </div>
            <ul>
                <li><Link to="/"><FontAwesomeIcon icon={faHome} /></Link></li>
                <li><Link to="/evaluation"><FontAwesomeIcon icon={faInfoCircle} /></Link></li>
                <li><Link to="/results"><FontAwesomeIcon icon={faEnvelope} /></Link></li>
                <li><Link to="/profile"><FontAwesomeIcon icon={faUser} /></Link></li>
            </ul>
        </nav>
    );
}

export default NavigationBar;