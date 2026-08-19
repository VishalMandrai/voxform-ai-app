"use client";   

/*
|--------------------------------------------------------------------------
| Home Page
|--------------------------------------------------------------------------
|
| Main dashboard shown after successful Login.
| The UI adapts based on the logged-in user's role.
|
*/
import { useEffect, useState } from "react";
// import { useSearchParams } from "next/navigation";

import IntroCard from "@/components/Invite/IntroCard";
import AcceptForm from "@/components/Invite/AcceptForm";

import { getTokenDetails } from "@/api/invite";


export default function AcceptInvite() {

  // Get the token from URL:
  // const searchParams = useSearchParams();
  // const token = searchParams.get("id");

  const [token, setToken] = useState(null);
  const [currentToken, setCurrentToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Only runs in the browser, completely safe from static pre-rendering
    const searchParams = new URLSearchParams(window.location.search);
    const token_from_url = searchParams.get('id');

    setToken(token_from_url);

    async function loadUser() {
      // Prevent running the API call if token is not available yet
      if (!token_from_url) return; 

      try {
        // 1. Get the token details
          const user = await getTokenDetails(token_from_url);
          setCurrentToken(user);

      } catch (error) {
        const errorMessage = error.response?.data?.detail || "Unable to load the Invitation completetion form.";
        setError(errorMessage);

      } finally {
          setLoading(false);
      }
    }
    loadUser();

  }, []);

  if (loading) {
    return (
        <div className="flex items-center justify-center text-white text-[52px]">
            Loading...
        </div>
    );
  }

  if (error) {
    return (
        <div className="flex min-h-screen items-center justify-center bg-zinc-950 text-red-400">
            {error}
        </div>
    );
  }


  return (

    <div className="min-w-5xl min-h-screen bg-zinc-950 text-white">

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-5">
        {/* 1. Introduction Card */}
        <IntroCard user={currentToken} />

        <AcceptForm 
                user={currentToken}
                token={token}
                />
      </main>

    </div>
  );

}
