import React, { useState } from "react";
import { API_ENDPOINTS } from "../../utils/constants";
import "./StoryInput.css";

interface StoryInputProps {
  onStoryGenerated: (story: any) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const StoryInput: React.FC<StoryInputProps> = ({ onStoryGenerated, setLoading, setError }) => {
  const [prompt, setPrompt] = useState<string>("");
  const [generateImages, setGenerateImages] = useState<boolean>(true);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (): Promise<void> => {
    if (!prompt.trim()) {
      setLocalError("Please provide an idea to spark the magic!");
      return;
    }
    setLoading(true);
    setLocalError(null);
    setError(null);
    
    try {
      const res = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, generate_images: generateImages }),
      });
      
      if (!res.ok) throw new Error(`The magic faltered. Please try a different idea.`);
      
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
        <div className="toggle-switch">
          <label className="switch">
            <input
              type="checkbox"
              checked={generateImages}
              onChange={(e) => setGenerateImages(e.target.checked)}
            />
            <span className="slider"></span>
          </label>
          <span>Illustrate My Story</span>
        </div>
      </div>
      
      <button className="generate-button" onClick={handleSubmit}>
        Weave Magic
      </button>

      {localError && <p className="error-message">{localError}</p>}
    </div>
  );
};

export default StoryInput;
