import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [envData, setEnvData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEnvData = async () => {
      try {
        const response = await axios.get('/api/env');
        setEnvData(response.data);
        setLoading(false);
      } catch (err) {
        setError('Error fetching environment data');
        console.error('Error fetching data:', err);
        setLoading(false);
      }
    };

    fetchEnvData();
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>React+Express Demo (App.jsx)</h1>
      </header>
      <main>
        <h2>Environment Data from API</h2>
        {envData ? (
          <div className="env-data">
            <pre>{JSON.stringify(envData, null, 2)}</pre>
          </div>
        ) : (
          <p>No data available</p>
        )}
      </main>
    </div>
  );
}

export default App;
