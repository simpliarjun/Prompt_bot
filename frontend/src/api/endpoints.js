import client from './client';

// ---- Auth ----

export const registerUser = (data) => client.post('/auth/register', data).then(r => r.data);
export const loginUser = (data) => client.post('/auth/login', data).then(r => r.data);
export const getMe = () => client.get('/auth/me').then(r => r.data);

// ---- Generate ----

export const generateGrievance = (data) => client.post('/generate', data).then(r => r.data);

// ---- Grievances CRUD ----

export const createGrievance = (data) => client.post('/grievances', data).then(r => r.data);
export const listGrievances = (params) => client.get('/grievances', { params }).then(r => r.data);
export const getGrievance = (id) => client.get(`/grievances/${id}`).then(r => r.data);
export const updateGrievance = (id, data) => client.put(`/grievances/${id}`, data).then(r => r.data);
export const deleteGrievance = (id) => client.delete(`/grievances/${id}`);
export const getGrievanceStats = () => client.get('/grievances/stats').then(r => r.data);

// ---- Export ----

export const exportPdf = (id) =>
  client.get(`/grievances/${id}/export/pdf`, { responseType: 'blob' }).then(r => r);
