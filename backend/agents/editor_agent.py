import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak
)

from reportlab.lib.utils import ImageReader


def sanitize_filename(name: str) -> str:
    """Remove invalid filename characters."""
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip()


def export_pdf(story_data, output_filename):
    """
    Create a storybook PDF with text and images.
    Saves in generated/exports folder (located outside backend).
    """
    # --- Setup correct base paths ---
    base_dir = os.path.dirname(__file__)  # backend/agents/
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))  # goes up to main folder
    generated_dir = os.path.join(project_root, "generated")
    exports_dir = os.path.join(generated_dir, "exports")
    images_dir = os.path.join(generated_dir, "images")

    os.makedirs(exports_dir, exist_ok=True)

    pdf_path = os.path.join(exports_dir, output_filename)
    print(f"📘 Exporting PDF to: {pdf_path}")

    # --- Prepare document ---
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # --- Title ---
    story.append(Paragraph(f"<b>{story_data.get('title', 'Untitled Story')}</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # --- Characters ---
    chars = story_data.get("characters", [])
    if chars:
        story.append(Paragraph(f"<b>Characters:</b> {', '.join(chars)}", styles["Normal"]))
        story.append(Spacer(1, 12))

    # --- Scenes ---
    scenes = story_data.get("scenes", [])
    for i, scene in enumerate(scenes, start=1):
        story.append(Paragraph(f"<b>Scene {i}</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(scene.get("text", ""), styles["Normal"]))
        story.append(Spacer(1, 12))
    
        # --- Image handling (safe for missing paths) ---
        img_path = scene.get("image_path")
        img_name = None
    
        if isinstance(img_path, str) and img_path.strip():
            img_name = os.path.basename(img_path)
        else:
            img_name = f"scene_{i}.png"
    
        abs_path = os.path.join(images_dir, img_name)
    
        print(f"🔍 Looking for image at: {abs_path}")
        if os.path.exists(abs_path):
            try:
                story.append(RLImage(abs_path, width=5 * inch, height=3 * inch))
                story.append(Spacer(1, 20))
                print(f"✅ Added image to PDF: {abs_path}")
            except Exception as e:
                print(f"⚠️ Failed to embed image: {abs_path} ({e})")
        else:
            print(f"❌ Image not found at: {abs_path}")
    
        # Add page break except after last scene
        if i != len(scenes):
            story.append(PageBreak())
    

    # --- Build final PDF ---
    doc.build(story)
    print(f"✅ PDF created successfully at: {pdf_path}")
    return pdf_path



class EditorAgent:
    """
    Performs final cleanup and calls export_pdf to save the story as a PDF.
    """

    def __init__(self, export_dir: str = None):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        generated_dir = os.path.join(project_root, "generated")
        self.export_dir = os.path.join(generated_dir, "exports")
        os.makedirs(self.export_dir, exist_ok=True)

    def edit_story(self, story_dict: Dict[str, Any]):
        """Clean story metadata and export it as a formatted PDF."""
        story_dict["meta"] = {
            "edited_at": datetime.utcnow().isoformat() + "Z",
            "editor_version": "0.6",
        }
        story_dict["finalized"] = True

        return story_dict, "Edited and packaged ✅"

