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
import { useRouter } from 'next/navigation';

import WelcomeCard from "@/components/WelcomeCard";
import StatsGrid from "@/components/StatsGrid";
import ActionGrid from "@/components/ActionGrid";
import RecentForms from "@/components/RecentForms";
import MembersCard from "@/components/MembersCard";

import { getUserDetails, getUsers, getAllInvites } from "@/api/auth";
import { getStats } from "@/api/analytics";


export default function Home() {

  const navigation = useRouter();
  
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [loginButton, setLoginButton] = useState(false);
  const [SignUpButton, setSignUpButton] = useState(false);

  const [userStats, setUserStats] = useState(null);
  const [members, setMembers] = useState(null);
  const [invites, setInvites] = useState(null);


  useEffect(() => {
    // Setting Tab Title
    document.title = 'Home | VoxForm AI';

    async function loadUser() {
        try {
          // 1. Get User Info:
          const user = await getUserDetails();
          setCurrentUser(user);

          // 2. Get User Stats:
          const stats = await getStats();
          setUserStats(stats);

          // 3. Get Members:
          const mems = await getUsers();
          setMembers(mems);

          // 4. Get Invite Count:
          const invites = await getAllInvites();
          setInvites(invites);
        } catch (error) {
            // Extract error message from Axios response
            if (error.response?.status === 401) {
              setError("Session over. Log In again.");
              setLoginButton(true);

            } else if (error.response?.status === 400) {
              setError("Not a User. Sign Up Now.");
              setSignUpButton(true);

            } else if (error.response?.status === 404) {
              setError("Log In to continue.");
              setLoginButton(true);

            } else {
              const errorMessage = error.response?.data?.detail || "Some error. Log in Now.";
              setError(errorMessage);
              setLoginButton(true);
            }
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
        <div className="text-red-400 text-2xl">
            {error}
            <div className="flex justify-center items-center mt-12">
              {loginButton ? 
                <button className="rounded-lg bg-sky-400 px-4 py-2 text-black 
                                  text-bold hover:bg-[#13333d] hover:text-white cursor-pointer"
                        onClick={() => navigation.push("/")}>
                      Log In
                </button>
              : ""
              }
            </div>

            <div className="flex justify-center items-center mt-12">
              {SignUpButton ? 
                <button className="rounded-lg bg-sky-400 px-4 py-2 text-black 
                                  text-bold hover:bg-[#13333d] hover:text-white cursor-pointer"
                        onClick={() => navigation.push("/sign-up")}>
                      Sign Up
                </button>
              : ""
              }
            </div>
        </div>
    );
  }

  const isAdmin = currentUser?.role === "org_admin";


  return (

    <div className="min-h-screen bg-zinc-950 text-white">

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-10">
        {/* 1. Welcome Card */}
        <WelcomeCard user={currentUser} />

        {/* 2. Stats Grid */}
        {isAdmin && <StatsGrid 
                          total_forms = {userStats.total_forms}
                          total_responses = {userStats.total_responses}
                          total_members = {members.length}
                          total_invites = {invites.total_invites}
                          />}

        {/* 3. Action Cards */}
        <ActionGrid isAdmin={isAdmin} />

        {/* 4. Recent forms  and All Members card */}
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <RecentForms 
                    forms = {userStats.forms}
                    />
          </div>

          {isAdmin && (
            <MembersCard members = {members}/>
          )}

        </div>
      </main>

    </div>
  );
}
