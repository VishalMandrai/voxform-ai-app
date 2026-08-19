'use-client';

/*
|--------------------------------------------------------------------------
| SurveyCSVExport
|--------------------------------------------------------------------------
|
| Purpose:
|   Export all responses for a SurveyJS Form to CSV.
|
| Important:
|   - Does NOT render a response table.
|   - Uses SurveyJS Dashboard's Tabulator integration.
|   - Keeps all normalization/schema interpretation inside SurveyJS.
|   - Designed for client-side CSV generation.
|
| Props:
|
|   formId
|       ID of the form whose responses should be exported.
|
|   getForm
|       Async function that returns the saved SurveyJS schema.
|
|   getResponses
|       Async function that returns all responses for the form.
|
| Example:
|
|   <SurveyResponseExporter
|       formId={formId}
|       getForm={getFormbyID}
|       getResponses={getFormResponses}
|   />
|
|--------------------------------------------------------------------------
*/

//         VoxForm static frontend
//         ────────────────────────

// Form Page
//    │
//    └──── [ Export Responses CSV ]
//                     │
//                     ▼
//         SurveyResponseExporter
//              "use client"
//                     │
//                     ▼
//            GET /forms/{id}/responses
//                     │
//                     ▼
//               FastAPI
//                     │
//              ┌──────┴──────┐
//              │             │
//          schema_json   response_json[]
//              │             │
//              └──────┬──────┘
//                     ▼
//              SurveyJS Model
//                     │
//                     ▼
//              SurveyJS Tabulator
//                     │
//                     ▼
//                CSV export
//                     │
//                     ▼
//               Browser download
//  ------------------------------------------------------------------------------
//  ------------------------------------------------------------------------------


import { useState } from "react";
import { Model } from "survey-core";
import { Tabulator } from "survey-analytics/survey.analytics.tabulator";

import { getResponses } from "@/api/responses"

import "tabulator-tables/dist/css/tabulator.css";
import "survey-analytics/survey.analytics.tabulator.css";

import { FaFileDownload } from "react-icons/fa";

/*
|--------------------------------------------------------------------------
| CSV helpers
|--------------------------------------------------------------------------
*/

/**
 * Convert any value into a CSV-safe string.
 *
 * CSV escaping rules:
 *   - null / undefined -> ""
 *   - arrays / objects -> JSON string
 *   - values containing comma, quote or newline -> quoted
 */
function csvValue(value) {
    if (value === null || value === undefined) {
        return "";
    }

    if (Array.isArray(value)) {
        value = value.join(", ");
    }

    if (typeof value === "object") {
        value = JSON.stringify(value);
    }

    value = String(value);

    if (
        value.includes(",") ||
        value.includes('"') ||
        value.includes("\n") ||
        value.includes("\r")
    ) {
        value = `"${value.replace(/"/g, '""')}"`;
    }

    return value;
};


/**
 * Trigger a browser download from a string.
 */
function downloadTextFile(content, filename) {
    const blob = new Blob(
        [content],
        {
            type: "text/csv;charset=utf-8;",
        }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    /*
     * Give the browser a moment to start the download
     * before releasing the object URL.
     */
    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 100);
};


function getExportValue(survey, dataRow, column) {
    const field = column.field;

    if (!field) {
        return "";
    }

    const rawValue = dataRow?.[field];

    if (
        rawValue === null ||
        rawValue === undefined
    ) {
        return "";
    }

    const question =
        survey.getQuestionByName(field);

    /*
    |--------------------------------------------------------------------------
    | Choice question
    |--------------------------------------------------------------------------
    */

    if (
        question &&
        Array.isArray(question.choices)
    ) {
        const choice = question.choices.find(
            (item) => {

                const value =
                    typeof item === "object"
                        ? item.value
                        : item;

                return value === rawValue;
            }
        );

        if (choice) {
            return typeof choice === "object"
                ? choice.value
                : choice;
        }
    }

    /*
    |--------------------------------------------------------------------------
    | Non-choice question
    |--------------------------------------------------------------------------
    */

    return rawValue;
}

// ----------------------------------------------------------------------
// ----------------------------------------------------------------------


export default function SurveyResponseExporter({form}) {

    const [isExporting, setIsExporting] = useState(false);
    const [error, setError] = useState(null);

    const handleExport = async () => {
        if (!form) {
            console.error("SurveyResponseExporter: Form is missing.");
            return;
        }

        setIsExporting(true);
        setError(null);

        try {
            /*
            |--------------------------------------------------------------------------
            | 1. Create form schema
            |--------------------------------------------------------------------------
            */
            const surveyJson = {
                title: form.title,
                description: form.description,
                pages: form.schema_json,
            }

            /*
            |--------------------------------------------------------------------------
            | 2. Load all form responses from API call
            |--------------------------------------------------------------------------
            */
            const responseResult = await getResponses(form.id);

            /*
             * Again, this supports a few common API shapes.
             * We will simplify this once we see your actual API wrapper.
             */
            const surveyResults = responseResult.answers;

            if (!Array.isArray(surveyResults)) {
                throw new Error(
                    "Response API did not return an array of responses."
                );
            }

            /*
            |--------------------------------------------------------------------------
            | 3. Handle empty result set
            |--------------------------------------------------------------------------
            */

            if (surveyResults.length === 0) {
                throw new Error(
                    "There are no responses to export for this form."
                );
            }

            /*
            |--------------------------------------------------------------------------
            | 4. Create SurveyJS model
            |--------------------------------------------------------------------------
            |
            | SurveyJS needs the original form schema so it knows:
            |
            */
            const survey = new Model(surveyJson);

            /*
            |--------------------------------------------------------------------------
            | 5. Create SurveyJS Dashboard Tabulator
            |--------------------------------------------------------------------------
            */

            const surveyDataTable = new Tabulator(
                survey,
                surveyResults
            );

            // Temporary DOM container
            const container = document.createElement("div");

            container.style.position = "fixed";
            container.style.left = "-10000px";
            container.style.top = "0";
            container.style.width = "1000px";
            container.style.height = "500px";
            container.style.visibility = "hidden";

            document.body.appendChild(container);

            // Initialize underlying Tabulator
            surveyDataTable.render(container);

            /*
            |--------------------------------------------------------------------------
            | 6. Get SurveyJS-generated columns
            |--------------------------------------------------------------------------
            */

            const columns =
                surveyDataTable.getColumns();


            if (!columns || columns.length === 0) {
                throw new Error(
                    "SurveyJS did not generate any export columns."
                );
            }

            const tableData = surveyDataTable.data;

            console.log("Dashboard normalized data:", tableData);

            if (!Array.isArray(tableData) || tableData.length === 0) {
                throw new Error(
                    "SurveyJS Dashboard produced no response rows."
                );
            }

            // Remove SurveyJS internal/non-downloadable columns
            const exportColumns = columns.filter((column) => {
                return (
                    column.field &&
                    column.download !== false &&
                    column.visible !== false
                );
            });

            // CSV headers
            const headers = exportColumns.map(
                (column) => column.title || column.field
            );

            // CSV rows
            const rows = surveyResults.map((response) => {

                return exportColumns.map((column) => {

                    const value =
                        response?.[column.field];

                    return csvValue(value);
                });

            });

            // CSV content
            const csv = [
                headers.map(csvValue).join(","),
                ...rows.map((row) => row.join(",")),
            ].join("\r\n");

            // UTF-8 BOM for Excel
            const csvWithBom = "\uFEFF" + csv;

            // Download
            downloadTextFile(
                csvWithBom,
                `form_${form.id}_responses.csv`
            );

        } catch (err) {
            console.error(
                "Failed to export SurveyJS responses:",
                err
            );

            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to export responses.";

            setError(message);

        } finally {
                // surveyDataTable = null;
                setIsExporting(false);
            }
        };

    /*
    |--------------------------------------------------------------------------
    | 8. Button
    |--------------------------------------------------------------------------
    |
    | The component owns the button for now.
    |
    | You can later replace this with your VoxForm Button component.
    |
    */

    return (
        <div className="mt-4">
            <button
                type="button"
                className="relative flex items-center m-auto gap-4 rounded-lg border 
                                px-6 py-2 text-[20px] w-56 h-10
                                text-black
                                bg-[#ffffff]
                                hover:bg-zinc-950
                                hover:text-white" 
                onClick={handleExport}
                disabled={isExporting}
            >
                <span className="w-5 h-5"><FaFileDownload /></span>{isExporting
                                                            ? "Exporting..."
                                                            : "Export CSV"}
            </button>

            {error && (
                <p
                    role="alert"
                    style={{
                        color: "red",
                        marginTop: "4px",
                    }}
                >
                    {error}
                </p>
            )}
        </div>
    );
}