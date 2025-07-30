# React Express Demo

This project demonstrates a React frontend application that fetches data from a Node Express backend API.

## Project Structure

- `/` - React frontend application
- `/api-mock` - Express backend server

## Running the Application

### Start the Express Server

```bash
cd api-mock
npm install
npm start
```

The server will run on http://localhost:5000

### Start the React Frontend

```bash
# In the project root
npm install
npm start
```

The React app will run on http://localhost:3000

## Available Endpoints

- `GET /api/env` - Returns a JSON object with environment data
