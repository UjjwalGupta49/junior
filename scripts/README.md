# Presentation Update Workflow

This script automates the process of updating PowerPoint presentations using AI-powered content generation through Google's Gemini AI.

## Working of this Script

The `main.py` script is a comprehensive workflow automation tool that:

1. **Extracts slide details** from an existing PowerPoint template
2. **Processes content** using Gemini AI to generate relevant presentation content
3. **Updates the presentation** with the AI-generated content
4. **Manages file operations** and cleanup automatically

The script uses Google's Gemini AI (model: `gemini-2.5-flash-preview-05-20`) to intelligently modify slide content based on user-provided requirements while maintaining the original template's structure and design.

## Flow of the Script

```
┌─────────────────────────────────────┐
│ 1. EXTRACTION STEP                  │
│ • Load template.pptx                │
│ • Extract slide details to JSON     │
│ • Save to slide_details.json        │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 2. AI MODIFICATION STEP             │
│ • Read user_content.txt             │
│ • Send slide details + user content │
│   to Gemini AI                      │
│ • Generate updated content          │
│ • Save to slide_details_updated.json│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 3. PRESENTATION UPDATE STEP         │
│ • Copy template.pptx to output/     │
│ • Apply updated content from JSON   │
│ • Generate template_updated.pptx    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 4. CLEANUP STEP                     │
│ • Remove __pycache__ directories    │
│ • Clean temporary files             │
└─────────────────────────────────────┘
```

### File Structure
- **Input**: `template/template.pptx` (original template)
- **User Content**: `user_content.txt` (content requirements)
- **Intermediate**: `content/slide_details.json` (extracted slide data)
- **Modified**: `content/slide_details_updated.json` (AI-updated content)
- **Output**: `output/template_updated.pptx` (final presentation)

### Dependencies
- `extract_slide_details.py` - Extracts slide information from PowerPoint files
- `update_presentation_from_json.py` - Updates PowerPoint files with JSON data
- `google.generativeai` - Google Gemini AI integration

## TODOs

### TODO 1: Intelligent Slide Removal
**Ability to remove slides from the existing template**
- Implement Gemini AI logic to analyze user requirements and determine which slides are unnecessary
- Add functionality to intelligently remove slides that don't match the content theme
- Ensure slide numbering and references are updated after removal
- Maintain presentation flow and coherence after slide removal

### TODO 2: Dynamic Image Updates
**Add a step to update images in the template to match the content**
- Integrate image generation or selection based on slide content
- Implement image replacement functionality in PowerPoint templates
- Add support for AI-generated images that match the presentation theme
- Ensure image quality and aspect ratios are maintained
- Consider adding image search and selection from stock photo APIs

### Additional Future Enhancements
- Add support for multiple template formats
- Implement batch processing for multiple presentations
- Add configuration file support for different AI models
- Enhance error handling and recovery mechanisms
- Add progress tracking and logging capabilities 