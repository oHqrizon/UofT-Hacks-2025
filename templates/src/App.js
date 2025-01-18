import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import Home from './pages/Home';
import Evaluation from './pages/Evaluation';
import Results from './pages/Results';
import Profile from './pages/Profile';
import logo from './logo.svg';
import './App.css';
import HomeForm from './components/HomeForm';

function App() {
  return (
    <Router>
      <div className="App">
        <NavigationBar />
        <Routes>
          <Route path="/" element={<HomeForm />} />
          <Route path="/evaluation" element={<Evaluation />} />
          <Route path="/results" element={<Results />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
