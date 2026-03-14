export const API_BASE_URL = (import.meta.env.PROD 
    ? '/api' 
    : (import.meta.env.VITE_API_URL || 'http://localhost:8000/api')).replace(/\/$/, '');
