"use client";

import { useState } from "react";
import { getResponses } from "@/api/responses";
import { FaFileDownload } from "react-icons/fa";

/**
 * Convert a value into a CSV-safe string.
 */
function csvValue(value) {
    if (value === null || value === undefined) {
        return "";
    }

    // Arrays → readable comma-separated value
    if (Array.isArray(value)) {
        value = value.join(", ");
    }

    // Objects → JSON string
    if (typeof value === "object") {
        value = JSON.stringify(value);
    }

    value = String(value);

    // Escape CSV-special characters
    if (
        value.includes(",") ||
        value.includes('"') ||
        value.includes("\n") ||
        value.includes("\r")
    ) {
        value = `"${value.replace(/"/g, '""')}"`;
    }

    return value;
}


/**
 * Trigger browser download.
 */
function downloadCSV(content, filename) {
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

    // Give browser time to start download
    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 100);
}


export default function SurveyResponseExporter({ form }) {

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

            // --------------------------------------------------
            // 1. Get all normalized responses
            // --------------------------------------------------

            const responseResult = await getResponses(form.id);

            const responses = responseResult.answers;

            if (!Array.isArray(responses)) {
                throw new Error(
                    "Response API did not return an array of responses."
                );
            }


            // --------------------------------------------------
            // 2. Handle empty responses
            // --------------------------------------------------

            if (responses.length === 0) {
                throw new Error(
                    "There are no responses to export for this form."
                );
            }


            // --------------------------------------------------
            // 3. Get all CSV columns
            // --------------------------------------------------
            //
            // Since the responses are already normalized, the
            // response keys themselves are now the column names.
            //
            // Example:
            //
            // {
            //     "First Name": "Vishal",
            //     "Last Name": "Mandrai",
            //     "Gender": "Male"
            // }
            //
            // becomes:
            //
            // First Name,Last Name,Gender
            //
            // --------------------------------------------------

            const columns = [
                ...new Set(
                    responses.flatMap((response) =>
                        Object.keys(response)
                    )
                ),
            ];


            if (columns.length === 0) {
                throw new Error(
                    "No response fields were found to export."
                );
            }


            // --------------------------------------------------
            // 4. Create CSV header
            // --------------------------------------------------

            const header = columns
                .map(csvValue)
                .join(",");


            // --------------------------------------------------
            // 5. Create CSV rows
            // --------------------------------------------------

            const rows = responses.map((response) => {

                return columns
                    .map((column) => {
                        return csvValue(response?.[column]);
                    })
                    .join(",");

            });


            // --------------------------------------------------
            // 6. Create final CSV
            // --------------------------------------------------

            const csv = [
                header,
                ...rows,
            ].join("\r\n");


            // --------------------------------------------------
            // 7. Add UTF-8 BOM for Excel
            // --------------------------------------------------

            const csvWithBom = "\uFEFF" + csv;


            // --------------------------------------------------
            // 8. Download CSV
            // --------------------------------------------------

            downloadCSV(
                csvWithBom,
                `form_${form.id}_responses.csv`
            );


        } catch (err) {

            console.error(
                "Failed to export responses:",
                err
            );

            const message =
                err instanceof Error
                    ? err.message
                    : "Failed to export responses.";

            setError(message);

        } finally {

            setIsExporting(false);

        }
    };


    return (
        <div className="mt-4">

            <button
                type="button"
                className="
                    relative flex items-center m-auto gap-4
                    rounded-lg border
                    px-6 py-2 text-[20px]
                    w-56 h-10
                    text-black
                    bg-[#ffffff]
                    hover:bg-zinc-950
                    hover:text-white
                "
                onClick={handleExport}
                disabled={isExporting}
            >

                <span className="w-5 h-5">
                    <FaFileDownload />
                </span>

                {isExporting
                    ? "Exporting..."
                    : "Export CSV"
                }

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