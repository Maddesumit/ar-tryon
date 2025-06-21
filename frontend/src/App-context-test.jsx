import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
          <h1 className="text-4xl font-bold text-center py-20 text-gray-900 dark:text-white">
            AR Try-On with Context Test
          </h1>
          <p className="text-center text-gray-600 dark:text-gray-300">
            If you can see this, the contexts are working!
          </p>
        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
