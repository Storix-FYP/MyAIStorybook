# backend/agents/director_agent.py
from typing import Dict, Any
from backend.agents.prompt_agent import PromptAgent
from backend.agents.writer_agent import WriterAgent
from backend.agents.reviewer_agent import ReviewerAgent
from backend.agents.editor_agent import EditorAgent
from backend.agents.image_agent import ImageAgent


class DirectorAgent:
    """
    DirectorAgent orchestrates the pipeline:
      PromptAgent -> WriterAgent -> (optional ImageAgent) -> ReviewerAgent -> EditorAgent
    """

    def __init__(self, llm_model: str = "llama3.1:8b-instruct-q4_K_M", writer_max_scenes: int = 3):
        self.prompt_agent = PromptAgent(model=llm_model)
        self.writer = WriterAgent(llm_model=llm_model, max_retries=2, max_scenes=writer_max_scenes)
        self.reviewer = ReviewerAgent()
        self.editor = EditorAgent()
        # ImageAgent instantiated only when images requested

    def create_story(self, user_prompt: str, generate_images: bool = False) -> Dict[str, Any]:
        # Step 0 - prompt handling (PromptAgent already enriches/validates)
        enhanced_prompt, prompt_type = self.prompt_agent.process_prompt(user_prompt)
        if prompt_type in ["invalid", "nonsense"]:
            raise ValueError("Invalid or nonsense prompt provided")

        # Step 1 - write story
        story_dict, write_status = self.writer.generate_story(enhanced_prompt)

        # Step 2 - images (optional)
        image_status = "skipped"
        if generate_images:
            image_agent = ImageAgent()
            story_dict, image_status = image_agent.generate_images(story_dict)

        # Step 3 - review
        story_dict, review_status = self.reviewer.review_story(story_dict)

        # Step 4 - edit/package
        story_dict, edit_status = self.editor.edit_story(story_dict)

        # attach meta
        story_dict.setdefault("meta", {})
        story_dict["meta"].update({"prompt_type": prompt_type, "enhanced_prompt": enhanced_prompt})

        # Final response
        response = {
            "status": {"write": write_status, "image": image_status, "review": review_status, "edit": edit_status},
            "story": story_dict,
        }
        return response
