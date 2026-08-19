'use client'

import { useEffect, useRef } from "react";

export default function AudioWave({ stream, recording }) {

    const canvasRef = useRef(null);
    const animationRef = useRef(null);
    const analyserRef = useRef(null);
    const audioContextRef = useRef(null);

    useEffect(() => {

        console.log("Wave effect", recording, stream);

        if (!recording || !stream)
            return;

        const canvas = canvasRef.current;

        const ctx = canvas.getContext("2d");

        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;

        const source = audioContext.createMediaStreamSource(stream);

        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;

        analyserRef.current = analyser;

        source.connect(analyser);

        const bufferLength = analyser.frequencyBinCount;

        const data = new Uint8Array(bufferLength);

        const draw = () => {

            animationRef.current = requestAnimationFrame(draw);
            analyser.getByteTimeDomainData(data);
            // analyser.getByteFrequencyData(data);
            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );

            ctx.lineWidth = 3.2;
            ctx.strokeStyle = "#69e7de";
            // Dash pattern: 8px line, 6px gap
            // ctx.setLineDash([5, 4]);
            
            ctx.beginPath();

            const slice = canvas.width / bufferLength;

            let x = 0;
            for (let i = 0; i < bufferLength; i++) {
                const v = data[i] / 128.0;
                const centerY = canvas.height / 2;
                const gain = 3;
                const y = centerY + (v - 1) * centerY * gain;

                // const y = (v * canvas.height) / 2;

                if (i === 0)
                    ctx.moveTo(x, y);
                else
                    ctx.lineTo(x, y);

                x += slice;
            }

            ctx.lineTo(
                canvas.width,
                canvas.height / 2
            );

            ctx.stroke();
        };

        draw();

        return () => {
            cancelAnimationFrame(animationRef.current);
            // audioContext.close();
            source.disconnect();
            analyser.disconnect();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        };

    }, [stream, recording]);

    return (
        <canvas
            ref={canvasRef}
            width={600}
            height={100}
            className="absolute w-full h-full inset-0 rounded-lg pointer-events-none"
        />
    );
}