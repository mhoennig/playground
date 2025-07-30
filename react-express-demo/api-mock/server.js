const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8981;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
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

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
