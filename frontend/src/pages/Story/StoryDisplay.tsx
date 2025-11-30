'use client';

import React, { useState } from "react";
import { Chatbot } from './Chatbot';
import "./StoryDisplay.css";

interface Story {
  title: string;
  setting: string;
  characters: string[];
  scenes: Array<{
    scene_number: number;
    text: string;
    image_description?: string;
    image_url?: string;
  }>;
}

interface StoryDisplayProps {
  story: Story;
  storyId: number | null;
  onReset: () => void;
}

const ArrowLeftIcon: React.FC = () => (
  <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"></path></svg>
);

const ArrowRightIcon: React.FC = () => (
  <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"></path></svg>
);

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story, storyId, onReset }) => {
  const [page, setPage] = useState<number>(0); // 0 is cover
  const scenes = story.scenes || [];
  const totalPages = scenes.length;
  const sceneIndex = page - 1;
  const currentScene = scenes[sceneIndex] || {};

  if (!story) return null;

  // Extract characters and setting from the first scene or use defaults
  const firstScene = scenes[0] || {};
  const characters = story.characters || extractCharacters(firstScene.text);
  const setting = story.setting || extractSetting(firstScene.text);

  function extractCharacters(text: string): string[] {
    if (!text) return ["Main Character"];
    // Simple extraction - you can enhance this with AI or more sophisticated parsing
    const names = text.match(/\b[A-Z][a-z]+\b/g) || ["The Protagonist"];
    // Get unique names using Array.from instead of spread operator
    const uniqueNames = Array.from(new Set(names));
    return uniqueNames.slice(0, 3); // Get unique names, max 3
  }

  function extractSetting(text: string): string {
    if (!text) return "A mysterious world";
    // Simple setting extraction
    if (text.includes('village')) return "A peaceful village";
    if (text.includes('forest')) return "An enchanted forest";
    if (text.includes('city')) return "A bustling city";
    if (text.includes('sea') || text.includes('ocean')) return "The vast seas";
    if (text.includes('mountain')) return "Majestic mountains";
    return "A magical realm";
  }

  const handlePageTurn = (direction: 'left' | 'right'): void => {
    if (direction === 'left' && page > 0) {
      setPage(page - 1);
    } else if (direction === 'right' && page < totalPages) {
      setPage(page + 1);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, direction: 'left' | 'right'): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handlePageTurn(direction);
    }
  };

  return (
    <div className="story-display-wrapper">
      <div className="story-back-button">
        <button
          className="back-to-home-btn"
          onClick={onReset}
          aria-label="Back to home"
        >
          <ArrowLeftIcon />
          <span>Back to Home</span>
        </button>
      </div>
      <div className="storybook-container">
        {page > 0 && (
          <div
            className="page-turn-arrow left"
            onClick={() => handlePageTurn('left')}
            onKeyDown={(e) => handleKeyDown(e, 'left')}
            tabIndex={0}
            role="button"
            aria-label="Previous page"
          >
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
              style={{ animation: 'fadeIn 0.7s ease' }}
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
            <div key={page} style={{ animation: 'fadeIn 0.7s ease', height: '100%' }}>
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
                    <div key={`character-${index}`} className="character-item">
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
          <div
            className="page-turn-arrow right"
            onClick={() => handlePageTurn('right')}
            onKeyDown={(e) => handleKeyDown(e, 'right')}
            tabIndex={0}
            role="button"
            aria-label="Next page"
          >
            <ArrowRightIcon />
          </div>
        )}
      </div>

      {/* Chatbot Component - shows below the storybook */}
      <Chatbot storyId={storyId} storyData={story} />
    </div>
  );
};

export default StoryDisplay;
