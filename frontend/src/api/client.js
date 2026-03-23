/**
 * API client for FRS Data Management System
 * Handles all HTTP requests to the backend API
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload a directory of FRS data
 * @param {string} directoryPath - Path to directory
 * @param {string} tag - Optional custom tag
 * @param {string} description - Optional description
 * @returns {Promise} Upload response
 */
export const uploadDirectory = async (directoryPath, tag = null, description = null) => {
  const response = await apiClient.post('/upload', {
    directory_path: directoryPath,
    tag,
    description,
  });
  return response.data;
};

/**
 * Get list of all datasets
 * @returns {Promise} Array of datasets
 */
export const getDatasets = async () => {
  const response = await apiClient.get('/datasets');
  return response.data;
};

/**
 * Get data for a specific dataset
 * @param {string} tag - Dataset tag
 * @param {string} unitFilter - Unit filter ("All" or specific unit)
 * @param {string} sheetType - Optional sheet type filter
 * @returns {Promise} Data response
 */
export const getData = async (tag, unitFilter = 'All', sheetType = null) => {
  const params = { unit_filter: unitFilter };
  if (sheetType) {
    params.sheet_type = sheetType;
  }
  const response = await apiClient.get(`/data/${encodeURIComponent(tag)}`, { params });
  return response.data;
};

/**
 * Get list of units in a dataset
 * @param {string} tag - Dataset tag
 * @returns {Promise} Array of unit names
 */
export const getUnits = async (tag) => {
  const response = await apiClient.get(`/data/${encodeURIComponent(tag)}/units`);
  return response.data;
};

/**
 * Compare two datasets
 * @param {string} tag1 - First dataset tag
 * @param {string} tag2 - Second dataset tag
 * @param {Array} sheetTypes - Optional array of sheet types to compare
 * @returns {Promise} Comparison response with LLM-generated text
 */
export const compareDatasets = async (tag1, tag2, sheetTypes = null) => {
  const response = await apiClient.post('/compare', {
    tag1,
    tag2,
    sheet_types: sheetTypes,
  });
  return response.data;
};

/**
 * Delete a dataset and all associated data
 * @param {string} tag - Dataset tag to delete
 * @returns {Promise} Success message
 */
export const deleteDataset = async (tag) => {
  const response = await apiClient.delete(`/datasets/${encodeURIComponent(tag)}`);
  return response.data;
};

/**
 * Check API health
 * @returns {Promise} Health status
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * DEMO: Load demo data from hardcoded path
 * @returns {Promise} Success message
 */
export const loadDemoData = async () => {
  const response = await apiClient.post('/demo/load');
  return response.data;
};

/**
 * DEMO: Clean all data from database
 * @returns {Promise} Success message
 */
export const cleanDemoData = async () => {
  const response = await apiClient.post('/demo/clean');
  return response.data;
};

/**
 * Generate summary for a dataset using LLM
 * @param {string} tag - Dataset tag
 * @param {string} unitFilter - Unit filter ("All" or specific unit)
 * @param {string} sheetType - Sheet type to summarize
 * @param {string} promptTemplate - Custom prompt template with {metadata} and {data} placeholders
 * @returns {Promise} Summary response with generated text
 */
export const generateSummary = async (tag, unitFilter, sheetType, promptTemplate) => {
  const response = await apiClient.post('/generate-summary', {
    tag,
    unit_filter: unitFilter,
    sheet_type: sheetType,
    prompt_template: promptTemplate,
  });
  return response.data;
};
/**
 * Get list of available models from Ollama
 * @returns {Promise} Array of available models
 */
export const getAvailableModels = async () => {
  const response = await apiClient.get('/models/available');
  return response.data;
};

/**
 * Get current loaded model information
 * @returns {Promise} Current model details
 */
export const getCurrentModel = async () => {
  const response = await apiClient.get('/models/current');
  return response.data;
};

/**
 * Load a specific model into Ollama
 * @param {string} modelName - Name of the model to load
 * @returns {Promise} Load response with success status
 */
export const loadModel = async (modelName) => {
  const response = await apiClient.post('/models/load', {
    name: modelName,
  });
  return response.data;
};
export { apiClient };
export default apiClient;
