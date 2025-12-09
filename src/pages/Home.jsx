import React, { useState } from 'react';
import axios from 'axios';
import './Home.css';
import { useNavigate } from 'react-router-dom'; // ✅ Import navigation hook

export default function Home() {
  const [responseMsg, setResponseMsg] = useState('');
  const navigate = useNavigate(); // ✅ Initialize navigator

  const toggleMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
  };

  const handleGetStarted = async () => {
    try {
      // Optional backend trigger (you can remove if unnecessary)
      const res = await axios.post('http://localhost:5000/api/start', {
        message: 'User clicked get started'
      });
      setResponseMsg(res.data.message);

      // ✅ Redirect to the Upload Receipt page
      navigate('/upload');
    } catch (err) {
      console.error(err);
      setResponseMsg('Error connecting to backend.');
      // Still redirect even if backend fails (optional)
      navigate('/upload');
    }
  };

  return (
    <div>
      <nav className="navbar">
        <a href="#" className="logo">EcoSphere</a>
        <div className="menu-toggle" onClick={toggleMenu}>☰</div>
        <div className="nav-links">
          <a href="#">Home</a>
          <a href="#">Features</a>
          <a href="#">About</a>
          <a href="#">Contact</a>
        </div>
      </nav>

      <section className="hero">
        <h1>EcoSphere – Make Every Purchase Count</h1>
        <p>Earn rewards. Track impact. Shop sustainably with Walmart.</p>
        <button className="cta-button" onClick={handleGetStarted}>
          Get Started
        </button>
        {responseMsg && <p style={{ marginTop: '20px' }}>{responseMsg}</p>}
      </section>

      <section className="features">
        <div className="feature-card">
          <h3>Earn EcoPoints</h3>
          <p>Earn EcoPoints for green purchases</p>
        </div>
        <div className="feature-card">
          <h3>Upload Receipts</h3>
          <p>Upload Walmart receipt and get rewarded</p>
        </div>
        <div className="feature-card">
          <h3>Sentiment Gauge</h3>
          <p>See how many users care via sentiment gauge</p>
        </div>
      </section>

      <footer className="footer">
        <p>© 2025 EcoSphere. All rights reserved.</p>
      </footer>
    </div>
  );
}
