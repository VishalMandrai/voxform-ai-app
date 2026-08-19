/*
|--------------------------------------------------------------------------
| Shared Axios Client
|--------------------------------------------------------------------------
|
| - A single Axios instance used throughout the application.
| - Automatically sends/receives the "HTTP-only" session cookie.
*/

import axios from "axios";

const api = axios.create({
  // baseURL: "http://localhost:8000",   // Use base URL only when running the frontend via Next.js
  baseURL: "",                           // When FastAPI itself serving the static build; keep it empty
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },

});

export default api;


// NOTES: for baseURL = ""
// When frontend is loaded from: http://your-server:8000
// and Axios makes: api.get("/forms")
// the browser requests: http://your-server:8000/forms
// So both frontend and backend are coming from the same origin.