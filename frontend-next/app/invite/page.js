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

import WelcomeCard from "@/components/WelcomeCard";
import InviteForm from "@/components/Invite/InviteForm";

import { getUserDetails } from "@/api/auth";


export default function Invite() {

  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadUser() {
        try {
          // 1. Get the user details
            const user = await getUserDetails();
            setCurrentUser(user);

        }
        catch {
            setError("Unable to load user.");
        }
        finally {
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

  const isAdmin = currentUser?.role === "org_admin";


  return (

    <div className="min-h-screen bg-zinc-950 text-white">

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-10">
        {/* 1. Welcome Card */}
        <WelcomeCard user={currentUser} />

        <InviteForm />

      </main>

    </div>
  );
}