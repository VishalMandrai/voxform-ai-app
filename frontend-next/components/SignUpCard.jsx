'use client'

/*
|--------------------------------------------------------------------------
| Login Card
|--------------------------------------------------------------------------
*/

import { useState } from "react";

// NEXT Equivalent of -> import { useNavigate } from "react-router-dom";
import { useRouter } from 'next/navigation';

import { signup } from "@/api/auth"


export default function SignUpCard() {

  // React Router navigation hook
  // const navigate = useNavigate();
  const navigate = useRouter();

  // Form field state
  const [fullName, setName] = useState("");
  const [org, setOrg] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");



  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");


  /*
  |--------------------------------------------------------------------------
  | Handle Login
  |--------------------------------------------------------------------------
  | Sends user credentials to FastAPI.
  | On success:
  |   - FastAPI sets an HTTP-only session cookie.
  |   - React navigates to the dashboard.
  |
  | On failure:
  |   - Displays the backend error message.
  |--------------------------------------------------------------------------
  */
  async function handleSignup(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      // Axios throws automatically for 4xx/5xx errors
      const response = await signup(fullName, org, email, password);

      setMessage(`${response.full_name} - Sign Up successful! Now Log In.`)

      // Login successful.
      // Cookie has already been stored by the browser.
      //   navigate.push("/");

    } catch (error) {
      // Extract error message from Axios response
      const errorMessage = error.response?.data?.detail || "Invalid email or password.";
      setError(errorMessage);

    } 
    finally {
      setLoading(false);
      
    }
  }

  return (
    <main>
      <div className="rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl shadow-[0_0_60px_rgba(14,165,233,0.12)]">

        <h2 className="text-3xl font-bold">
          Sign Up
        </h2>

        <form
          className="mt-5 space-y-2"
          onSubmit={handleSignup}
        >
        <input
            type="text"
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full rounded-xl text-[20px] border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
          />
        
        <input
            type="text"
            placeholder="Organisation Name"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            required
            className="w-full rounded-xl text-[20px] border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-xl text-[20px] border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
          />

          <input
            type="password"
            placeholder="Password (min 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-xl text-[20px] border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
          />

          {/* Visual Anchor for Error Message */}

          {error && (
            <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sl text-red-300">
              {error}
            </div>
          )}

          {!error && message && (
            <div className="rounded-lg border border-green-500/40 bg-green-500/10 p-3 text-sl text-green-300">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-sky-500 mt-3 py-3 px-10 font-semibold transition hover:bg-sky-400 text-xl font-black disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Signing Up..." : "Sign Up"}
          </button>

        </form>

      </div>

      <div className="m-25 mt-9 mb-5">
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl px-7 py-4 font-semibold transition hover:bg-sky-500 
                    text-xl font-black cursor:pointer disabled:opacity-60"
          onClick={() => navigate.push("/")}
        >
          Log In
        </button>
      </div>


    </main>

  );
}

