import api from "./axios";

// GET all the forms available for a USER
export async function getForms() {
    
    try {
        const response = await api.get('/api/forms');
        return response.data;
    } catch (error) {
        console.error("Failed to fetch forms:", error);
        throw error;
    }
}


// POST a newly created Form to save
export async function SaveForm(data) {
    try {
        const response = await api.post('/api/forms', data);
        return response.data;
    } catch (error) {
        console.error("Failed to save the form. Error - ", error);
        throw error;
    }
}


// GET a form based on Form ID
export async function getFormbyID(form_id) {
    try {
        const response = await api.get(`/api/forms/${form_id}`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch the form:", error);
        throw error;
    }
}


// POST a Form Response for Saving
export async function saveResponse({formId, answers}) {
    try {
        const response = await api.post(`/api/forms/${formId}/responses`, answers);
        return response.data;
    } catch (error) {
        console.error("Failed to save the form response. Error - ", error);
        throw error;
    }
}


// GET total form responses based on Form ID
export async function getRespCountbyID(form_id) {
    try {
        const response = await api.get(`/api/forms/${form_id}/responsecount`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch the form:", error);
        throw error;
    }
}


// DELETE a form based on Form ID
export async function DeleteForm(form_id) {
    try {
        const response = await api.delete(`/api/forms/${form_id}`);
        return response.data;
    } catch (error) {
        console.error("Failed to delete the form:", error);
        throw error;
    }
}
