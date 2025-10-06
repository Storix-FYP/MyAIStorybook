import React, { useState } from "react";

export default function StoryInput({ onStory }) {
  const [prompt, setPrompt] = useState("");
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [generateImages, setGenerateImages] = useState(true); // Checkbox state
  const [loading, setLoading] = useState(false); // "Generating..." state
  const [error, setError] = useState(null); // Error message

  const handleCheckDevice = async () => {
    try {
      const res = await fetch("http://localhost:8000/device");
      const data = await res.json();
      setDeviceInfo(data);
    } catch (err) {
      console.error("Device check failed:", err);
      setDeviceInfo({ device: "unknown" });
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt before generating.");
      return;
    }

    setLoading(true);
    setError(null); // clear any previous error

    try {
      const res = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          generate_images: generateImages,
        }),
      });

      if (!res.ok) throw new Error(`Backend error: ${res.statusText}`);

      const data = await res.json();
      if (data?.story) {
        onStory(data.story);
      } else {
        throw new Error("No story returned from backend.");
      }
    } catch (err) {
      console.error("Generation failed:", err);
      setError("Failed to generate story. Please try again.");
    } finally {
      setLoading(false); // always revert button to "Generate"
    }
  };

  return (
    <div className="p-4 bg-gray-900 rounded-2xl shadow-lg text-white space-y-4">
      <h2 className="text-2xl font-semibold"> Story Generator</h2>

      <div className="space-y-2">
        <textarea
          className="w-full p-3 rounded-lg text-black"
          rows="3"
          placeholder="Enter your story idea..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>

      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          checked={generateImages}
          onChange={(e) => setGenerateImages(e.target.checked)}
        />
        <label>Generate images</label>
      </div>

      <div className="flex space-x-3">
        <button
          onClick={handleCheckDevice}
          className="px-4 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-700"
        >
          Check Device
        </button>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className={`px-4 py-2 rounded-lg font-semibold ${
            loading
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {deviceInfo && (
        <p className="text-sm text-gray-400">
          Device: {deviceInfo.device}{" "}
          {deviceInfo.name ? `(${deviceInfo.name})` : ""}
        </p>
      )}

      {error && (
        <p className="text-red-400 font-medium mt-2">{error}</p>
      )}
    </div>
  );
}
