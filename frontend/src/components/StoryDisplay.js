import React, { useState } from "react";

export default function StoryDisplay({ story }) {
  const [index, setIndex] = useState(0);

  if (!story) return <div>No story yet.</div>;

  const scenes = story.scenes || [];
  const scene = scenes[index] || {};

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>{story.title || "Untitled"}</h2>
      <p><b>Setting:</b> {story.setting || "N/A"}</p>
      <p><b>Characters:</b> {(story.characters || []).join(", ") || "N/A"}</p>

      <hr />

      <h3>Scene {index + 1}</h3>
      <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
        {scene.image_url && (
          <img
            src={`http://localhost:8000${scene.image_url}`}
            alt="scene illustration"
            style={{
              width: "300px",   // fixed max width
              borderRadius: "8px",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
            }}
          />
        )}

        <div style={{ flex: 1 }}>
          <p>{scene.text || "No text available."}</p>
        </div>
      </div>

      <div style={{ marginTop: "1rem" }}>
        <button
          onClick={() => setIndex((i) => Math.max(i - 1, 0))}
          disabled={index === 0}
        >
          ◀ Prev
        </button>
        <button
          onClick={() => setIndex((i) => Math.min(i + 1, scenes.length - 1))}
          disabled={index === scenes.length - 1}
          style={{ marginLeft: "1rem" }}
        >
          Next ▶
        </button>
      </div>
    </div>
  );
}
