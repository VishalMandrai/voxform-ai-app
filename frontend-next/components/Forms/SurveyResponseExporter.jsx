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
            // 1. Get all responses
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
            // 3. Validate and normalize responses
            // --------------------------------------------------
            //
            // Input:
            //
            // [
            //     [
            //         {"question1": "Aditya"},
            //         {"question2": "Rana"},
            //         {"question4": "1999-12-03"},
            //         {"question3": "Item 1"}
            //     ],
            //     [
            //         {"question1": "Aditya"},
            //         {"question2": "Rana"},
            //         {"question4": "1999-12-03"},
            //         {"question3": "Item 1"}
            //     ]
            // ]
            //
            // Each inner list becomes one response object.
            //
            // --------------------------------------------------

            const normalizedResponses = responses.map((responseList) => {

                if (!Array.isArray(responseList)) {
                    throw new Error(
                        "Invalid response format: each response must be an array."
                    );
                }

                return responseList.reduce(
                    (responseObject, answer) => {

                        if (
                            answer &&
                            typeof answer === "object" &&
                            !Array.isArray(answer)
                        ) {
                            Object.assign(responseObject, answer);
                        }

                        return responseObject;

                    },
                    {}
                );

            });


            // --------------------------------------------------
            // 4. Get CSV columns
            // --------------------------------------------------
            //
            // IMPORTANT:
            //
            // The order of columns follows the order in which
            // keys appear in the original response lists.
            //
            // The first occurrence of a key determines its
            // column position.
            //
            // Example:
            //
            // [
            //     {"question1": "Aditya"},
            //     {"question2": "Rana"},
            //     {"question4": "1999-12-03"},
            //     {"question3": "Item 1"}
            // ]
            //
            // produces:
            //
            // question1, question2, question4, question3
            //
            // --------------------------------------------------

            const columns = [
                ...new Set(
                    responses.flatMap((responseList) =>
                        responseList.flatMap((answer) =>
                            Object.keys(answer)
                        )
                    )
                ),
            ];


            if (columns.length === 0) {
                throw new Error(
                    "No response fields were found to export."
                );
            }


            // --------------------------------------------------
            // 5. Create CSV header
            // --------------------------------------------------

            const header = columns
                .map(csvValue)
                .join(",");


            // --------------------------------------------------
            // 6. Create CSV rows
            // --------------------------------------------------

            const rows = normalizedResponses.map((response) => {

                return columns
                    .map((column) => {
                        return csvValue(response?.[column]);
                    })
                    .join(",");

            });


            // --------------------------------------------------
            // 7. Create final CSV
            // --------------------------------------------------

            const csv = [
                header,
                ...rows,
            ].join("\r\n");


            // --------------------------------------------------
            // 8. Add UTF-8 BOM for Excel
            // --------------------------------------------------

            const csvWithBom = "\uFEFF" + csv;


            // --------------------------------------------------
            // 9. Download CSV
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