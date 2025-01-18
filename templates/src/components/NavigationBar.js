// src/NavigationBar.js
import React from 'react';
import '../styling/NavigationBar.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faInfoCircle, faEnvelope, faUser } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';

function NavigationBar() {
    return (
        <nav className="navbar">
            <div className="navigation-bar">
                <ul>
                    <li><Link to="/"><FontAwesomeIcon icon={faHome} /></Link></li>
                    <li><Link to="/evaluation"><FontAwesomeIcon icon={faInfoCircle} /></Link></li>
                    <li><Link to="/results"><FontAwesomeIcon icon={faEnvelope} /></Link></li>
                    <li><Link to="/profile"><FontAwesomeIcon icon={faUser} /></Link></li>
                </ul>
            </div>
        </nav>
    );
}

export default NavigationBar;