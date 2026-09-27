import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Contacts
export const getContacts = (params) => api.get('/contacts/', { params });
export const createContact = (data) => api.post('/contacts/', data);
export const updateContact = (id, data) => api.put(`/contacts/${id}/`, data);
export const deleteContact = (id) => api.delete(`/contacts/${id}/`);
export const bulkImportContacts = (data) => api.post('/contacts/bulk-import/', data);

// Groups
export const getGroups = (params) => api.get('/groups/', { params });
export const createGroup = (data) => api.post('/groups/', data);
export const getGroupDetail = (id) => api.get(`/groups/${id}/`);
export const addGroupMembers = (id, contactIds) => api.post(`/groups/${id}/add-members/`, { contact_ids: contactIds });
export const removeGroupMembers = (id, contactIds) => api.post(`/groups/${id}/remove-members/`, { contact_ids: contactIds });

// Templates
export const getTemplates = (params) => api.get('/templates/', { params });
export const createTemplate = (data) => api.post('/templates/', data);

// Broadcasts
export const getBroadcasts = (params) => api.get('/broadcasts/', { params });
export const createBroadcast = (data) => api.post('/broadcasts/', data);
export const getBroadcastDetail = (id) => api.get(`/broadcasts/${id}/`);
export const sendBroadcast = (id) => api.post(`/broadcasts/${id}/send/`);
export const getBroadcastStatus = (id) => api.get(`/broadcasts/${id}/status/`);
export const getBroadcastRecipients = (id, params) => api.get(`/broadcasts/${id}/recipients/`, { params });
export const retryFailedMessages = (id) => api.post(`/broadcasts/${id}/retry-failed/`);

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats/');

export default api;
