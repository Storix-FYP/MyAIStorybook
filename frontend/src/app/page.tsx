'use client';

import { useState } from 'react';
import { Navigation, Footer } from '@/layout';
import { LandingPage } from '@/pages/Home';
import { StoryInput, StoryDisplay } from '@/pages/Story';
import { Login, Register } from '@/pages/Auth';
import { LoadingExperience } from '@/shared/components';

// Story type definition
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
  meta?: {
    prompt_type: string;
    enhanced_prompt: string;
  };
}

export default function Home() {
  const [story, setStory] = useState<Story | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showLanding, setShowLanding] = useState<boolean>(true);
  const [showLogin, setShowLogin] = useState<boolean>(false);
  const [showRegister, setShowRegister] = useState<boolean>(false);

  const handleStartCreating = (): void => {
    setShowLanding(false);
    setStory(null);
    setError(null);
  };

  const handleStoryGenerated = (newStory: Story): void => {
    setStory(newStory);
    setError(null);
    setShowLanding(false);
  };

  const handleReset = (): void => {
    setStory(null);
    setError(null);
    setShowLanding(true);
  };

  const handleGoHome = (): void => {
    setStory(null);
    setError(null);
    setShowLanding(true);
  };

  return (
    <div className="app">
      <Navigation 
        onReset={handleReset} 
        showReset={story !== null}
        onGoHome={handleGoHome}
        onShowLogin={() => setShowLogin(true)}
        onShowRegister={() => setShowRegister(true)}
      />
      
      {loading && <LoadingExperience />}
      
      <main className="main-content">
        {showLanding && !story ? (
          <LandingPage onStartCreating={handleStartCreating} />
        ) : !story ? (
          <div className="story-input-section">
            <div className="story-input-container">
              <StoryInput
                onStoryGenerated={handleStoryGenerated}
                setLoading={setLoading}
                setError={setError}
                onShowLogin={() => setShowLogin(true)}
              />
            </div>
          </div>
        ) : (
          <div className="story-display-section">
            <StoryDisplay story={story} onReset={handleReset} />
          </div>
        )}
      </main>
      
      <Footer />
      
      {showLogin && (
        <Login 
          onClose={() => setShowLogin(false)} 
          onSwitchToRegister={() => { setShowLogin(false); setShowRegister(true); }}
        />
      )}
      
      {showRegister && (
        <Register 
          onClose={() => setShowRegister(false)} 
          onSwitchToLogin={() => { setShowRegister(false); setShowLogin(true); }}
        />
      )}
    </div>
  );
}
