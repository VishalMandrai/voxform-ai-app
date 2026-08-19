import api from "./axios";

// GET all the forms available for a USER
export async function getStats() {
    
    try {
        const response = await api.get('/api/analytics/overview');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch forms:", error);
        throw error;
    }
}