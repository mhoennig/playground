# React+Express Demo
# React Express Demo (Vite)

This is a React application built with Vite that communicates with an Express backend.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode using Vite.
Open [http://localhost:8980](http://localhost:8980) to view it in your browser.

### `npm run build`

Builds the app for production to the `dist` folder.

### `npm run preview`

Locally preview the production build.

### `npm test`

Launches the test runner using Vitest.

### `npm run server`

Runs the API mock server.

### `npm run dev`

Runs both the frontend and API server concurrently.
This project demonstrates deployment of a React/Express application in a Hostsharing Managed Webspace.
It consists of a React frontend that fetches data from a Node Express backend API.

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
