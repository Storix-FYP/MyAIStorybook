import React, { useState } from "react";
import StoryInput from "./components/StoryInput";
import StoryDisplay from "./components/StoryDisplay";
import "./App.css"; // Importing the custom CSS

function App() {
  const [story, setStory] = useState(null);

  return (
    <div className="app-background">
      <div className="app-container">
        <header className="app-header">
          <h1>📖 Storybook Generator</h1>
          <p>Turn your imagination into beautiful stories powered by AI</p>
        </header>

        <main className="app-main">
          <section className="input-section">
            <h2>Enter Your Story Idea</h2>
            <p className="section-subtext">
              Type a short idea or theme below, then click <b>Generate</b> to
              bring it to life!
            </p>
            <StoryInput onStory={setStory} />
          </section>

          {story && (
            <section className="output-section">
              <h2>Your Generated Story ✨</h2>
              <StoryDisplay story={story} />
            </section>
          )}
        </main>

        <footer className="app-footer">
          <p>
            Built by <strong>FAST FYP Team</strong> | Powered by Dolphin 3
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
