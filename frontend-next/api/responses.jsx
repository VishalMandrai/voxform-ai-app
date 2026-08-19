import api from "./axios";

// GET all the forms available for a USER
export async function getResponses(form_id) {
    
    try {
        const response = await api.get(`/api/analytics/forms/responses/${form_id}`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch forms:", error);
        throw error;
    }
}