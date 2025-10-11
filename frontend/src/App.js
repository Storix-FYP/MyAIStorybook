// src/App.js
import React, { useState, useEffect } from "react";
import StoryInput from "./components/StoryInput";
import StoryDisplay from "./components/StoryDisplay";
import "./App.css";

const loadingMessages = [
  "Awakening the Storyteller...",
  "Gathering stardust and moonbeams...",
  "Dreaming up characters and quests...",
  "Painting scenes with vibrant colors...",
  "The final chapter is being written...",
];

const LoadingExperience = () => {
  const [message, setMessage] = useState(loadingMessages[0]);

  useEffect(() => {
    let messageIndex = 0;
    const interval = setInterval(() => {
      messageIndex = (messageIndex + 1) % loadingMessages.length;
      setMessage(loadingMessages[messageIndex]);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-overlay">
      <div className="loading-animation"></div>
      <p className="loading-text">{message}</p>
    </div>
  );
};

function App() {
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <>
      {loading && <LoadingExperience />}
      <div className="app-container">
        {/* Background decorative elements */}
        {!story && (
          <div className="background-decoration">
            <div className="floating-book book-1">📖</div>
            <div className="floating-book book-2">✨</div>
            <div className="floating-book book-3">🪄</div>
            <div className="floating-book book-4">🌟</div>
          </div>
        )}
        
        {!story ? (
          <StoryInput
            onStoryGenerated={(newStory) => {
              setStory(newStory);
              setError(null);
            }}
            setLoading={setLoading}
            setError={setError}
          />
        ) : (
          <StoryDisplay story={story} onReset={() => setStory(null)} />
        )}
      </div>
    </>
  );
}

export default App;