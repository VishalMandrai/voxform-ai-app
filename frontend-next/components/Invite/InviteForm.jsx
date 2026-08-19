'use client'

/*
|--------------------------------------------------------------------------
| Login Card
|--------------------------------------------------------------------------
*/

import { useState } from "react";

import { createInvite } from "@/api/invite";


export default function InviteForm() {

  // Form field state
  const [full_name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");

  // Invite
  const [invitation, setInvitation] = useState(false);
  const [inviteData, setInvitationData] = useState(null);


  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
  async function handleInvitation(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      // Axios throws automatically for 4xx/5xx errors
      const response = await createInvite(full_name, email, role);

      setInvitation(true);
      setInvitationData(response);

    } 
    catch (error) {
      // Extract error message from Axios response
      const errorMessage = error.response?.data?.detail || "Problem with creating Invitation. Try after some time.";
      setError(errorMessage);

    } 
    finally {
      setLoading(false);
    }
  }

  return (

    <div className="rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl shadow-[0_0_60px_rgba(14,165,233,0.12)]">

      <h1 className="text-3xl font-bold">
        Invite New Member
      </h1>

      <span className="mt-2 text-zinc-500 text-[20px]/12 font-calibiri font-medium font-italic">
        Provide new member's information &rarr; Generate invite link &rarr; Ask member to complete onboarding
      </span>

      <form
        className="mt-8 space-y-5 "
        onSubmit={handleInvitation}
      >

        <input
          type="text"
          placeholder="Full Name"
          value={full_name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full rounded-xl text-[20px] text-zinc-100 border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full rounded-xl text-[20px] text-zinc-100 border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
        />

        <select
        value={role}
        onChange={(e) => setRole(e.target.value)}
        required
        className="w-full rounded-xl text-[20px] border border-zinc-700 bg-zinc-900 p-3 text-white outline-none focus:border-sky-500 appearance-none"
        >
        <option value="" disabled className="bg-zinc-900">Select Role</option>
            <option value="org_admin" className="bg-zinc-900 text-white">Org Admin</option>
            <option value="respondent" className="bg-zinc-900 text-white">Respondent</option>
        </select>

        {/* Visual Anchor for Error Message */}

        {error && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sl text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-sky-500 py-4 mb-10 font-semibold text-2xl transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Creating New Invite Link..." : "Create Invite"}
        </button>

      </form>

      {invitation ? (
        <div className="mt-4 z-20 rounded-3xl border border-white/200 bg-white/200 pt-8 pb-10 
                        backdrop-blur-xl shadow-[0_0_60px_rgba(14,165,233,0.12)]">
            <span className="mt-2 text-zinc-100 text-[24px]/12 font-calibiri font-medium font-italic">
                Share this LINK with the registered Member to complete the onboarding!
            </span>
            <br></br>

            <span className="mt-2 text-red-400 text-[20px]/12 font-mono font-bold font-italic">
                Link will only be shown once.
            </span>
            <br></br>
            <br></br>

            <span className="border rounded-xl border-zinc-300 p-4 mt-2 text-white text-[18px]/12 
                            font-mono font-medium bg-black-900">
                {window.location.origin}/accept-invite/?id={inviteData.token}
            </span>
        </div>
                ) : ""}

      {/* {invitation ? inviteData.token : "No Invitation...!"} */}

    </div>

  );
};

