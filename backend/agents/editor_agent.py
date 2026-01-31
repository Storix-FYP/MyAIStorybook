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


from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Rect

# Try to register a child-friendly font
try:
    comic_path = "C:\\Windows\\Fonts\\comic.ttf"
    if os.path.exists(comic_path):
        pdfmetrics.registerFont(TTFont('ComicSans', comic_path))
        pdfmetrics.registerFont(TTFont('ComicSans-Bold', "C:\\Windows\\Fonts\\comicbd.ttf"))
        STORY_FONT = 'ComicSans'
        STORY_FONT_BOLD = 'ComicSans-Bold'
    else:
        STORY_FONT = 'Helvetica'
        STORY_FONT_BOLD = 'Helvetica-Bold'
except:
    STORY_FONT = 'Helvetica'
    STORY_FONT_BOLD = 'Helvetica-Bold'


def draw_background_and_border(canvas, doc):
    """Draw parchment-like background and hand-drawn style border."""
    canvas.saveState()
    
    # Ivory/Parchment background color
    canvas.setFillColor(colors.HexColor('#FFFDF0'))
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Decorative Border - slightly irregular for hand-drawn look
    canvas.setStrokeColor(colors.HexColor('#8B5A2B'))
    canvas.setLineWidth(3)
    margin = 40
    # Draw a rectangle with slightly inner lines to look like a frame
    canvas.roundRect(margin, margin, A4[0] - 2*margin, A4[1] - 2*margin, 15, stroke=1, fill=0)
    
    # Adding subtle "corner" accents
    canvas.setLineWidth(1)
    canvas.circle(margin, margin, 5, stroke=1, fill=1) # Bottom left
    canvas.circle(A4[0]-margin, margin, 5, stroke=1, fill=1) # Bottom right
    canvas.circle(margin, A4[1]-margin, 5, stroke=1, fill=1) # Top left
    canvas.circle(A4[0]-margin, A4[1]-margin, 5, stroke=1, fill=1) # Top right
    
    # Footer
    canvas.setFont(STORY_FONT, 9)
    canvas.setFillColor(colors.HexColor('#5D4037'))
    footer_text = "✨ MyAIStorybook - A Magical Adventure ✨"
    canvas.drawCentredString(A4[0] / 2, 0.6 * inch, footer_text)
    
    # Page Number in a small circle/badge
    page_num = str(doc.page)
    canvas.drawRightString(A4[0] - margin - 10, 0.6 * inch, f"Page {page_num}")
    
    canvas.restoreState()


def export_pdf(story_data, output_filename):
    """
    Create a highly creative storybook PDF with parchment background, 
    decorative borders, photo-frame images, and book-style typography.
    """
    base_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    generated_dir = os.path.join(project_root, "generated")
    exports_dir = os.path.join(generated_dir, "exports")
    images_dir = os.path.join(generated_dir, "images")

    os.makedirs(exports_dir, exist_ok=True)
    pdf_path = os.path.join(exports_dir, output_filename)
    
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=A4,
        rightMargin=72, leftMargin=72,
        topMargin=80, bottomMargin=80
    )
    
    styles = getSampleStyleSheet()
    
    # High-quality typography
    title_style = styles["Title"]
    title_style.fontName = STORY_FONT_BOLD
    title_style.fontSize = 36
    title_style.textColor = colors.HexColor('#4E342E')
    title_style.leading = 42
    title_style.spaceAfter = 40

    body_text_style = styles["Normal"]
    body_text_style.fontName = STORY_FONT
    body_text_style.fontSize = 14
    body_text_style.leading = 20
    body_text_style.alignment = TA_CENTER
    body_text_style.textColor = colors.HexColor('#212121')

    # Style for the text box
    from reportlab.platypus import Table, TableStyle
    
    story = []

    # --- Cover Page ---
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(f"<b>{story_data.get('title', 'Untitled Story')}</b>", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    scenes = story_data.get("scenes", [])
    cover_img_path = None
    if scenes:
        img_path = scenes[0].get("image_path")
        if img_path:
            abs_path = os.path.join(images_dir, os.path.basename(img_path))
            if os.path.exists(abs_path):
                cover_img_path = abs_path

    if cover_img_path:
        try:
            # Photo frame effect using a table
            img = RLImage(cover_img_path, width=4.5 * inch, height=4.5 * inch)
            img_table = Table([[img]], colWidths=[4.7 * inch], rowHeights=[4.7 * inch])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), colors.white),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDBDBD')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(img_table)
        except:
            pass
    
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("<i>Authored by Magic & MyAIStorybook</i>", body_text_style))
    story.append(PageBreak())

    # --- Scenes ---
    for i, scene in enumerate(scenes, start=1):
        # Image in Photo Frame
        img_path = scene.get("image_path")
        abs_path = os.path.join(images_dir, os.path.basename(img_path)) if img_path else ""

        if os.path.exists(abs_path):
            try:
                img = RLImage(abs_path, width=5 * inch, height=3.5 * inch)
                img_table = Table([[img]], colWidths=[5.2 * inch], rowHeights=[3.7 * inch])
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (-1,-1), colors.white),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ]))
                story.append(img_table)
                story.append(Spacer(1, 25))
            except Exception as e:
                print(f"⚠️ Failed to embed image: {abs_path} ({e})")
        
        # Text in a colored rounded box
        text_content = scene.get("text", "")
        # Use a table for the rounded box effect
        text_para = Paragraph(text_content, body_text_style)
        
        # Soft pastel color for the text box based on scene index
        box_colors = ['#E3F2FD', '#F1F8E9', '#FFF3E0', '#F3E5F5', '#E0F2F1']
        current_box_color = box_colors[(i-1) % len(box_colors)]
        
        text_table = Table([[text_para]], colWidths=[5.5 * inch])
        text_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(current_box_color)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDBDBD')),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ]))
        
        story.append(text_table)
        
        if i != len(scenes):
            story.append(PageBreak())

    # --- Build final PDF with background and border ---
    doc.build(story, onFirstPage=draw_background_and_border, onLaterPages=draw_background_and_border)
    print(f"✅ Redesigned V2 PDF created successfully at: {pdf_path}")
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

