import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 12000,
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Unexpected error';
    return Promise.reject({
      message,
      status: error.response?.status,
      data: error.response?.data,
    });
  }
);

export const getHealth = () => api.get('/health');
export const getRecommendations = () => api.get('/recommendations');
export const getAlerts = () => api.get('/alerts');

export const getEmergencyLoad = (payload = { horizon: 7 }) => api.post('/predict/emergency', payload);
export const getIcuStatus = (payload = { horizon: 7 }) => api.post('/predict/icu', payload);
export const getStaffLoad = (payload = { horizon: 7 }) => api.post('/predict/staff', payload);
export const getDashboard = () => api.get('/dashboard');

// Generic patient risk / predict endpoint (FastAPI expects numeric fields)
export const predictPatientRisk = (payload) => api.post('/predict', payload);
export const predictNoShow = (payload) => api.post('/noshow/predict', payload);
export const getFeatureInsights = () => api.get('/noshow/model-insights');

export const getChatbotFeed = (params = {}) => api.get('/chatbot/feed', { params });
export const getChatbotStatus = () => api.get('/chatbot/status');
export const sendChatMessage = (message) => api.post('/chatbot/chat', { message });

export const getVitalsOverview = () => api.get('/vitals/overview');
export const getAdherenceOverview = () => api.get('/adherence/population-overview');

export default api;
