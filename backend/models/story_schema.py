# backend/models/story_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional


class Scene(BaseModel):
    scene_number: int = Field(..., description="Order of the scene in the story")
    text: str = Field(..., description="Narrative content of the scene")
    image_description: Optional[str] = Field(
        None, description="Optional description of the visual for this scene"
    )
    # allow additional fields like image_path if set later
    image_path: Optional[str] = Field(None, description="Local path to generated image")


class Story(BaseModel):
    title: str = Field(..., description="Title of the storybook")
    setting: str = Field(..., description="Main setting / background of the story")
    characters: List[str] = Field(..., description="List of main characters")
    scenes: List[Scene] = Field(..., description="Ordered scenes in the story")


# Example usage
if __name__ == "__main__":
    example_story = {
        "title": "The Brave Cat",
        "setting": "A small village near the forest",
        "characters": ["Milo the Cat", "Old Farmer"],
        "scenes": [
            {"scene_number": 1, "text": "Milo wakes up early to explore the farm."},
            {
                "scene_number": 2,
                "text": "He hears strange noises from the forest.",
                "image_description": "A cat looking curiously at the forest edge."
            },
        ],
    }

    story = Story(**example_story)
    # Pydantic v2: use model_dump_json for pretty printing
    print(story.model_dump_json(indent=2))
