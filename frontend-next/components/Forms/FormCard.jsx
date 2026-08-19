'use client'

import { useState, useEffect} from "react";

import { useRouter } from "next/navigation";
import { RiSurveyLine } from "react-icons/ri";
import { FaLocationArrow } from "react-icons/fa";
import { FaCopy } from "react-icons/fa";
import { RiDeleteBinFill } from "react-icons/ri";
import { FaEdit } from "react-icons/fa";

import { getRespCountbyID }from "@/api/forms";
import { getFormbyID } from "@/api/forms";
import { SaveForm } from "@/api/forms";
import { DeleteForm } from "@/api/forms";

import dynamic from "next/dynamic";

const SurveyCSVExport = dynamic(
    () => import("@/components/Forms/SurveyCSVExport"),
    {
        ssr: false,
    }
);

// form contains -> id, title, description, schema_json, total_questions and created_at.

export default function FormCard({ form, index, refreshForms}) {
    const dateObj = new Date(form.created_at);
    const navigate = useRouter();

    const [total_responses, setResponses] = useState(0);
    
    useEffect(() => {
        async function load() {
            const data = await getRespCountbyID(form.id);
            setResponses(data.count);
        }
        load();
    }, []);


    // Function that creates a Duplicate form on single click
    const duplicateForm = async () => {
        try {
            // 1. Get the form schema via GET form_id
            const data = await getFormbyID(form.id);

            const form_schema = {
                title: data.title + " - COPY",
                description: data.description,
                pages: data.schema_json
            };

            // 2. Create a new form via POST form
            await SaveForm(form_schema);
        }
        catch (err) {
            console.error(err);
            alert("Unable to delete form.");
        }
        finally{
            await refreshForms();          // This will reload the Forms page
        }
    };

    // Function that DELETES a form on single click
    const deleteForm = async () => {
        const confirmed = window.confirm(`Delete "${form.title}"?`);

        if (!confirmed) return;

        try {
            await DeleteForm(form.id);
        }
        catch (err) {
            console.error(err);
            alert("Unable to delete form.");
        }
        finally{
            await refreshForms();          // This will reload the Forms page
        }
    };


    return (
        // Card div; Card level formatting
        <div className="bg-zinc-900
                        rounded-xl py-5 pl-4 pr-8 border border-[#28545d] 
                        transition-all duration-500 ease-out 
                        hover:-translate-y-2 hover:shadow-xl 
                        hover:shadow-[#28545d]/25 
                        hover:bg-[#020c0e]">

            {/* To compartmentalise the Card internals */}
            <div className="mt-2 mb-2 grid max-w-9xl items-center gap-3 px-2 lg:grid-cols-[13%_60%_27%]">
                {/* 1. Form Number */}
                <div className="flex items-center">
                    <RiSurveyLine className="w-20 h-28 text-white transition-transform 
                                            duration-900 hover:-rotate-30"
                                />
                    <h1 className="text-4xl">{index}.</h1>
                </div>

                {/* 2. Form details */}
                <div className="text-left font-mono">
                    <span className="text-[32px] font-mono font-bold text-white mb-5">
                        {form.title}
                    </span>

                    <p className="text-gray-400 mt-2 mb-5">
                        {form.description}
                    </p>

                    <div className="mt-11 mb-2 grid max-w-9xl items-center gap-3 px-0 
                                    lg:grid-cols-[60%_40%]">
                        <div className="text-[18px] font-mono font-semibold text-gray-200">
                            <span>Total Questions: {form.total_questions}</span><br></br>
                            <span>Responses: {total_responses || 0}</span><br></br>
                            <span>Created: {dateObj.toLocaleDateString()}</span>

                        </div>

                        {/* Button to open the form for filling */}
                        <button 
                        className="flex items-center m-auto gap-2 rounded-lg border 
                                    px-5 py-2 text-lg 
                                    bg-[#020c0e]
                                    hover:bg-white
                                    hover:text-zinc-800" 
                        onClick={() => navigate.push(`/fillform?id=${form.id}`)}>
                            <span className="text-lg"><FaLocationArrow /></span> Open Form
                        </button>
                    </div>

                </div>

                {/* 3. Operations on Form - Delete / Duplicate / Edit */}
                <div className="flex flex-col items-center gap-2">
                    {/* Button to Duplicate the form */}
                    <button 
                    className="flex items-center m-auto gap-4 rounded-lg border 
                                px-6 py-2 text-[20px] w-56 h-10
                                text-black
                                bg-[#ffffff]
                                hover:bg-green-300" 
                    onClick={duplicateForm}>
                        <span className="w-5 h-5"><FaCopy /></span> Duplicate Form
                    </button>

                    {/* Button to Delete the form */}
                    <button 
                    className="flex items-center m-auto gap-4 rounded-lg border 
                                px-6 py-2 text-[20px] w-56 h-10
                                text-black
                                bg-[#ffffff]
                                hover:bg-red-300" 
                    onClick={deleteForm}>
                        <span className="w-5 h-5"><RiDeleteBinFill /></span> Delete Form
                    </button>

                    {/* Button to Edit the form */}
                    <button 
                    className="relative flex items-center m-auto gap-4 rounded-lg border 
                                px-6 py-2 text-[20px] w-56 h-10
                                text-black
                                bg-[#ffffff]
                                hover:bg-[#79dbee]" 
                    onClick={() => navigate.push(`/edit-form?id=${form.id}`)}>
                        <span className="w-5 h-5"><FaEdit /></span> Edit Form
                    </button>

                    <div>
                        { total_responses >= 5 ? <SurveyCSVExport form={form}/> : ""}
                    </div>

                </div>

            </div>
        </div>
    );
};


