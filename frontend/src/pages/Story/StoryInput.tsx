'use client';

import React, { useState } from "react";
import { API_ENDPOINTS } from "@/utils/constants";
import { useAuth } from "@/contexts/AuthContext";
import "./StoryInput.css";

interface StoryInputProps {
  onStoryGenerated: (story: any) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  onShowLogin?: () => void;
}

const StoryInput: React.FC<StoryInputProps> = ({ onStoryGenerated, setLoading, setError, onShowLogin }) => {
  const { isAuthenticated, token } = useAuth();
  const [prompt, setPrompt] = useState<string>("");
  const [generateImages, setGenerateImages] = useState<boolean>(isAuthenticated);
  const [localError, setLocalError] = useState<string | null>(null);
  const [showLoginMessage, setShowLoginMessage] = useState<boolean>(false);

  const handleSubmit = async (): Promise<void> => {
    if (!prompt.trim()) {
      setLocalError("Please provide an idea to spark the magic!");
      return;
    }
    
    // Check if user is trying to generate images without being authenticated
    if (generateImages && !isAuthenticated) {
      setShowLoginMessage(true);
      setLocalError("Please login to generate images. Guest users can only create text stories.");
      return;
    }
    
    setLoading(true);
    setLocalError(null);
    setError(null);
    setShowLoginMessage(false);
    
    try {
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      
      const res = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers,
        body: JSON.stringify({ prompt, generate_images: generateImages }),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        if (res.status === 401 && errorData.detail?.includes("login")) {
          setShowLoginMessage(true);
          throw new Error("Please login to generate images. Guest users can only create text stories.");
        }
        throw new Error(errorData.detail || `The magic faltered. Please try a different idea.`);
      }
      
      const data = await res.json();
      if (data?.story) {
        onStoryGenerated(data.story);
      } else {
        throw new Error("Received a confusing scroll from the server.");
      }
    } catch (err) {
      console.error("Generation failed:", err);
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred";
      setLocalError(errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  const handleImageToggle = (checked: boolean): void => {
    if (checked && !isAuthenticated) {
      setShowLoginMessage(true);
      if (onShowLogin) {
        onShowLogin();
      }
      return;
    }
    setGenerateImages(checked);
    setShowLoginMessage(false);
    setLocalError(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="story-input-wrapper">
      <div className="story-input-header">
        <h2>Begin Your Adventure</h2>
        <p>Whisper an idea, and watch a world unfold.</p>
      </div>
      
      <div className="input-field-container">
        <textarea
          className="main-prompt-input"
          placeholder="A cat who learns to sail the seas..."
          value={prompt}
          onChange={(e) => {
            setPrompt(e.target.value);
            setLocalError(null);
          }}
          onKeyPress={handleKeyPress}
          rows={3}
        />
      </div>

      <div className="input-controls">
        <div className={`toggle-switch ${!isAuthenticated ? 'disabled' : ''}`}>
          <label className="switch">
            <input
              type="checkbox"
              checked={generateImages && isAuthenticated}
              onChange={(e) => handleImageToggle(e.target.checked)}
              disabled={!isAuthenticated}
            />
            <span className={`slider ${!isAuthenticated ? 'disabled' : ''}`}></span>
          </label>
          <span 
            className={!isAuthenticated ? 'disabled-text' : ''}
            title={!isAuthenticated ? 'Please login first to enable image generation' : ''}
          >
            Illustrate My Story
          </span>
          {!isAuthenticated && (
            <div className="illustrate-tooltip">Please login first</div>
          )}
        </div>
        {showLoginMessage && (
          <div className="login-prompt">
            <p>Please <button type="button" className="login-link" onClick={onShowLogin}>login</button> to enable image generation</p>
          </div>
        )}
      </div>
      
      <button className="generate-button" onClick={handleSubmit}>
        Weave Magic
      </button>

      {localError && <p className="error-message">{localError}</p>}
    </div>
  );
};

export default StoryInput;
