export const API_BASE_URL = (import.meta.env.VITE_API_URL || 
    (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api')).replace(/\/$/, '');

// Replace this with your actual Cloudflare Worker URL after deployment
export const CLOUDFLARE_WORKER_URL = import.meta.env.VITE_WORKER_URL || 'https://your-worker.workers.dev';
