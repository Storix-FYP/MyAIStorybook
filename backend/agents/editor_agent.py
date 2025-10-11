# backend/agents/editor_agent.py
import datetime
from typing import Dict, Any, Tuple



class EditorAgent:
    """
    EditorAgent: final metadata and sanitization for frontend
    """

    def __init__(self, version: str = "0.2"):
        self.version = version

    def edit_story(self, story_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        meta = story_dict.get("meta", {})
        meta.update(
            {
                "edited_at": datetime.datetime.utcnow().isoformat() + "Z",
                "editor_version": self.version,
            }
        )
        story_dict["meta"] = meta

        # sort scenes by scene_number
        scenes = story_dict.get("scenes", [])
        scenes_sorted = sorted(scenes, key=lambda s: int(s.get("scene_number", 0)))
        story_dict["scenes"] = scenes_sorted

        # remove heavy fields not needed by main frontend
        for s in story_dict["scenes"]:
            s.pop("image_description", None)

        story_dict.setdefault("finalized", True)
        return story_dict, "Edited and packaged ✅"
