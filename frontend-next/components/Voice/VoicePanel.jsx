'use client'

import { useState } from "react";
import MicRecorder from "./MicRecorder";
import { processVoice } from "@/api/voice";
import AudioWave from "./AudioWave"


export default function VoicePanel({ FormID, Survey }) {
    // Survey Schema in JSON format
    // const schema = Survey.toJSON();
    // Current Form data:
    // const formData = Survey.data
    // console.log(schema);
    // console.log(formData);
    // console.log(FormID);

    const [processing, setProcessing] = useState(false);
    const [message, setMessage] = useState("Hold to Speak...!");

    const [error, setError] = useState("");
    const [transcript, setTranscript] = useState("");
    const [duration, setDuration] = useState(0);

    const [stream, setStream] = useState(null);
    const [recording, setRecording] = useState(false);

    // Handle Voice Processing & dynamic Survey Updates
    const handleRecordingComplete = async ({audioBlob, mimeType, size, duration}) => {

        // Remove previous transcript
        setTranscript("");
        setDuration(duration);
        setError("");

        // Reject short recordings
        if (duration < 3) {
            setError("Recording is too short. Record for atleast 3 secs.");
            return;
        }

        try {
            setProcessing(true);

            const result = await processVoice({
                formID: FormID,
                audio: audioBlob,
            });

            // Show transcribed text in a box below Mic Button
            setTranscript(result.transcript);

            // Fill LLM returned JSON (using transcribed text) in the Survey form:
            result.extracted.forEach(element => {
                if (element.answer) {
                    Survey.setValue(element.name, element.answer);
                }
            });

            } catch (err) {
                console.error(err);
                setError("Unable to process the recording. Try Again!");
            } finally {
                setProcessing(false);
            }
    };

    return (
        <div className="flex flex-col items-center gap-2">

            {/* Mic Button & Timer and Waveform canvas: */}
            <div className="relative w-full h-40 flex items-center justify-center">
                <MicRecorder
                    onRecordingStart={(stream)=>{
                        setStream(stream);
                        setRecording(true);
                    }}
                    onRecordingStop={()=>{
                        setRecording(false);
                    }}
                    onRecordingComplete={handleRecordingComplete}
                />
                <AudioWave 
                    stream={stream}
                    recording={recording}
                />
            </div>

            {/* Instructions and Processing Message: */}
            <div className="w-full mt-0 mb-5
                            text-l
                            font-mono
                            text-slate-400
                            tracking-widest
                            h-10">
                {message}
            </div>

            {/* Error Message: */}
            <div className="w-full mt-0 mb-5
                            text-l
                            font-arial
                            text-red-300
                            tracking-widest">
                {!recording ? error : ""}
            </div>

            {/* Transcript Box : */}
            <div className="w-full min-h-40 rounded-lg border border-slate-700 px-4">
                <p className="text-xl font-arial text-slate-100">
                    Transcript
                </p>

                <p className="text-l font-mono text-slate-500">
                    {!recording ? transcript : `Transcribed text will appear here...`}
                </p>
            </div>

        </div>
    );
}
