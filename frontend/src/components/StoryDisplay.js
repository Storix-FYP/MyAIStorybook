// src/components/StoryDisplay.js
import React, { useState } from "react";
import "./StoryDisplay.css";

const ArrowLeftIcon = () => (
  <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"></path></svg>
);

const ArrowRightIcon = () => (
  <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"></path></svg>
);

export default function StoryDisplay({ story, onReset }) {
  const [page, setPage] = useState(0); // 0 is cover
  const scenes = story.scenes || [];
  const totalPages = scenes.length;
  const sceneIndex = page - 1;
  const currentScene = scenes[sceneIndex] || {};

  if (!story) return null;

  // Extract characters and setting from the first scene or use defaults
  const firstScene = scenes[0] || {};
  const characters = story.characters || extractCharacters(firstScene.text);
  const setting = story.setting || extractSetting(firstScene.text);

  function extractCharacters(text) {
    if (!text) return ["Main Character"];
    // Simple extraction - you can enhance this with AI or more sophisticated parsing
    const names = text.match(/\b[A-Z][a-z]+\b/g) || ["The Protagonist"];
    return [...new Set(names)].slice(0, 3); // Get unique names, max 3
  }

  function extractSetting(text) {
    if (!text) return "A mysterious world";
    // Simple setting extraction
    if (text.includes('village')) return "A peaceful village";
    if (text.includes('forest')) return "An enchanted forest";
    if (text.includes('city')) return "A bustling city";
    if (text.includes('sea') || text.includes('ocean')) return "The vast seas";
    if (text.includes('mountain')) return "Majestic mountains";
    return "A magical realm";
  }

  return (
    <>
      <button className="reset-button" onClick={onReset}>
        Start Anew
      </button>

      <div className="storybook-container">
        {page > 0 && (
          <div className="page-turn-arrow left" onClick={() => setPage(p => p - 1)}>
            <ArrowLeftIcon />
          </div>
        )}

        <div className="page image-page">
          {page > 0 && currentScene.image_url ? (
            <img
              key={page}
              src={`http://localhost:8000${currentScene.image_url}`}
              alt={`Illustration for scene ${currentScene.scene_number}`}
              className="storybook-image"
              style={{animation: 'fadeIn 0.7s ease'}}
            />
          ) : page === 0 ? (
            <div className="cover-page">
              <h2 className="cover-title">{story.title}</h2>
              <p className="cover-subtitle">by MyAIStorybook</p>
            </div>
          ) : (
            <div className="no-illustration">
              <p>No illustration for this page</p>
            </div>
          )}
        </div>

        <div className="page text-page">
          {page > 0 ? (
            <div key={page} style={{animation: 'fadeIn 0.7s ease', height: '100%'}}>
              <p>{currentScene.text}</p>
              <div className="page-indicator">
                Page {page} of {totalPages}
              </div>
            </div>
          ) : (
            // Cover page right side - Story Details
            <div className="story-details">
              

              <div className="details-section">
                <h3 className="details-title">🏰 Setting</h3>
                <p className="details-content">
                  {setting}
                </p>
              </div>

              <div className="details-section">
                <h3 className="details-title">🎭 Main Characters</h3>
                <div className="characters-list">
                  {characters.map((character, index) => (
                    <div key={index} className="character-item">
                      <span className="character-bullet">•</span>
                      <span className="character-name">{character}</span>
                    </div>
                  ))}
                </div>
              </div>

              

              <div className="begin-reading">
                <button 
                  className="begin-button"
                  onClick={() => setPage(1)}
                >
                  Begin Reading →
                </button>
                <p className="page-count">
                  {totalPages} captivating pages await
                </p>
              </div>
            </div>
          )}
        </div>

        {page < totalPages && (
          <div className="page-turn-arrow right" onClick={() => setPage(p => p + 1)}>
            <ArrowRightIcon />
          </div>
        )}
      </div>
    </>
  );
}