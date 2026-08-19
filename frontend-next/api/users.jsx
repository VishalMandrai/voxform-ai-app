import api from "./axios";

export async function getCurrentUser() {
    const response = await api.get("/api/users/me");
    return response.data;

}