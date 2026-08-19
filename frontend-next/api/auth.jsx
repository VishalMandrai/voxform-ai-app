/*
|--------------------------------------------------------------------------
| Authentication API
|--------------------------------------------------------------------------
*/

import api from "./axios";

/*
|--------------------------------------------------------------------------
| Sign Up
|--------------------------------------------------------------------------
|
| POST /api/auth/signup
|
*/

export async function signup(full_name, org_name, email, password) {
  try {
    const response = await api.post("/api/auth/signup", {full_name, org_name, email, password});
    return response.data;
} catch (error) {
        console.error("Failed in Sign Up:", error);
        throw error;
    }
}

/*
|--------------------------------------------------------------------------
| Login
|--------------------------------------------------------------------------
|
| POST /api/auth/login
| Returns the logged-in user.
| FastAPI also sets the HTTP-only session cookie.
|
*/

export async function login(email, password) {
  try {
    const response = await api.post("/api/auth/login", {email, password});
    return response.data;
} catch (error) {
        console.error("Failed to fetch the user:", error);
        throw error;
    }
}

/*
|--------------------------------------------------------------------------
| Logout
|--------------------------------------------------------------------------
*/

export async function logout() {
  try {
    const response = await api.post("/api/auth/logout");
    return response.data;
} catch (error) {
        console.error("Failed to logout.", error);
        throw error;
    }
}

/*
|--------------------------------------------------------------------------
| Get Current Logged-in User
|
| Uses the HTTP-only session cookie sent automatically by Axios.
|--------------------------------------------------------------------------
*/

export async function getCurrentUser() {
  try {
    const response = await api.get("/api/auth/me");
    return response.data;
} catch (error) {
        console.error("Failed to fetch the user:", error);
        throw error;
    }
}

/*
|--------------------------------------------------------------------------
| Get Complete details of a Logged-in User
|--------------------------------------------------------------------------
*/

export async function getUserDetails() {
  try {
    const response = await api.get("/api/auth/userfulldet");
    return response.data;
  } catch (error) {
          console.error("Failed to fetch the user details:", error);
          throw error;
  }
}


/*
|--------------------------------------------------------------------------
| Get All Users in a Org
|--------------------------------------------------------------------------
*/

export async function getUsers() {
  try {
    const response = await api.get("/api/auth/users");
    return response.data;
} catch (error) {
        console.error("Failed to fetch users:", error);
        throw error;
    }
}


/*
|--------------------------------------------------------------------------
| Get All Invitations sent by the Org
|--------------------------------------------------------------------------
*/

export async function getAllInvites() {
  try {
    const response = await api.get("/api/auth/invites/all");
    return response.data;
} catch (error) {
        console.error("Failed to fetch users:", error);
        throw error;
    }
}
