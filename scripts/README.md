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
│ 1.5. INTELLIGENT SLIDE ORGANIZATION │
│ • Analyze slides with Gemini AI     │
│ • Determine relevance to user needs │
│ • Remove irrelevant slides          │
│ • Reorder slides for logical flow   │
│ • Save to slide_details_reorganized │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 2. AI CONTENT MODIFICATION STEP     │
│ • Read user_content.txt             │
│ • Send reorganized slides + content │
│   to Gemini AI                      │
│ • Generate updated content          │
│ • Save to slide_details_updated.json│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│ 3. REORGANIZED PRESENTATION CREATION│
│ • Create new presentation structure │
│ • Apply slide removal/reordering    │
│ • Update content from JSON          │
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
- **Reorganized**: `content/slide_details_reorganized.json` (AI-reorganized slides)
- **Modified**: `content/slide_details_updated.json` (AI-updated content)
- **Output**: `output/template_updated.pptx` (final presentation)

### Dependencies
- `extract_slide_details.py` - Extracts slide information from PowerPoint files
- `intelligent_slide_organizer.py` - AI-powered slide analysis and reorganization
- `create_presentation_from_reorganized_json.py` - Creates presentations from reorganized data
- `update_presentation_from_json.py` - Updates PowerPoint files with JSON data
- `google.generativeai` - Google Gemini AI integration

## TODOs

### ✅ COMPLETED: Intelligent Slide Removal and Reordering
**Ability to remove and reorder slides from the existing template**
- ✅ Implemented Gemini AI logic to analyze user requirements and determine slide relevance
- ✅ Added functionality to intelligently remove slides that don't match the content theme
- ✅ Implemented slide reordering for optimal logical flow
- ✅ Ensured slide numbering and references are updated after reorganization
- ✅ Maintained presentation flow and coherence after slide removal/reordering

**New Features Added:**
- `intelligent_slide_organizer.py` - AI-powered slide analysis and decision making
- `create_presentation_from_reorganized_json.py` - Presentation creation with reorganized structure
- Integrated workflow step 1.5 for intelligent slide organization
- Comprehensive AI prompting for slide relevance scoring and reasoning

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