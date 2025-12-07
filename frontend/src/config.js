/**
 * Application Configuration
 * Uses Vite environment variables for deployment flexibility
 */

// API Base URL - defaults to localhost for development
// Set VITE_API_URL in your .env or Vercel environment variables for production
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Export other configuration as needed
export const config = {
  apiBaseUrl: API_BASE_URL,
  // Add other config values here
};

export default config;

