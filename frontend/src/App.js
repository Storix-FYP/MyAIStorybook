import React, { useState } from "react";
import StoryInput from "./components/StoryInput";
import StoryDisplay from "./components/StoryDisplay";

function App() {
  const [story, setStory] = useState(null);

  return (
    <div>
      <h1>Children's Storybook Generator</h1>
      <StoryInput onStory={setStory} />
      <StoryDisplay story={story} />
    </div>
  );
}

export default App;
