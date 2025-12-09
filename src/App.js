import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './Components/Login';
import Signup from './Components/Signup';
import ResultPage from './pages/ResultPage';
import UploadReceipt from './Components/UploadReceipt';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/signup" />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/upload" element={<UploadReceipt />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}
