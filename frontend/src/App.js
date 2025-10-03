import React, { useState } from "react";
import StoryInput from "./components/StoryInput";
import StoryDisplay from "./components/StoryDisplay";

function App() {
  const [story, setStory] = useState(null);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>📖 Storybook - Iteration 1</h1>
      <p>Enter a short idea and click Generate:</p>

      <StoryInput onStory={setStory} />

      {story && <StoryDisplay story={story} />}
    </div>
  );
}

export default App;
