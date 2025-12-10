'use client';

import React, { useState, useEffect, useRef } from 'react';
import './WorkshopPage.css';

interface Message {
    role: 'user' | 'assistant';
    message: string;
    metadata?: any;
}

interface WorkshopPageProps {
    mode: 'improvement' | 'new_idea';
    onBack: () => void;
    onStoryGenerated?: (story: string) => void;
}

export const WorkshopPage: React.FC<WorkshopPageProps> = ({ mode, onBack, onStoryGenerated }) => {
    const [sessionId, setSessionId] = useState<number | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [userInput, setUserInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [readyToGenerate, setReadyToGenerate] = useState(false);
    const [generatedStory, setGeneratedStory] = useState<string | null>(null);
    const [storyVersion, setStoryVersion] = useState(1);
    const [wordCount, setWordCount] = useState(0);
    const [isInitializing, setIsInitializing] = useState(true);
    const [connectionError, setConnectionError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initialize session
    useEffect(() => {
        // Scroll to top when component mounts
        window.scrollTo({ top: 0, behavior: 'smooth' });

        const initSession = async () => {
            setIsInitializing(true);
            setConnectionError(null);
            try {
                const response = await fetch('http://127.0.0.1:8000/api/workshop/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode })
                });

                if (!response.ok) {
                    throw new Error('Failed to start workshop');
                }

                const data = await response.json();
                setSessionId(data.session_id);
                setMessages([{
                    role: 'assistant',
                    message: data.initial_message
                }]);
            } catch (error) {
                console.error('Error starting workshop:', error);
                setConnectionError('Unable to connect to the workshop server. Please make sure the backend is running.');
                setMessages([{
                    role: 'assistant',
                    message: 'Welcome! I\'m here to help you craft your story. Please share your ideas and let\'s create something magical together! ✨'
                }]);
            } finally {
                setIsInitializing(false);
            }
        };

        initSession();
    }, [mode]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Word count for improvement mode
    useEffect(() => {
        if (mode === 'improvement') {
            setWordCount(userInput.trim().split(/\s+/).filter(w => w.length > 0).length);
        }
    }, [userInput, mode]);

    const handleSendMessage = async () => {
        if (!userInput.trim() || isLoading) return;

        const message = userInput.trim();
        setUserInput('');
        setIsLoading(true);

        // Add user message optimistically
        setMessages(prev => [...prev, { role: 'user', message }]);

        if (!sessionId) {
            // If no session, just echo back for demo purposes
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    message: 'Thank you for sharing! Let me help you develop this idea further. What other details would you like to add?'
                }]);
                setIsLoading(false);
            }, 1000);
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/workshop/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    user_message: message
                })
            });

            if (!response.ok) throw new Error('Failed to send message');

            const data = await response.json();

            // Add assistant response
            setMessages(prev => [...prev, {
                role: 'assistant',
                message: data.response,
                metadata: data.metadata
            }]);

            setReadyToGenerate(data.ready_to_generate);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                message: 'I\'m having trouble connecting right now. Please try again in a moment.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGenerateStory = async () => {
        if (!sessionId) {
            alert('Session not initialized. Please refresh and try again.');
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/workshop/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (!response.ok) throw new Error('Failed to generate story');

            const data = await response.json();
            setGeneratedStory(data.story_text);
            setStoryVersion(data.version);
            if (onStoryGenerated) {
                onStoryGenerated(data.story_text);
            }
        } catch (error) {
            console.error('Error generating story:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                message: 'Unable to generate the story right now. Please try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleImproveFurther = () => {
        setGeneratedStory(null);
        setReadyToGenerate(false);
        setMessages(prev => [...prev, {
            role: 'assistant',
            message: "What would you like to improve about the story?"
        }]);
    };

    const handleAcceptStory = () => {
        alert('Story saved! Redirecting to home...');
        onBack();
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (readyToGenerate) {
                handleGenerateStory();
            } else {
                handleSendMessage();
            }
        }
    };

    const getModeDetails = () => {
        if (mode === 'improvement') {
            return {
                icon: '🔧',
                title: 'Improve My Story',
                subtitle: 'Share your story and let\'s make it even better together.',
                placeholder: 'Paste your story here or describe what you want to improve...'
            };
        }
        return {
            icon: '💡',
            title: 'Share a New Idea',
            subtitle: 'Whisper your idea, and let\'s build a magical story together.',
            placeholder: 'Describe your story idea, characters, or theme...'
        };
    };

    const modeDetails = getModeDetails();

    // Loading state
    if (isInitializing) {
        return (
            <div className="workshop-wrapper">
                <div className="workshop-loading">
                    <div className="workshop-spinner"></div>
                    <p>Setting up your creative workshop...</p>
                </div>
            </div>
        );
    }

    // Story display view
    if (generatedStory) {
        return (
            <div className="workshop-wrapper">
                <div className="workshop-header">
                    <button className="back-button" onClick={onBack}>
                        ← Back to Home
                    </button>
                    <div className="mode-badge">
                        <span className="mode-icon">{modeDetails.icon}</span>
                        <span>{modeDetails.title}</span>
                    </div>
                </div>

                <div className="workshop-card story-result-card">
                    <div className="story-result-header">
                        <h2>✨ Your Generated Story</h2>
                        <span className="version-badge">Version {storyVersion}</span>
                    </div>
                    <div className="story-result-content">
                        {generatedStory}
                    </div>
                    <div className="story-result-actions">
                        <button className="action-button primary" onClick={handleAcceptStory}>
                            ✓ I Love It!
                        </button>
                        {mode === 'improvement' && (
                            <button className="action-button secondary" onClick={handleImproveFurther}>
                                🔧 Improve Further
                            </button>
                        )}
                        <button className="action-button outline" onClick={onBack}>
                            Start Over
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Main chat view
    return (
        <div className="workshop-wrapper">
            <div className="workshop-header">
                <button className="back-button" onClick={onBack}>
                    ← Back to Home
                </button>
                <div className="mode-badge">
                    <span className="mode-icon">{modeDetails.icon}</span>
                    <span>{modeDetails.title}</span>
                </div>
            </div>

            <div className="workshop-card">
                <div className="workshop-card-header">
                    <h2>{modeDetails.title}</h2>
                    <p>{modeDetails.subtitle}</p>
                </div>

                {connectionError && (
                    <div className="connection-warning">
                        <span>⚠️</span>
                        <p>{connectionError}</p>
                    </div>
                )}

                <div className="chat-container">
                    <div className="messages-area">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}
                            >
                                <div className="message-bubble">
                                    {msg.message}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="message assistant-message">
                                <div className="message-bubble typing">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="input-area">
                        {mode === 'improvement' && wordCount > 0 && (
                            <div className={`word-count ${wordCount > 300 ? 'error' : ''}`}>
                                {wordCount}/300 words
                            </div>
                        )}
                        <div className="input-row">
                            <textarea
                                className="message-input"
                                value={userInput}
                                onChange={(e) => setUserInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder={modeDetails.placeholder}
                                rows={3}
                                disabled={isLoading}
                            />
                        </div>
                        <div className="button-row">
                            {readyToGenerate ? (
                                <button
                                    className="generate-story-button"
                                    onClick={handleGenerateStory}
                                    disabled={isLoading}
                                >
                                    ✨ Generate My Story
                                </button>
                            ) : (
                                <button
                                    className="send-message-button"
                                    onClick={handleSendMessage}
                                    disabled={!userInput.trim() || isLoading || (mode === 'improvement' && wordCount > 300)}
                                >
                                    Send Message
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WorkshopPage;
