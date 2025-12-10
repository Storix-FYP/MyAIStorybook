'use client';

import React, { useState } from "react";
import { API_ENDPOINTS } from "@/utils/constants";
import { useAuth } from "@/contexts/AuthContext";
import "./StoryInput.css";

interface StoryInputProps {
  onStoryGenerated: (story: any, storyId?: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  onShowLogin?: () => void;
  mode?: 'simple' | 'personalized';
}

const StoryInput: React.FC<StoryInputProps> = ({ onStoryGenerated, setLoading, setError, onShowLogin, mode = 'simple' }) => {
  const { isAuthenticated, token } = useAuth();
  const [prompt, setPrompt] = useState<string>("");
  const [generateImages, setGenerateImages] = useState<boolean>(isAuthenticated);
  const [usePersonalizedImages, setUsePersonalizedImages] = useState<boolean>(false);
  const [userPhoto, setUserPhoto] = useState<string | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
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

      // Debug logging
      console.log('🎭 Personalized Images Debug:');
      console.log('  - usePersonalizedImages:', usePersonalizedImages);
      console.log('  - hasUserPhoto:', userPhoto !== null);
      console.log('  - photoDataLength:', userPhoto?.length || 0);

      const res = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers,
        body: JSON.stringify({
          prompt,
          generate_images: generateImages,
          use_personalized_images: usePersonalizedImages && userPhoto !== null,
          user_photo: userPhoto,  // Base64 photo data
          mode: mode  // Include mode in request
        }),
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
        onStoryGenerated(data.story, data.story_id);  // Pass story_id to parent
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

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setLocalError('Please upload an image file (JPEG or PNG)');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setLocalError('Image too large. Please upload an image smaller than 5MB.');
      return;
    }

    // Read file and convert to base64
    const reader = new FileReader();
    reader.onload = (event) => {
      const base64Data = event.target?.result as string;
      setUserPhoto(base64Data);
      setPhotoPreview(base64Data);
      setLocalError(null);
    };
    reader.onerror = () => {
      setLocalError('Failed to read the image file');
    };
    reader.readAsDataURL(file);
  };

  const handleRemovePhoto = (): void => {
    setUserPhoto(null);
    setPhotoPreview(null);
    setUsePersonalizedImages(false);
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

        {/* Personalized Images Toggle */}
        {generateImages && isAuthenticated && (
          <div className="toggle-switch">
            <label className="switch">
              <input
                type="checkbox"
                checked={usePersonalizedImages}
                onChange={(e) => setUsePersonalizedImages(e.target.checked)}
                disabled={!userPhoto}
              />
              <span className={`slider ${!userPhoto ? 'disabled' : ''}`}></span>
            </label>
            <span className={!userPhoto ? 'disabled-text' : ''}>
              Use My Photo 🎭
            </span>
          </div>
        )}

        {/* Photo Upload Section */}
        {generateImages && isAuthenticated && (
          <div className="photo-upload-section">
            {!photoPreview ? (
              <div className="upload-area">
                <label htmlFor="photo-upload" className="upload-label">
                  <span className="upload-icon">📸</span>
                  <span>Upload Your Photo</span>
                  <input
                    id="photo-upload"
                    type="file"
                    accept="image/jpeg,image/png,image/jpg"
                    onChange={handlePhotoUpload}
                    style={{ display: 'none' }}
                  />
                </label>
                <p className="upload-hint">Clear frontal photo works best</p>
              </div>
            ) : (
              <div className="photo-preview-container">
                <img src={photoPreview} alt="Your photo" className="photo-preview" />
                <button
                  type="button"
                  className="remove-photo-btn"
                  onClick={handleRemovePhoto}
                  title="Remove photo"
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        )}

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
