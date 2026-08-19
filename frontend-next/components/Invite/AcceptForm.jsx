'use client'

/*
|--------------------------------------------------------------------------
| Login Card
|--------------------------------------------------------------------------
*/

import { useState } from "react";
import { useRouter } from 'next/navigation';

import { acceptInvite } from "@/api/invite";

import { RiMic2AiLine } from "react-icons/ri";

export default function AcceptanceForm({user, token}) {

  const navigation = useRouter();

  // Form field state
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Real-time password validation logic
  const isPasswordEmpty = password1 === "" || password2 === "";
  const doPasswordsMatch = password1 === password2 && !isPasswordEmpty;

  const [submission, setSubmission] = useState(false);

  

  /*
  |--------------------------------------------------------------------------
  | Handle Invitation and New User Creation
  |--------------------------------------------------------------------------
  */
  async function handleSubmission(event) {
    event.preventDefault();

    // Prevent submission if passwords do not match
    if (!doPasswordsMatch) {
      setError("Passwords do not match!");
      console.log(`${token} ------ ${password2}`);
      return;
    }

    setLoading(true);
    setError("");


    try {
      // Axios throws automatically for 4xx/5xx errors
      const response = await acceptInvite(token, password2);
      setSubmission(true);
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
        Create Password
      </h1>

      <span className="mt-2 text-zinc-500 text-[18px] font-mono font-medium font-italic">
        Complete your onbaording &rarr; Log-In to VoxForm &rarr; Start filling Voice Forms!
      </span>

      <form
        className="mt-8 space-y-5 "
        onSubmit={handleSubmission}
      >

        <input
          type="password"
          placeholder="Enter Password"
          value={password1}
          onChange={(e) => setPassword1(e.target.value)}
          required
          className="w-full rounded-xl text-[20px] text-zinc-100 border border-zinc-700 bg-zinc-900/70 p-3 outline-none focus:border-sky-500"
        />

        <div className="relative">
          <input
            type="password"
            placeholder="Re-enter Password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            required
            className={`w-full rounded-xl text-[20px] text-zinc-100 border bg-zinc-900/70 p-3 outline-none transition-colors ${
              doPasswordsMatch 
                ? "border-emerald-500 focus:border-emerald-500" 
                : "border-zinc-700 focus:border-sky-500"
            }`}
          />
          
          {/* Green Indicator Label/Signal */}
          {doPasswordsMatch && (
            <p className="mt-1.5 text-sm text-emerald-400 font-medium flex items-center gap-1">
              ✓ Passwords match
            </p>
          )}
          
          {/* Optional: Warning if they don't match yet (only after user typed in both) */}
          {!doPasswordsMatch && !isPasswordEmpty && (
            <p className="mt-1.5 text-sm text-red-400 font-medium">
              ✗ Passwords do not match
            </p>
          )}
        </div>


        {/* Visual Anchor for Error Message */}

        {error && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sl text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !doPasswordsMatch}
          className="w-full rounded-xl bg-sky-500 py-4 mb-10 font-semibold text-2xl transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Submitting Password & Adding User..." : "Submit"}
        </button>

      </form>

      {submission ? (
        <div className="mt-4 z-20 rounded-3xl border border-white/200 bg-white/200 pt-8 pb-10 
                        backdrop-blur-xl shadow-[0_0_60px_rgba(14,165,233,0.12)]">
            <span className="mt-2 text-zinc-100 text-[28px]/12 font-arial font-medium font-italic">
                Congratualtions! You are added to <span className="border rounded-lg p-1 text-sky-400" >
                  {user.org_name}</span>
            </span>
            <br></br>

            <span className="mt-2 text-green-400 text-[20px]/12 font-mono font-bold font-italic">
                Now Log-In to VoxForm. Click below!
            </span>
            <br></br>
            <br></br>

            <button className="inline-flex items-center gap-2 rounded-lg bg-[#4aafaf] border border-white 
                              px-4 py-2 text-[22px] text-black font-semibold hover:bg-[#13333d] 
                              hover:text-white"
                onClick={() => navigation.push("/")}>
                <RiMic2AiLine /> VoxForm AI
            </button>

        </div>) : ""}

    </div>

  );
};
