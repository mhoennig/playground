const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.get('/api/env', (req, res) => {
  // Dummy environment data
  const envData = {
    appName: 'React Express Demo',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    serverTime: new Date().toISOString(),
    features: {
      featureA: true,
      featureB: false,
      featureC: true
    },
    config: {
      maxItems: 100,
      cacheEnabled: true,
      timeout: 30000
    }
  };

  res.json(envData);
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'UP' });
});

// Serve all static files from the React build directory
app.use(express.static(path.join(__dirname, '../build')));

// For any other routes, serve the index.html file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../build', 'index.html'));
});

// Export the app for Passenger
module.exports = app;

// Only start the server if this file is run directly
if (require.main === module) {
  const PORT = process.env.PORT || 8981;
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}