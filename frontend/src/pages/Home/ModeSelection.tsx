'use client';

import React from 'react';
import styles from './ModeSelection.module.css';

interface ModeSelectionProps {
  onSelectMode: (mode: 'simple' | 'personalized') => void;
  onClose: () => void;
}

export const ModeSelection: React.FC<ModeSelectionProps> = ({ onSelectMode, onClose }) => {
  const handleModeSelect = (mode: 'simple' | 'personalized') => {
    onSelectMode(mode);
    // Don't call onClose() here - onSelectMode handles the navigation
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2 className={styles.title}>✨ Choose Your Story Mode ✨</h2>
        <p className={styles.subtitle}>How would you like to create your story?</p>

        <div className={styles.modeCards}>
          {/* Simple Story Mode */}
          <div
            className={styles.modeCard}
            onClick={() => handleModeSelect('simple')}
          >
            <div className={styles.icon}>📖</div>
            <h3 className={styles.cardTitle}>Simple Story</h3>
            <p className={styles.cardDescription}>
              Create a magical story with beautiful illustrations.
              Just describe your idea and let AI bring it to life!
            </p>
            <button className={styles.selectButton}>
              Create Simple Story
            </button>
          </div>

          {/* Personalized Story Mode */}
          <div
            className={styles.modeCard}
            onClick={() => handleModeSelect('personalized')}
          >
            <div className={styles.icon}>🎨</div>
            <h3 className={styles.cardTitle}>Personalized Story</h3>
            <p className={styles.cardDescription}>
              Create a unique story with personalized characters and themes.
              Your imagination, your adventure!
            </p>
            <button className={styles.selectButton}>
              Create Personalized Story
            </button>
            <span className={styles.comingSoon}>(Enhanced features coming soon!)</span>
          </div>
        </div>

        <button className={styles.closeButton} onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
};
