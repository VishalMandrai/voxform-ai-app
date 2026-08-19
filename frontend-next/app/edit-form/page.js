"use client";   
// We'll keep this page as a Client Component

/*
|--------------------------------------------------------------------------
| Form Edit Page
|--------------------------------------------------------------------------
|
| Visual drag-and-drop form designer powered by SurveyJS.
| This page serves as the workspace where users can Load and Edit forms.
|
*/
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
// import { useSearchParams } from "next/navigation";

import EditorHeader from "@/components/Edit-forms/EditorHeader";
import BuilderToolbar from "@/components/Builder/BuilderToolbar";

import { getFormbyID } from "@/api/forms";


const SurveyCreatorWidget = dynamic(
  () => import("@/components/Builder/SurveyCreatorPanel"),
  {
    ssr: false,
    loading: () => <p>Loading Survey Creator...</p>,
  }
);


export default function Editor() {
    // const searchParams = useSearchParams();
    // const form_id = searchParams.get("id");

    const [form_id, setFormID] = useState("");
    const [title, setTitle] = useState(null);        
    const [description, setDesc] = useState(null);    
    const [schema, setSchema] = useState(null);        


    useEffect(() => {
        // Only runs in the browser, completely safe from static pre-rendering
        const searchParams = new URLSearchParams(window.location.search);
        const form_id_from_url = searchParams.get('id');

        setFormID(form_id_from_url);

        async function load() {
            // -------------------------- Get Form to Load --------------------------------
            const data = await getFormbyID(form_id_from_url);

            setTitle(data.title);
            setDesc(data.description);

            const json = {
                title: data.title,
                description: data.description,
                pages: data.schema_json
            };
            setSchema(json);

        }
        load();
    
    }, []);
    
    if (!title || !description || !schema)
        return <div className="mt-20 text-[40px] font-arial font-semibold">Loading the Form... </div>;

    return (
        <div className="h-[134vh] text-white overflow-hidden">

            {/* Page */}
            <main className="relative z-10">
                {/* Page Title */}
                <EditorHeader 
                    title={title}
                    description={description}/>

                {/* Toolbar */}
                <BuilderToolbar />
                
                {/* SurveyJS Creator */}
                <main className="h-[calc(110vh-80px)] w-full">
                    <SurveyCreatorWidget 
                        json={schema}
                        />
                </main>
            </main>

        </div>
    );
}