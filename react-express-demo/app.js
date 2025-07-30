/**
 * app.js - Entry point for Phusion Passenger
 * This file exports the Express app from the api-mock directory
 */
const app = require('./api-mock/server');
module.exports = app;