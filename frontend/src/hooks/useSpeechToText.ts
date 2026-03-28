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

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const streamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Silence detection config
    const SILENCE_THRESHOLD = 0.02; // Volume threshold for silence (increased sensitivity)
    const SILENCE_DURATION = 2000; // Stop after 2 seconds of silence

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
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
            if (silenceTimeoutRef.current) {
                clearTimeout(silenceTimeoutRef.current);
            }
        };
    }, []);

    const sendAudioToWhisper = async (audioBlob: Blob) => {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
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

    const monitorAudioLevel = useCallback(() => {
        if (!analyserRef.current) return;

        const analyser = analyserRef.current;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        let frameId: number;

        const checkAudioLevel = () => {
            // Check if recorder is still active
            if (!analyserRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
                return;
            }

            analyser.getByteFrequencyData(dataArray);

            const average = dataArray.reduce((a, b) => a + b) / dataArray.length / 255;

            console.log('[STT] Audio level:', average.toFixed(3)); // Debug log

            if (average < SILENCE_THRESHOLD) {
                if (!silenceTimeoutRef.current) {
                    console.log('[STT] Silence detected, waiting...');
                    silenceTimeoutRef.current = setTimeout(() => {
                        console.log('[STT] Auto-stopping after silence');
                        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
                            mediaRecorderRef.current.stop();
                            setIsListening(false);
                        }
                    }, SILENCE_DURATION);
                }
            } else {
                if (silenceTimeoutRef.current) {
                    console.log('[STT] Sound detected, continuing...');
                    clearTimeout(silenceTimeoutRef.current);
                    silenceTimeoutRef.current = null;
                }
            }

            frameId = requestAnimationFrame(checkAudioLevel);
        };

        checkAudioLevel();

        // Return cleanup function
        return () => {
            if (frameId) {
                cancelAnimationFrame(frameId);
            }
        };
    }, []);

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
            const analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;
            analyserRef.current = analyser;

            source.connect(analyser);

            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                setInterimTranscript('Processing...');

                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                await sendAudioToWhisper(audioBlob);

                setInterimTranscript('');
                audioChunksRef.current = [];

                if (streamRef.current) {
                    streamRef.current.getTracks().forEach(track => track.stop());
                    streamRef.current = null;
                }
                if (audioContextRef.current) {
                    audioContextRef.current.close();
                    audioContextRef.current = null;
                }
                if (silenceTimeoutRef.current) {
                    clearTimeout(silenceTimeoutRef.current);
                    silenceTimeoutRef.current = null;
                }
            };

            mediaRecorder.start();
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
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            setIsListening(false);
        }
    }, []);

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
