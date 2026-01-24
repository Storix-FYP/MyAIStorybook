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
  const [prevPage, setPrevPage] = useState<number>(0);
  const [isFlipping, setIsFlipping] = useState<boolean>(false);
  const [flipDirection, setFlipDirection] = useState<'left' | 'right' | null>(null);
  const scenes = story.scenes || [];
  const totalPages = scenes.length;

  // Helpers to get scene data for any page index
  const getScene = (p: number) => scenes[p - 1] || {};

  if (!story) return null;

  // Extract characters and setting
  const firstScene = scenes[0] || {};
  const characters = story.characters || extractCharacters(firstScene.text || "");
  const setting = story.setting || extractSetting(firstScene.text || "");

  function extractCharacters(text: string): string[] {
    if (!text) return ["Main Character"];
    const names = text.match(/\b[A-Z][a-z]+\b/g) || ["The Protagonist"];
    return Array.from(new Set(names)).slice(0, 3);
  }

  function extractSetting(text: string): string {
    if (!text) return "A mysterious world";
    if (text.includes('village')) return "A peaceful village";
    if (text.includes('forest')) return "An enchanted forest";
    if (text.includes('city')) return "A bustling city";
    if (text.includes('sea') || text.includes('ocean')) return "The vast seas";
    if (text.includes('mountain')) return "Majestic mountains";
    return "A magical realm";
  }

  const handlePageTurn = (direction: 'left' | 'right'): void => {
    if (isFlipping) return;

    if (direction === 'left' && page > 0) {
      setPrevPage(page);
      setPage(page - 1);
      setIsFlipping(true);
      setFlipDirection('left');
      setTimeout(() => {
        setIsFlipping(false);
        setFlipDirection(null);
      }, 700);
    } else if (direction === 'right' && page < totalPages) {
      setPrevPage(page);
      setPage(page + 1);
      setIsFlipping(true);
      setFlipDirection('right');
      setTimeout(() => {
        setIsFlipping(false);
        setFlipDirection(null);
      }, 700);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, direction: 'left' | 'right'): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handlePageTurn(direction);
    }
  };

  // Helper to render a specific page side (image or text)
  const renderPage = (p: number, type: 'left' | 'right') => {
    const scene = getScene(p);
    if (type === 'left') {
      return (
        <div className="page image-page">
          {p > 0 && scene.image_url ? (
            <img src={`http://localhost:8000${scene.image_url}`} alt={`Illustration ${p}`} className="storybook-image" />
          ) : p === 0 ? (
            <div className="cover-page">
              <h2 className="cover-title">{story.title}</h2>
              <p className="cover-subtitle">by MyAIStorybook</p>
            </div>
          ) : (
            <div className="no-illustration"><p>No illustration</p></div>
          )}
        </div>
      );
    } else {
      return (
        <div className="page text-page">
          {p > 0 ? (
            <>
              <div className="text-content">
                <p>{scene.text}</p>
              </div>
              <div className="page-indicator">Page {p} of {totalPages}</div>
            </>
          ) : (
            <div className="story-details">
              <div className="details-section">
                <h3 className="details-title">🏰 Setting</h3>
                <p className="details-content">{setting}</p>
              </div>
              <div className="details-section">
                <h3 className="details-title">🎭 Main Characters</h3>
                <div className="characters-list">
                  {characters.map((character, idx) => (
                    <div key={idx} className="character-item">
                      <span className="character-bullet">•</span>
                      <span className="character-name">{character}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="begin-reading">
                <button className="begin-button" onClick={() => handlePageTurn('right')}>Begin Reading →</button>
                <p className="page-count">{totalPages} captivating pages await</p>
              </div>
            </div>
          )}
        </div>
      );
    }
  };

  return (
    <div className="story-display-wrapper">
      <div className="story-back-button">
        <button className="back-to-home-btn" onClick={onReset}>
          <ArrowLeftIcon />
          <span>Back to Home</span>
        </button>
      </div>

      <div className={`storybook-container ${isFlipping ? 'is-flipping' : ''}`}>
        {/* ARROWS */}
        {page > 0 && !isFlipping && (
          <div className="page-turn-arrow left" onClick={() => handlePageTurn('left')} tabIndex={0} role="button">
            <ArrowLeftIcon />
          </div>
        )}
        {page < totalPages && !isFlipping && (
          <div className="page-turn-arrow right" onClick={() => handlePageTurn('right')} tabIndex={0} role="button">
            <ArrowRightIcon />
          </div>
        )}

        {/* LAYER 1: THE TARGET SPREAD (Revealed underneath) */}
        <div className="spread-layer bottom-layer">
          <div className="spread-content static-spread">
            {/* 
              COMPOSITE RENDERING LOGIC:
              When flipping right (Next): Left side stays as prevPage until covered. Right side is already New page.
              When flipping left (Prev): Right side stays as prevPage until covered. Left side is already New page.
            */}
            {renderPage(
              isFlipping && flipDirection === 'right' ? prevPage : page,
              'left'
            )}
            {renderPage(
              isFlipping && flipDirection === 'left' ? prevPage : page,
              'right'
            )}
          </div>
        </div>

        {/* LAYER 3: THE FLIPPING LEAF (The physical page turn) */}
        {isFlipping && (
          <div className={`flipping-leaf ${flipDirection}`}>
            <div className="leaf-face leaf-front">
              {flipDirection === 'right' ? renderPage(prevPage, 'right') : renderPage(prevPage, 'left')}
            </div>
            <div className="leaf-face leaf-back">
              {flipDirection === 'right' ? renderPage(page, 'left') : renderPage(page, 'right')}
            </div>
          </div>
        )}
      </div>

      <Chatbot storyId={storyId} storyData={story} />
    </div>
  );
};

export default StoryDisplay;
