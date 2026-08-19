"use client";   
// We'll keep this page as a Client Component

/*
|--------------------------------------------------------------------------
| Forms Page
|--------------------------------------------------------------------------
|
| Select all the saved and prvided forms from the list and start filling.
| This page serves as the workspace where users can find created forms,
| fill, and save forms.
|
*/

import { useEffect, useState } from "react";
import FormCard from "@/components/Forms/FormCard";
import { getForms } from "@/api/forms";

export default function Forms() {

    const [forms, setForms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [loginButton, setLoginButton] = useState(false);
    const [SignUpButton, setSignUpButton] = useState(false);

    useEffect(() => {
        // Setting Tab Title
        document.title = 'My Forms | VoxForm AI';

        async function load() {
            try {
                const data = await getForms();
                setForms(data);
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
                const errorMessage = error.response?.data?.detail || "Unable to Load the Forms. Try Again.";
                setError(errorMessage);
                setLoginButton(true);
                }
            }
            finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const refreshForms = async () => {
        const data = await getForms();
        setForms(data);
    };

    
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
        <div className="p-2">
            <div className="text-white overflow-hidden mb-5 mt-10">
                <main className="relative z-10 border-b border-[#13333d] pb-10">
                    <h1 className="mt-2 mb-22 text-3xl font-bold text-slate-800">
                        My Forms
                    </h1>
                    <br></br>

                    <span className="mt-1 text-3xl text-slate-500">
                        All forms in one place for easy access and management
                    </span>
                </main>
            </div>

            {/* <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"> */}
            <div className="mx-auto mt-10 grid grid-cols-1 gap-4 md:ml-[0%] xl:ml-[0%]">
                {forms.map((form, index) => (
                    <FormCard
                        key={form.id}
                        form={form}
                        index={index + 1}
                        refreshForms={refreshForms}
                    />
                ))}
            </div>
        </div>
    );
}