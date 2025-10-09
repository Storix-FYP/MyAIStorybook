// src/components/StoryInput.js
import React, { useState } from "react";
import "./StoryInput.css";

export default function StoryInput({ onStoryGenerated, setLoading, setError }) {
  const [prompt, setPrompt] = useState("");
  const [generateImages, setGenerateImages] = useState(true);
  const [localError, setLocalError] = useState(null); // Add local error state

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setLocalError("Please provide an idea to spark the magic!"); // Use local error
      return;
    }
    setLoading(true);
    setLocalError(null); // Clear local error
    setError(null); // Clear parent error
    try {
      const res = await fetch("http://localhost:8000/api/generate", {
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
      setLocalError(err.message); // Use local error
      setError(err.message); // Also set parent error if needed
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="story-input-wrapper">
      <h2>Begin Your Adventure</h2>
      <p>Whisper an idea, and watch a world unfold.</p>
      
      <div className="input-field-container">
        <textarea
          className="main-prompt-input"
          placeholder="A cat who learns to sail the seas..."
          value={prompt}
          onChange={(e) => {
            setPrompt(e.target.value);
            setLocalError(null); // Clear error when user types
          }}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSubmit()}
          rows="3"
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

      {/* Fix: Show localError instead of setError */}
      {localError && <p className="error-message">{localError}</p>}
    </div>
  );
}