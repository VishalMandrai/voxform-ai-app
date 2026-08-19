'use client'

import { useRef, useState, useEffect } from "react";
import { Mic } from "lucide-react";

export default function MicRecorder({ 
    onRecordingComplete, 
    onRecordingStart,
    onRecordingStop,
    disabled = false }) {
    const [isRecording, setIsRecording] = useState(false);

    const mediaRecorderRef = useRef(null);
    const streamRef = useRef(null);
    const chunksRef = useRef([]);

    // Variable to calculate duration
    const startedAtRef = useRef(0);

    // Variables for recording timer
    const [elapsed, setElapsed] = useState(0);
    const intervalRef = useRef(null);

    const formattedTime = `${String(Math.floor(elapsed / 60)).padStart(2, "0")}:${String(elapsed % 60).padStart(2, "0")}`;

    /**
     * Get microphone stream once and reuse it.
     * Instead of creating a new microphone stream for every recording, we can acquire the stream once 
     * and reuse it. We still create a new MediaRecorder for each recording session (since a stopped 
     * MediaRecorder can't be restarted), but the underlying microphone stream remains open until the
     * component unmounts.
    */
    const getMicrophoneStream = async () => {
        if (streamRef.current) {
            return streamRef.current;
        }
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
        });
        streamRef.current = stream;

        return stream;
    };


    const startRecording = async () => {
        if (disabled || isRecording) return;

        try {
            const stream =  await getMicrophoneStream();
            streamRef.current = stream;

            // Send the stream for Waveform Canvas:
            onRecordingStart?.(stream);

            const recorder = new MediaRecorder(stream, {
                mimeType: "audio/webm",
            });
            mediaRecorderRef.current = recorder;
            chunksRef.current = [];

            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunksRef.current.push(event.data);
                }
            };

            recorder.onstop = () => {
                const duration = ((Date.now() - startedAtRef.current) / 1000);

                // Sending stop signal to Waveform when recording is stopped:
                onRecordingStop?.();

                const blob = new Blob(chunksRef.current, {
                    type: "audio/webm",
                });
                // Send the recorded audio to backend
                onRecordingComplete?.({
                                        audioBlob:blob,
                                        mimeType: blob.type,
                                        size: blob.size,
                                        duration: duration
                                    });

                mediaRecorderRef.current = null;
                chunksRef.current = [];
                // console.log("Mic Stopped.....")
            };

            recorder.start();
            startedAtRef.current = Date.now();                  // recording start time

            // Recording Timer settings:
            setElapsed(0);

            intervalRef.current = setInterval(() => {
                setElapsed(
                    Math.floor((Date.now() - startedAtRef.current) / 1000)
                );
            }, 200);

            // console.log(`Mic Recording.....`)

            setIsRecording(true);
        } catch (err) {
            console.error("Microphone access denied:", err);
        }
    };

    const stopRecording = () => {
        // Recording Timer:
        clearInterval(intervalRef.current);
        intervalRef.current = null;

        if (!isRecording) return;
        setIsRecording(false);

        if (
            mediaRecorderRef.current &&
            mediaRecorderRef.current.state !== "inactive"
        ) {
            mediaRecorderRef.current.stop();
        }
    };

    /**
     * Cleanup when component unmounts.
     */
    useEffect(() => {
        return () => {
            // Cleanup Recording Timer:
            clearInterval(intervalRef.current);

            // Cleanup and close Stream on unmount:
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
                streamRef.current = null;
                startedAtRef.current = 0;
            }
        };
    }, []);

    return (
        <div className="relative z-100">
            <button
                type="button"
                disabled={disabled}
                onMouseDown={startRecording}
                onMouseUp={stopRecording}
                onMouseLeave={() => {
                    if (isRecording) stopRecording();
                }}
                onTouchStart={(e) => {
                    e.preventDefault();
                    startRecording();
                }}
                onTouchEnd={(e) => {
                    e.preventDefault();
                    stopRecording();
                }}
                onTouchCancel={stopRecording}
                className={`
                    w-25 h-20 z-10 rounded-full mb-2
                    flex items-center justify-center
                    transition-all duration-200
                    select-none

                    ${
                        isRecording
                            ? "bg-red-600 scale-110 shadow-lg shadow-red-500/20"
                            : "bg-sky-500 hover:bg-sky-800"
                    }

                    disabled:opacity-50
                    disabled:cursor-not-allowed
                `}
            >
                <Mic className={`w-12 h-12 text-white transition-transform duration-900 
                                ${isRecording ? 'rotate-360' : 'rotate-0'}`} />
            </button>
            <span
                className="
                    mt-12 rounded-full bg-slate-900 px-4
                    border
                    text-sm
                    font-mono
                    text-slate-400
                    tracking-widest
                    h-10
                "
            >
                {isRecording ? formattedTime : "00:00"}
            </span>
        </div>
    );
}
