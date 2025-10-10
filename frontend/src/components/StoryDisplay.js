import React, { useState } from "react";

export default function StoryDisplay({ story }) {
  const [index, setIndex] = useState(0);

  if (!story) return <div style={{ color: "#aaa" }}>No story yet.</div>;

  const scenes = story.scenes || [];
  const scene = scenes[index] || {};

  return (
    <div
      style={{
        marginTop: "2rem",
        background: "#1e1e1e",
        color: "#f0f0f0",
        padding: "2rem",
        borderRadius: "12px",
        boxShadow: "0 4px 16px rgba(0, 0, 0, 0.4)",
        fontFamily: "Segoe UI, sans-serif",
      }}
    >
      {/* Story Header */}
      <h2 style={{ marginBottom: "0.25rem", fontSize: "1.8rem" }}>
        {story.title || "Untitled"}
      </h2>
      <p style={{ color: "#aaa", fontSize: "0.9rem", marginBottom: "1rem" }}>
        Detected Prompt Type:{" "}
        <span style={{ color: "#6ecfff" }}>
          {story?.meta?.prompt_type || "unknown"}
        </span>
      </p>

      {/* Story Metadata */}
      <p style={{ marginBottom: "0.3rem" }}>
        <b>Setting:</b> {story.setting || "N/A"}
      </p>
      <p style={{ marginBottom: "1rem" }}>
        <b>Characters:</b>{" "}
        {(story.characters || []).length > 0
          ? story.characters.join(", ")
          : "N/A"}
      </p>

      <hr style={{ border: "1px solid #333", margin: "1rem 0" }} />

      {/* Scene Display */}
      <h3 style={{ marginBottom: "1rem" }}>
        Scene {index + 1} of {scenes.length || 1}
      </h3>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "20px",
          alignItems: "flex-start",
        }}
      >
        {scene.image_url && (
          <img
            src={`http://localhost:8000${scene.image_url}`}
            alt="scene illustration"
            style={{
              width: "100%",
              maxWidth: "350px",
              borderRadius: "10px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
              flexShrink: 0,
            }}
          />
        )}

        <div style={{ flex: 1, minWidth: "250px" }}>
          <p style={{ lineHeight: "1.6", color: "#ddd" }}>
            {scene.text || "No text available for this scene."}
          </p>
        </div>
      </div>

      {/* Navigation Buttons */}
      <div
        style={{
          marginTop: "1.5rem",
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
        }}
      >
        <button
          onClick={() => setIndex((i) => Math.max(i - 1, 0))}
          disabled={index === 0}
          style={{
            background: index === 0 ? "#333" : "#444",
            color: "#fff",
            border: "none",
            padding: "0.6rem 1.2rem",
            borderRadius: "6px",
            cursor: index === 0 ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          ◀ Prev
        </button>
        <button
          onClick={() => setIndex((i) => Math.min(i + 1, scenes.length - 1))}
          disabled={index === scenes.length - 1}
          style={{
            background:
              index === scenes.length - 1 ? "#333" : "#444",
            color: "#fff",
            border: "none",
            padding: "0.6rem 1.2rem",
            borderRadius: "6px",
            cursor:
              index === scenes.length - 1 ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
        >
          Next ▶
        </button>
      </div>
    </div>
  );
}
