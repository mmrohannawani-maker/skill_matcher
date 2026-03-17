import apiClient from './client';

export const loginUser = async (credentials) => {
  const response = await apiClient.post('/auth/login', credentials);
  return response.data; // Stores JWT and User info
};