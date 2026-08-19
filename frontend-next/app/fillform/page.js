'use client'

import { useEffect, useState } from "react";
// import { useSearchParams } from "next/navigation";

import { Survey } from "survey-react-ui";
import { Model } from "survey-core";
import "survey-core/survey-core.css";
import voxformTheme from "@/components/builder/themes/survey_theme_fill";

import FormTitle from "@/components/Forms/FormTitle";
import FormToolbar from "@/components/Forms/FormToolbar";
import VoicePanel from "@/components/Voice/VoicePanel";

import { saveResponse } from "@/api/forms";
import { getFormbyID } from "@/api/forms";


export default function FillForm() {
    // const searchParams = useSearchParams();
    // const form_id = searchParams.get("id");

    const [form_id, setFormID] = useState("");
    const [error, setError] = useState("");
    const [form, setForm] = useState(null);     // Entire data recieved from API 
    const [model, setModel] = useState(null);   // Data sent to Survey Model for loading the Form

    useEffect(() => {
        try {
            // Only runs in the browser, completely safe from static pre-rendering
            const searchParams = new URLSearchParams(window.location.search);
            const f_id = searchParams.get('id');

            setFormID(f_id);    // keep using f_id inside useEffect hook cause it takes time to set Form ID

            async function load() {
                // -------------------------- Get Form to Load --------------------------------
                const data = await getFormbyID(f_id);
                setForm(data);

                const json = {
                    completedHtml: "<h3>Thanks for completing the Survey!</h3>",
                    pages: data.schema_json
                };

                const survey = new Model(json);
                survey.applyTheme(voxformTheme);

                // ------------ Callback for saving the Survey Response ------------------------
                survey.onComplete.add(async (sender) => {
                    try {
                        const json = {answers: sender.data};
                        await saveResponse({
                            formId: f_id,
                            answers: json                // here, "sender.data" is same as "model.data",
                        });                              // that stores all the survey answers.

                    }
                    catch(err){
                        console.error(err);
                    }
                    finally {
                        const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                        await sleep(2500); 

                        load();
                }
                });

                setModel(survey);
            }
            load();
        } catch (error) {
            // Extract error message from Axios response
            if (error.response?.status === 401) {
              setError("Session over. Log In again.");

            } else if (error.response?.status === 400) {
              setError("Not a User. Sign Up Now.");

            } else if (error.response?.status === 404) {
              setError("Form not Found!");

            } else {
              const errorMessage = error.response?.data?.detail || "Some error. Log in Now.";
              setError(errorMessage);
            }
        }

    }, []);


    if (!model)
        return <div className="mt-20 text-[40px] font-arial font-semibold">Loading the Form... </div>;

    if (error) {
        return (
            <div className="text-red-400 text-2xl">
                {error}
            </div>
        );
    }


    return (
        <div className="text-white overflow-hidden py-10">
        
            <main className="relative z-10">
                <FormTitle
                    title={form.title}
                    description={form.description} />
                <FormToolbar 
                        form_id={form_id}
                        />
            </main>
            
            <section className="mt-2 mb-2 grid max-w-9xl gap-5 px-6 lg:grid-cols-[60%_40%]">
                
                {/* Survey Form to be filled */}
                <Survey model={model} />

                {/* VoicePanel to handle Mic and watch transcription */}
                <div className="mt-5 mb-2">
                    <VoicePanel 
                        FormID={form.id}
                        Survey={model} />
                </div>

            </section>
            
        </div>
    );
}