import api from "./axios";


// POST new memeber details to generate new-token and invitation link ---------------------
export async function createInvite(full_name, email, role) {
    
    try {
        const response = await api.post('/api/auth/invites', {full_name, email, role});
        return response.data;
    } catch (error) {
        console.error("Failed to create the invitation:", error);
        throw error;
    }
}



// GET detials of new user from generated token -------------------------------------------
export async function getTokenDetails(token) {
    
    try {
        const response = await api.get(`/api/auth/invites/accept/${token}`);
        return response.data;
    } catch (error) {
        console.error("Failed to get the Token Details for the invitation:", error);
        throw error;
    }
}



// POST to accept the Invitation for nem membwe --------------------------------------------
export async function acceptInvite(token, password) {
    try {
        const response = await api.post(`/api/auth/invites/accept`, {token, password});
        return response.data;
    } catch (error) {
        console.error("Failed to save the form. Error - ", error);
        throw error;
    }
}
