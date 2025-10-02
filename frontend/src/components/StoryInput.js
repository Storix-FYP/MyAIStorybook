import React, { useState } from "react";

export default function StoryInput({ onStory }) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = async () => {
    const res = await fetch("http://localhost:8000/generate_story", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    onStory(data);
  };

  return (
    <div>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <button onClick={handleSubmit}>Generate Story</button>
    </div>
  );
}
