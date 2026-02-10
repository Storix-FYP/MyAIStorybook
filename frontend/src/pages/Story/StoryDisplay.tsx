'use client';

import React, { useState, useRef, useEffect, useCallback } from "react";
import { Chatbot } from './Chatbot';
import { useAuth } from "../../contexts/AuthContext";
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

const SpeakerIcon: React.FC = () => (
  <svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"></path></svg>
);

const StopIcon: React.FC = () => (
  <svg viewBox="0 0 24 24"><path d="M6 6h12v12H6z"></path></svg>
);

const DownloadIcon: React.FC = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="7 10 12 15 17 10"></polyline>
    <line x1="12" y1="15" x2="12" y2="3"></line>
  </svg>
);

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story, storyId, onReset }) => {
  const [page, setPage] = useState<number>(0); // 0 is cover
  const [prevPage, setPrevPage] = useState<number>(0);
  const [isFlipping, setIsFlipping] = useState<boolean>(false);
  const [flipDirection, setFlipDirection] = useState<'left' | 'right' | null>(null);

  const { token } = useAuth();

  // TTS State
  const [isReadingAloud, setIsReadingAloud] = useState<boolean>(false);
  const [isAudioLoading, setIsAudioLoading] = useState<boolean>(false);
  const [selectedVoice, setSelectedVoice] = useState<'female' | 'male'>('female');
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [autoPageNotice, setAutoPageNotice] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Reset to cover page when story changes
  useEffect(() => {
    setPage(0);
    setPrevPage(0);
    setIsFlipping(false);
    setFlipDirection(null);
  }, [storyId]);

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

  const handlePageTurn = useCallback((direction: 'left' | 'right'): void => {
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
  }, [page, isFlipping, totalPages]);

  // TTS Logic
  const stopReading = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsReadingAloud(false);
    setCurrentAudioUrl(null);
  }, []);

  const handleDownload = async () => {
    if (!storyId) {
      alert("Story ID not found. Cannot download.");
      return;
    }

    setIsDownloading(true);
    try {
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`http://localhost:8000/api/stories/${storyId}/download`, {
        headers
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeTitle = story.title.replace(/[^\w\s-]/g, '').replace(/[\s-]+/g, '_').toLowerCase();
        a.download = `${safeTitle}_storybook.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to generate PDF: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error("Download failed:", err);
      alert("Error connecting to server for download.");
    } finally {
      setIsDownloading(false);
    }
  };

  const fetchAndPlayAudio = useCallback(async (sceneNum: number) => {
    if (!storyId || sceneNum < 1 || sceneNum > totalPages) return;

    setIsAudioLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tts/${storyId}/${sceneNum}?voice=${selectedVoice}`);
      if (response.ok) {
        const data = await response.json();
        const fullAudioUrl = `http://localhost:8000${data.audio_url}`;
        setCurrentAudioUrl(fullAudioUrl);

        if (audioRef.current) {
          audioRef.current.src = fullAudioUrl;
          audioRef.current.play().catch(err => {
            console.error("Playback failed:", err);
            stopReading();
          });
        }
      } else {
        console.error("Failed to fetch TTS audio");
        stopReading();
      }
    } catch (err) {
      console.error("Error fetching audio:", err);
      stopReading();
    } finally {
      setIsAudioLoading(false);
    }
  }, [storyId, totalPages, stopReading, selectedVoice]);

  const toggleReadingAloud = useCallback(() => {
    if (isReadingAloud) {
      stopReading();
    } else {
      setIsReadingAloud(true);
      // If on cover, transition to first page. The useEffect will handle audio.
      if (page === 0) {
        handlePageTurn('right');
      }
    }
  }, [isReadingAloud, stopReading, page, handlePageTurn]);

  // Effect: Handle page changes during reading aloud
  useEffect(() => {
    if (isReadingAloud && page > 0 && !isFlipping) {
      fetchAndPlayAudio(page);
    }
  }, [page, isReadingAloud, isFlipping, fetchAndPlayAudio]);

  // Effect: Cleanup TTS on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const handleAudioEnded = () => {
    if (isReadingAloud) {
      if (page < totalPages) {
        setAutoPageNotice("Turning page...");
        setTimeout(() => {
          handlePageTurn('right');
          setTimeout(() => setAutoPageNotice(null), 3000);
        }, 1000);
      } else {
        stopReading();
        setAutoPageNotice("Story finished!");
        setTimeout(() => setAutoPageNotice(null), 3000);
      }
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

              <div className="tts-controls on-cover">
                <div className="voice-selector">
                  <button
                    className={`voice-btn ${selectedVoice === 'female' ? 'active' : ''}`}
                    onClick={() => setSelectedVoice('female')}
                    title="Female Voice"
                  >
                    👩
                  </button>
                  <button
                    className={`voice-btn ${selectedVoice === 'male' ? 'active' : ''}`}
                    onClick={() => setSelectedVoice('male')}
                    title="Male Voice"
                  >
                    👨
                  </button>
                </div>

                <button
                  className={`tts-button ${isReadingAloud ? 'is-playing' : ''}`}
                  onClick={toggleReadingAloud}
                  title={isReadingAloud ? "Stop Reading" : "Read Story Aloud"}
                >
                  {isReadingAloud ? <StopIcon /> : <SpeakerIcon />}
                  {isAudioLoading && <div className="tts-loader"></div>}
                </button>
              </div>
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
              <div className={`text-content ${isReadingAloud && page === p ? 'reading-highlight' : ''}`}>
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
      <div className="story-top-controls">
        <div className="story-back-button">
          <button className="back-to-home-btn" onClick={onReset}>
            <ArrowLeftIcon />
            <span>Back to Home</span>
          </button>

          <button
            className={`download-pdf-btn ${isDownloading ? 'loading' : ''}`}
            onClick={handleDownload}
            disabled={isDownloading}
          >
            <DownloadIcon />
            <span>{isDownloading ? "Preparing..." : "Download PDF"}</span>
          </button>
        </div>

        <div className="tts-controls main-controls">
          <button
            className={`tts-button ${isReadingAloud ? 'is-playing' : ''} ${page === 0 ? 'hidden' : ''}`}
            onClick={toggleReadingAloud}
            title={isReadingAloud ? "Stop Reading" : "Read Aloud"}
            disabled={isFlipping}
          >
            {isReadingAloud ? <StopIcon /> : <SpeakerIcon />}
            {isAudioLoading && <div className="tts-loader"></div>}
          </button>
        </div>
      </div>

      {autoPageNotice && <div className="auto-page-notice">{autoPageNotice}</div>}

      <audio
        ref={audioRef}
        onEnded={handleAudioEnded}
        style={{ display: 'none' }}
      />

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
