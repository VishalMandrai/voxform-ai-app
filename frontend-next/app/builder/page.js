"use client";   
// We'll keep this page as a Client Component

//                              Builder Page Layout
// ┌────────────────────────────────────────────────────────────────────────────┐
// │ Navbar                                                             Profile │
// ├────────────────────────────────────────────────────────────────────────────┤
// │                                                                            │
// │  Form Builder                                         Auto Saved ✓         │
// │  Build powerful voice-enabled forms                                   Save │
// │────────────────────────────────────────────────────────────────────────────│
// │                                                                            │
// │  + New Form     Preview     Publish     AI Generate     Voice Test         │
// │                                                                            │
// ├────────────────────────────────────────────────────────────────────────────┤
// │                                                                            │
// │                         SurveyJS Creator                                   │
// │                                                                            │
// │  ┌────────────┐ ┌─────────────────────────────┐ ┌──────────────────────┐   │
// │  │ Toolbox    │ │                             │ │ Properties           │   │
// │  │            │ │                             │ │                      │   │
// │  │ Text       │ │        Form Canvas          │ │ Question Settings    │   │
// │  │ Checkbox   │ │                             │ │ Validation           │   │
// │  │ Dropdown   │ │                             │ │ Logic                │   │
// │  │ Matrix     │ │                             │ │ Required             │   │
// │  │ File       │ │                             │ │ Placeholder          │   │
// │  │ Signature  │ │                             │ │ ...                  │   │
// │  │ ...        │ │                             │ │                      │   │
// │  └────────────┘ └─────────────────────────────┘ └──────────────────────┘   │
// │                                                                            │
// └────────────────────────────────────────────────────────────────────────────┘

/*
|--------------------------------------------------------------------------
| Form Builder Page
|--------------------------------------------------------------------------
|
| Visual drag-and-drop form designer powered by SurveyJS.
| This page serves as the workspace where users can build,
| preview, and later publish voice-enabled forms.
|
*/
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

import BuilderHeader from "@/components/Builder/BuilderHeader";
import BuilderToolbar from "@/components/Builder/BuilderToolbar";

import { getCurrentUser } from "@/api/auth";

const SurveyCreatorWidget = dynamic(
  () => import("@/components/Builder/SurveyCreatorPanel"),
  {
    ssr: false,
    loading: () => <p>Loading Survey Creator...</p>,
  }
);


export default function Builder() {
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [loginButton, setLoginButton] = useState(false);
    const [SignUpButton, setSignUpButton] = useState(false);

    const reloadBuilder = async () => {
        window.location.reload();
    };

    useEffect(() => {
    // Setting Tab Title
    document.title = 'Builder | VoxForm AI';

    async function loadUser() {
        try {
            // 1. Get User Info:
            const user = await getCurrentUser();

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

    return (
        <div className="h-[134vh] text-white overflow-hidden">

            {/* Page */}
            <main className="relative z-10">
                {/* Page Title */}
                <BuilderHeader />

                {/* Toolbar */}
                <BuilderToolbar 
                    reloadBuilder = {reloadBuilder}
                    />
                
                {/* SurveyJS Creator */}
                <main className="h-[calc(110vh-80px)] w-full">
                    <SurveyCreatorWidget />
                </main>
            </main>

        </div>
    );
}