# Data Flow Diagram (DFD) Specification
## MyAIStorybook - System Level Processing

**Tool:** Draw.io (https://app.diagrams.net/)  
**Notation:** Gane-Sarson (recommended) or Yourdon  
**Chapter:** 3, Section 3.3.5

---

## Level 0 DFD (Context Diagram)

### Elements:

**External Entity:**
- User (rectangle)

**Process:**
- 0: MyAIStorybook System (circle)

**Data Flows:**
- User → System: "Story Prompt + Generation Options"
- System → User: "Generated Story + Images + PDF"

### Description:
Simple context showing the system as a black box with inputs and outputs.

---

## Level 1 DFD (Decomposed System)

### Processes (Circles):

1. **1.0 Validate & Enhance Input**
   - Input: Raw Prompt (from User)
   - Output: Enhanced Prompt (to 2.0, D1)
   - Description: Prompt Agent validates and classifies prompt

2. **2.0 Generate Story Narrative**
   - Input: Enhanced Prompt (from D1)
   - Output: Story Draft (to D2, 3.0, 4.0)
   - Description: Writer Agent uses Ollama to create story structure

3. **3.0 Generate Scene Illustrations**
   - Input: Scene Descriptions (from D2)
   - Output: Image Files (to D3)
   - Description: Image Agent creates PNG files using Stable Diffusion
   - Note: Conditional based on user toggle

4. **4.0 Review & Validate Quality**
   - Input: Story Draft (from D2)
   - Output: Validation Report (to D4), Reviewed Story (to 5.0)
   - Description: Reviewer Agent checks coherence and appropriateness

5. **5.0 Edit & Format Output**
   - Input: Reviewed Story (from 4.0)
   - Input: Images (from D3) - optional
   - Output: Final Story (to D6), PDF Export (to D7)
   - Description: Editor Agent polishes and generates PDF

6. **6.0 Evaluate Story Metrics**
   - Input: Final Story (from D6)
   - Output: Quality Metrics (to D8)
   - Description: Background evaluation for analysis
   - Note: Non-blocking, async

### Data Stores (Parallel Lines):

- **D1: Prompts** - Stores enhanced prompts
- **D2: Drafts** - Stores writer agent outputs
- **D3: Images** - Stores generated PNG files
- **D4: Reviews** - Stores reviewer feedback
- **D5: Edits** - Stores editor outputs
- **D6: Stories** - Stores final story JSON
- **D7: Exports** - Stores PDF files
- **D8: Evaluations** - Stores quality metrics

### Data Flows (Arrows with Labels):

#### From User:
- User → 1.0: "Raw Story Prompt + Image Toggle"

#### Between Processes:
- 1.0 → D1: "Enhanced Prompt"
- D1 → 2.0: "Enhanced Prompt"
- 2.0 → D2: "Story Draft (3 scenes)"
- D2 → 3.0: "Scene Descriptions" (if images enabled)
- D2 → 4.0: "Story Draft"
- 3.0 → D3: "Generated Images"
- 4.0 → D4: "Validation Report"
- 4.0 → 5.0: "Reviewed Story"
- D3 → 5.0: "Image Files" (optional)
- 5.0 → D6: "Final Story JSON"
- 5.0 → D7: "PDF Export"
- D6 → 6.0: "Final Story"
- 6.0 → D8: "Quality Metrics"

#### To User:
- D6 → User: "Story JSON with Image URLs"
- D7 → User: "PDF Download" (automatic)

---

## Draw.io Step-by-Step Instructions

### Level 0 DFD:
1. Create new blank diagram
2. Add rectangle for "User" (external entity)
3. Add large circle for "0: MyAIStorybook System"
4. Add two arrows:
   - User → System (label: "Story Prompt + Options")
   - System → User (label: "Generated Story + Images + PDF")
5. Use different colors: External entities (yellow), Process (blue)

### Level 1 DFD:
1. Create new diagram or add to same file
2. Add 6 circles for processes 1.0 through 6.0
3. Add 8 parallel line pairs for data stores D1-D8
4. Add rectangle for User (external entity)
5. Connect all elements with arrows per specification above
6. Label each arrow clearly
7. Use color coding:
   - External entities: Yellow (#FFFACD)
   - Processes: Blue (#87CEEB)
   - Data stores: Green (#90EE90)
   - Data flows: Black arrows with labels

### Positioning:
- User at top left
- Processes in center (arrange in logical flow)
- Data stores on sides or bottom
- Minimize crossing lines

### Export:
- File → Export as → PNG
- Select "Transparent Background"
- Choose "300 DPI" or "4x" zoom
- Save as `dfd_level_0.png` and `dfd_level_1.png`
- Copy to `document/FYP1/ThesisFigs/`

---

## Example Text Description (for understanding):

**Data Flow Example:**
```
User submits a story prompt which enters the system at process 1.0 
(Validate & Enhance Input). The enhanced prompt is stored in D1 
(Prompts data store) and flows to process 2.0 (Generate Story 
Narrative), which uses the Ollama LLM to create a story draft. This 
draft is stored in D2 (Drafts). If images are requested, scene 
descriptions flow from D2 to process 3.0 (Generate Scene 
Illustrations), which creates PNG files stored in D3 (Images). 
Meanwhile, the story draft also flows to process 4.0 (Review & 
Validate Quality), which stores feedback in D4 (Reviews) and sends 
the reviewed story to process 5.0 (Edit & Format Output). Process 
5.0 combines the reviewed story with images from D3 (if available), 
creates the final story stored in D6 (Stories), and generates a PDF 
stored in D7 (Exports). Finally, the story from D6 flows to process 
6.0 (Evaluate Story Metrics) which runs asynchronously and stores 
metrics in D8 (Evaluations). The final story JSON with image URLs 
flows back to the User.
```

---

## Validation Checklist

- [ ] All processes numbered and named
- [ ] All data stores labeled D1-D8
- [ ] External entity (User) clearly marked
- [ ] All data flows have arrows and labels
- [ ] No processes directly connected (must flow through data store or external entity)
- [ ] Consistent notation throughout (Gane-Sarson or Yourdon)
- [ ] Clear, readable labels
- [ ] Logical layout with minimal crossing
- [ ] Color coding for clarity
- [ ] High-resolution export (300 DPI minimum)

---

**Estimated Time:** 2-3 hours for both levels

**Tip:** Create Level 0 first to understand the big picture, then decompose into Level 1.

