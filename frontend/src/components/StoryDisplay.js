import React from "react";

export default function StoryDisplay({ story }) {
  if (!story) return <div>No story yet.</div>;
  return (
    <div>
      <h2>{story.title}</h2>
      <p><b>Setting:</b> {story.setting}</p>
      <p><b>Characters:</b> {story.characters.join(", ")}</p>
      {story.scenes.map((s) => (
        <div key={s.scene_number}>
          <h3>Scene {s.scene_number}</h3>
          <p>{s.text}</p>
        </div>
      ))}
    </div>
  );
}
