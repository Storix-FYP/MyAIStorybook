'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseSpeechToTextOptions {
    language?: string;
    continuous?: boolean;
    onTranscript?: (transcript: string) => void;
}

interface UseSpeechToTextReturn {
    isListening: boolean;
    transcript: string;
    interimTranscript: string;
    error: string | null;
    isSupported: boolean;
    startListening: () => void;
    stopListening: () => void;
    resetTranscript: () => void;
}

// ─── WAV encoding helpers (pure JS, no ffmpeg needed) ───────────────

function writeString(view: DataView, offset: number, str: string) {
    for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
    }
}

function floatTo16BitPCM(view: DataView, offset: number, input: Float32Array) {
    for (let i = 0; i < input.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
}

function encodeWAV(samples: Float32Array, sampleRate: number): Blob {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    // RIFF header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(view, 8, 'WAVE');

    // fmt sub-chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);            // SubChunk1Size (PCM = 16)
    view.setUint16(20, 1, true);             // AudioFormat (PCM = 1)
    view.setUint16(22, 1, true);             // NumChannels (mono)
    view.setUint32(24, sampleRate, true);     // SampleRate
    view.setUint32(28, sampleRate * 2, true); // ByteRate = SampleRate * NumChannels * BitsPerSample/8
    view.setUint16(32, 2, true);             // BlockAlign = NumChannels * BitsPerSample/8
    view.setUint16(34, 16, true);            // BitsPerSample

    // data sub-chunk
    writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);
    floatTo16BitPCM(view, 44, samples);

    return new Blob([buffer], { type: 'audio/wav' });
}

function mergeFloat32Arrays(chunks: Float32Array[]): Float32Array {
    const totalLength = chunks.reduce((acc, c) => acc + c.length, 0);
    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
        merged.set(chunk, offset);
        offset += chunk.length;
    }
    return merged;
}

// ─── Hook ───────────────────────────────────────────────────────────

export const useSpeechToText = (options: UseSpeechToTextOptions = {}): UseSpeechToTextReturn => {
    const {
        language = 'en-US',
        continuous = false,
        onTranscript
    } = options;

    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [interimTranscript, setInterimTranscript] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isSupported, setIsSupported] = useState(false);

    const streamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const pcmChunksRef = useRef<Float32Array[]>([]);
    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const isRecordingRef = useRef(false);

    // Silence detection config
    const SILENCE_THRESHOLD = 0.02;
    const SILENCE_DURATION = 2000; // Stop after 2s of silence

    // Check browser support on mount
    useEffect(() => {
        const hasMediaDevices = typeof window !== 'undefined' &&
            typeof navigator !== 'undefined' &&
            !!navigator.mediaDevices &&
            typeof navigator.mediaDevices.getUserMedia === 'function';
        setIsSupported(hasMediaDevices);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            cleanupResources();
        };
    }, []);

    const cleanupResources = () => {
        if (silenceTimeoutRef.current) {
            clearTimeout(silenceTimeoutRef.current);
            silenceTimeoutRef.current = null;
        }
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        analyserRef.current = null;
        isRecordingRef.current = false;
    };

    const sendAudioToWhisper = async (audioBlob: Blob) => {
        try {
            const formData = new FormData();
            // Send as .wav — Whisper reads WAV natively, no ffmpeg needed
            formData.append('audio', audioBlob, 'recording.wav');
            formData.append('language', language.split('-')[0]);

            const response = await fetch('http://localhost:8000/api/stt', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('STT request failed');
            }

            const result = await response.json();
            const newText = result.text;

            if (newText) {
                const updated = continuous ? `${transcript} ${newText}`.trim() : newText;
                setTranscript(updated);

                if (onTranscript) {
                    onTranscript(updated);
                }
            }

        } catch (err) {
            console.error('Whisper transcription error:', err);
            setError('Failed to transcribe audio');
        }
    };

    const finishRecording = useCallback(async () => {
        if (!isRecordingRef.current) return;
        isRecordingRef.current = false;
        setIsListening(false);
        setInterimTranscript('Processing...');

        // Encode captured PCM samples to WAV
        const chunks = pcmChunksRef.current;
        if (chunks.length > 0) {
            const sampleRate = audioContextRef.current?.sampleRate || 44100;
            const allSamples = mergeFloat32Arrays(chunks);
            const wavBlob = encodeWAV(allSamples, sampleRate);
            await sendAudioToWhisper(wavBlob);
        }

        setInterimTranscript('');
        pcmChunksRef.current = [];
        cleanupResources();
    }, [continuous, language, onTranscript, transcript]);

    const monitorAudioLevel = useCallback(() => {
        if (!analyserRef.current) return;

        const analyser = analyserRef.current;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        let frameId: number;

        const checkAudioLevel = () => {
            if (!analyserRef.current || !isRecordingRef.current) {
                return;
            }

            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length / 255;

            if (average < SILENCE_THRESHOLD) {
                if (!silenceTimeoutRef.current) {
                    silenceTimeoutRef.current = setTimeout(() => {
                        console.log('[STT] Auto-stopping after silence');
                        finishRecording();
                    }, SILENCE_DURATION);
                }
            } else {
                if (silenceTimeoutRef.current) {
                    clearTimeout(silenceTimeoutRef.current);
                    silenceTimeoutRef.current = null;
                }
            }

            frameId = requestAnimationFrame(checkAudioLevel);
        };

        checkAudioLevel();

        return () => {
            if (frameId) cancelAnimationFrame(frameId);
        };
    }, [finishRecording]);

    const startListening = useCallback(async () => {
        if (!navigator.mediaDevices) {
            setError('Speech recognition is not supported in this browser');
            return;
        }

        try {
            setError(null);
            if (!continuous) {
                setTranscript('');
            }
            setInterimTranscript('Listening...');

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            audioContextRef.current = audioContext;

            const source = audioContext.createMediaStreamSource(stream);

            // ── Analyser for silence detection ──
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;
            analyserRef.current = analyser;
            source.connect(analyser);

            // ── ScriptProcessor to capture raw PCM samples ──
            // (We record mono PCM → encode to WAV → send to Whisper)
            const processor = audioContext.createScriptProcessor(4096, 1, 1);
            processorRef.current = processor;
            pcmChunksRef.current = [];

            processor.onaudioprocess = (e: AudioProcessingEvent) => {
                if (isRecordingRef.current) {
                    const channelData = e.inputBuffer.getChannelData(0);
                    pcmChunksRef.current.push(new Float32Array(channelData));
                }
            };

            source.connect(processor);
            // ScriptProcessorNode requires connection to destination to work
            processor.connect(audioContext.destination);

            isRecordingRef.current = true;
            setIsListening(true);

            monitorAudioLevel();

        } catch (err) {
            console.error('Error starting recording:', err);
            setError('Failed to access microphone');
            setIsListening(false);
            setInterimTranscript('');
        }
    }, [continuous, language, onTranscript, transcript, monitorAudioLevel]);

    const stopListening = useCallback(() => {
        finishRecording();
    }, [finishRecording]);

    const resetTranscript = useCallback(() => {
        setTranscript('');
        setInterimTranscript('');
        setError(null);
    }, []);

    return {
        isListening,
        transcript,
        interimTranscript,
        error,
        isSupported,
        startListening,
        stopListening,
        resetTranscript
    };
};

export default useSpeechToText;
