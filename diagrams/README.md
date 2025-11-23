# MyAIStorybook - Diagrams Directory

This directory contains all diagram source files and specifications for the FYP documentation.

## 📁 Directory Contents

### Main Guide
- **`DIAGRAMS_GUIDE.md`** - Complete guide with instructions, priorities, and timelines ⭐ START HERE

### Ready-to-Use Mermaid Files (.mmd)
1. ✅ `class_diagram.mmd` - Story, Scene, and Agent class hierarchy
2. ✅ `sequence_diagram.mmd` - Multi-agent story generation flow
3. ✅ `state_diagram.mmd` - Story generation lifecycle states
4. ✅ `activity_diagram.mmd` - Complete workflow with decision points
5. ✅ `domain_model.mmd` - Entity-relationship diagram
6. ✅ `architecture_diagram/architecture_diagram.mmd` - Full system architecture (already exists)

### Other Formats
- ✅ `use_case_diagram.puml` - PlantUML code for use cases (Mermaid doesn't support)
- ✅ `dfd_specification.md` - Detailed guide for creating DFD in Draw.io

## 🚀 Quick Start

### Option 1: Online (Easiest)
1. Go to https://mermaid.live/
2. Copy content from any `.mmd` file
3. Paste in editor (instant preview!)
4. Click "Actions" → "PNG" or "SVG"
5. Download and save to `document/FYP1/ThesisFigs/`

### Option 2: VS Code (Best for editing)
1. Install "Mermaid Preview" extension in VS Code
2. Open any `.mmd` file
3. Right-click → "Preview Mermaid"
4. Edit and see live updates
5. Export when satisfied

### Option 3: Command Line (For automation)
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG (2000px width)
mmdc -i class_diagram.mmd -o ../document/FYP1/ThesisFigs/class_diagram.png -w 2000

# Or generate all at once
for file in *.mmd; do
  mmdc -i "$file" -o "../document/FYP1/ThesisFigs/${file%.mmd}.png" -w 2000
done
```

## 📋 Diagram Status Checklist

### High Priority (Do First)
- [ ] **Use Case Diagram** - Use PlantUML online or Draw.io
- [ ] **Class Diagram** - Use `class_diagram.mmd` 
- [ ] **Architecture Diagram** - Export existing `architecture_diagram.mmd`

### Medium Priority
- [ ] **Sequence Diagram** - Use `sequence_diagram.mmd`
- [ ] **Activity Diagram** - Use `activity_diagram.mmd`
- [ ] **State Diagram** - Use `state_diagram.mmd`

### Lower Priority
- [ ] **Data Flow Diagram** - Use Draw.io with `dfd_specification.md` guide
- [ ] **Domain Model** - Use `domain_model.mmd` (or reuse Class Diagram)

## 🛠️ Tools & Links

### Mermaid
- **Online Editor**: https://mermaid.live/
- **Documentation**: https://mermaid.js.org/
- **VS Code Extension**: Search "Mermaid Preview"

### PlantUML
- **Online Editor**: https://www.plantuml.com/plantuml/
- **Documentation**: https://plantuml.com/

### Draw.io
- **Online Editor**: https://app.diagrams.net/
- **Desktop App**: https://github.com/jgraph/drawio-desktop/releases

## 📐 Export Guidelines

### Resolution
- **Minimum**: 1920px width
- **Recommended**: 2000-2400px width
- **DPI for LaTeX**: 300 DPI minimum

### Format
- **PNG**: Best for most diagrams (with transparent background)
- **SVG**: Best for scaling (use if LaTeX supports)
- **PDF**: Alternative for high-quality printing

### Naming Convention
```
class_diagram.png
sequence_diagram.png
state_diagram.png
activity_diagram.png
use_case_diagram.png
architecture_diagram.png
dfd_level_0.png
dfd_level_1.png
domain_model.png
```

## 🎨 Style Consistency

All diagrams use consistent color scheme:
- **Success/Positive**: Green (#90EE90)
- **Error/Negative**: Red/Pink (#FFB6C1)
- **Process/Info**: Blue (#87CEEB)
- **Data/Warning**: Yellow (#FFFACD)
- **Background**: Purple/Lavender (#E6E6FA)

## 📝 Inserting in LaTeX

Example for any diagram:
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{ThesisFigs/class_diagram.png}
\caption{Class Diagram showing Story, Scene, and Agent hierarchy}
\label{fig:class-diagram}
\end{figure}
```

Then reference in text: `As shown in Figure~\ref{fig:class-diagram}...`

## 💡 Tips

1. **Start with high priority diagrams** - They're most important for evaluation
2. **Use Mermaid Live for instant preview** - Fastest way to see results
3. **Keep source files** - Always save `.mmd` or `.puml` files for future edits
4. **Test in LaTeX early** - Insert one diagram to verify size and quality
5. **Ask for feedback** - Show diagrams to team members before finalizing

## 🆘 Troubleshooting

**Mermaid syntax errors?**
→ Check https://mermaid.js.org/intro/ for syntax reference

**Export looks blurry?**
→ Increase width to 2000px or higher

**PlantUML not rendering?**
→ Try the online editor first, then paste working code elsewhere

**LaTeX shows diagram too small/large?**
→ Adjust width parameter: `[width=0.5\textwidth]` to `[width=1.0\textwidth]`

**Can't decide which tool to use?**
→ Read `DIAGRAMS_GUIDE.md` section "Tool Recommendations"

---

**Questions?** Check `DIAGRAMS_GUIDE.md` for detailed instructions on each diagram type!

**Good luck!** 🎓 Remember: Start with Priority 1, they make the biggest impact.

