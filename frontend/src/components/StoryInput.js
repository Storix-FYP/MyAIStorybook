import React, { useState } from "react";

export default function StoryInput({ onStory }) {
  const [prompt, setPrompt] = useState("");
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [generateImages, setGenerateImages] = useState(true); // new checkbox state
  const [loading, setLoading] = useState(false); // for "Generating..." indication

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, generate_images: generateImages }), // send flag
      });
      const data = await res.json();
      onStory(data.story);
    } catch (err) {
      console.error("Error generating story:", err);
    } finally {
      setLoading(false);
    }
  };

  const checkDevice = async () => {
    try {
      const res = await fetch("http://localhost:8000/device");
      const data = await res.json();
      setDeviceInfo(data);
    } catch (err) {
      setDeviceInfo({ error: "Failed to fetch device info" });
    }
  };

  return (
    <div>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your story idea..."
        style={{ width: "100%", height: "100px" }}
      />
      <br />

      <label style={{ display: "block", marginTop: "10px" }}>
        <input
          type="checkbox"
          checked={generateImages}
          onChange={(e) => setGenerateImages(e.target.checked)}
        />
        Generate Images
      </label>

      <br />

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Generating..." : "Generate Story"}
      </button>

      <button onClick={checkDevice} style={{ marginLeft: "10px" }}>
        Check Device
      </button>

      {deviceInfo && (
        <pre
          style={{
            background: "#f4f4f4",
            padding: "10px",
            marginTop: "10px",
          }}
        >
          {JSON.stringify(deviceInfo, null, 2)}
        </pre>
      )}
    </div>
  );
}
