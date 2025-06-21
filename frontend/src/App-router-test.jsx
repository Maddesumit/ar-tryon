import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

function TestHome() {
  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold">Home Page Test</h2>
      <p>This is a test home page.</p>
    </div>
  );
}

function TestProducts() {
  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold">Products Page Test</h2>
      <p>This is a test products page.</p>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            <nav className="bg-white dark:bg-gray-800 shadow p-4">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                AR Try-On Router Test
              </h1>
            </nav>
            <main>
              <Routes>
                <Route path="/" element={<TestHome />} />
                <Route path="/products" element={<TestProducts />} />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
