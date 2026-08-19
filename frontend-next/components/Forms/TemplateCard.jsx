'use client'

import { useEffect, useState } from "react";

import { RiSurveyLine } from "react-icons/ri";
import { FaLocationArrow } from "react-icons/fa";

import { SaveForm } from "@/api/forms";


export default function TemplateCard({ form, index}) {

    const [loading, setLoading] = useState(false);
    const [formAdded, setFormAdded] = useState(false);

    // Function that creates a Duplicate form on single click
    const addForm = async () => {
        setLoading(true);
        try {
            // 1. Create a new form via POST form
            const form_schema = {
                title: form.title,
                description: form.description,
                pages: form.schema,
            };

            await SaveForm(form_schema);
        }
        catch (err) {
            console.error(err);
            alert("Unable to Add Survey to your Forms.");
        }
        finally {
            setFormAdded(true);
        }
    };


    return (
        // Card div; Card level formatting
        <div className="bg-[#020c0e]
                        rounded-xl py-5 pl-4 pr-8 border border-[#28545d] 
                        transition-all duration-500 ease-out 
                        hover:-translate-y-2 hover:shadow-xl 
                        hover:shadow-[#28545d]/25 
                        hover:bg-[#020c0e]">

            {/* To compartmentalise the Card internals */}
            <div className="mt-2 mb-2 grid max-w-9xl items-center gap-3 px-2 lg:grid-cols-[13%_87%]">
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
                            <span>Created: {form.created_on}</span>

                        </div>

                        {/* Button to open the form for filling */}
                        <button 
                        className={`inline-flex items-center m-auto gap-2 rounded-lg border 
                                    px-5 py-2 text-lg bg-[#020c0e] transition-colors
                                    ${loading ? 'hover:bg-white hover:text-green-800' : 'hover:bg-white hover:text-zinc-950'}`} 
                        onClick={addForm}>
                            { loading ? ( formAdded ? (
                                <div className="flex items-center">
                                    <span className="text-lg"><FaLocationArrow /></span> &nbsp; Added!
                                </div>
                            ) : (
                                <div  className="flex items-center">
                                    <span className="text-lg"><FaLocationArrow /></span> &nbsp; Adding...
                                </div>
                            )
                            ) : (
                                <div  className="flex items-center">
                                    <span className="text-lg"><FaLocationArrow /></span> &nbsp; Add Survey
                                </div>
                            )
                            }
                        </button>
                    </div>

                </div>
                
            </div>
        </div>
    );
};


