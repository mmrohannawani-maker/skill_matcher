import apiClient from './client';

export const getDevelopers = async () => {
  const response = await apiClient.get('/developers');
  return response.data;
};