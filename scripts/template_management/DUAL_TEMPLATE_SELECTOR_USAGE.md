# Dual Template Selector Usage Guide

## Overview

The `intelligent_template_selector_dual.py` script provides an AI-powered system for selecting the two best matching PowerPoint templates from the Microsoft templates database based on user content and requirements.

## Key Features

✅ **AI-Powered Selection**: Uses Google Gemini AI to analyze content and match templates  
✅ **Dual Recommendations**: Returns the two best matching templates  
✅ **Flexible Parameters**: Accepts user content as parameters  
✅ **Multiple Usage Modes**: Command line, programmatic, and interactive modes  
✅ **Detailed Scoring**: Provides confidence scores and reasoning for selections  
✅ **Silent Mode**: Optional verbose output control  

## Function Signatures

### Main Function
```python
def select_dual_templates(
    user_content: str,                    # Required: Your presentation content
    templates_db_path: str = None,        # Optional: Path to templates database
    user_requirements: str = "",          # Optional: Additional requirements
    api_key: str = None,                  # Optional: Gemini API key
    model_name: str = "gemini-2.5-flash-preview-05-20",  # Optional: AI model
    verbose: bool = True,                 # Optional: Display detailed output
    save_results: bool = True             # Optional: Save results to JSON
) -> List[TemplateMatch]
```

### Simplified Function
```python
def select_templates_for_content(
    content: str,                         # Required: Presentation content
    requirements: str = "",               # Optional: Additional requirements
    **kwargs                              # Optional: Additional parameters
) -> List[TemplateMatch]
```

## Usage Examples

### 1. Basic Usage with Content Parameter

```python
from intelligent_template_selector_dual import select_dual_templates

user_content = """
I need to create a business presentation about our quarterly financial results.
The presentation should include revenue charts, expense analysis, and future projections.
The audience is our board of directors.
"""

matches = select_dual_templates(user_content=user_content)

for match in matches:
    print(f"Template: {match.template_title}")
    print(f"Confidence: {match.confidence_score:.2f}")
    print(f"ID: {match.template_id}")
```

### 2. With Additional Requirements

```python
content = """
Educational presentation about renewable energy for high school students.
Should cover solar, wind, and hydroelectric power sources.
"""

requirements = """
Need bright colors and modern design suitable for younger audience.
Should have good space for images and charts.
"""

matches = select_dual_templates(
    user_content=content,
    user_requirements=requirements
)
```

### 3. Silent Mode (No Verbose Output)

```python
matches = select_dual_templates(
    user_content="AI startup pitch deck for investors",
    verbose=False,
    save_results=False
)

# Handle results manually
if matches:
    best_template = matches[0]
    print(f"Best match: {best_template.template_title}")
```

### 4. Using Simplified Function

```python
from intelligent_template_selector_dual import select_templates_for_content

matches = select_templates_for_content(
    content="Digital marketing presentation for small businesses",
    requirements="Professional template for business training"
)
```

### 5. Programmatic Content Generation

```python
# Build content dynamically
topics = ["Machine Learning Basics", "Data Processing", "Model Training"]
audience = "Software developers new to ML"

content = f"""
Technical presentation covering: {', '.join(topics)}.
Target audience: {audience}.
Should include code examples and practical demonstrations.
"""

matches = select_dual_templates(
    user_content=content,
    user_requirements="Technical template with code display capabilities"
)
```

## Command Line Usage

### With User Content as Argument
```bash
python intelligent_template_selector_dual.py "Your presentation content here"
```

### Using Default Sample Content
```bash
python intelligent_template_selector_dual.py
```

### Using the Example Script
```bash
python example_dual_selector_usage.py
```

### Using the Runner Script
```bash
python run_dual_template_selector.py
python run_dual_template_selector.py --interactive
```

## Return Value Structure

The functions return a `List[TemplateMatch]` where each `TemplateMatch` contains:

```python
@dataclass
class TemplateMatch:
    template_id: str                    # Unique template identifier
    template_title: str                 # Human-readable template name
    confidence_score: float             # Overall confidence (0.0-1.0)
    reasoning: str                      # AI explanation for selection
    matching_factors: Dict[str, float]  # Detailed scoring breakdown
    use_case_alignment: float           # How well use cases match
    design_suitability: float           # Design appropriateness score
    content_compatibility: float        # Content structure compatibility
```

## Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
MODEL_NAME=gemini-2.5-flash-preview-05-20
```

### Default Paths
- Templates Database: `./scrapers/content/microsoft_templates.json`
- Output File: `./scrapers/content/dual_template_selections.json`

## AI Analysis Criteria

The system evaluates templates based on:

1. **Content Compatibility** (0.0-1.0): Template structure vs content type
2. **Use Case Alignment** (0.0-1.0): Template purpose vs presentation needs  
3. **Design Suitability** (0.0-1.0): Visual design vs audience/context
4. **Layout Appropriateness** (0.0-1.0): Layout types vs content structure
5. **Professional Fit** (0.0-1.0): Template formality vs professional context

## Content Analysis

The AI analyzes your content to understand:

- **Content Type**: Business, educational, technical, creative
- **Presentation Purpose**: Pitch, report, training, overview
- **Target Audience**: Executives, students, general public
- **Content Structure**: Data-heavy, narrative, visual

## Error Handling

Common scenarios handled:

- ❌ Empty or missing user content
- ❌ Missing API key
- ❌ Templates database not found
- ❌ AI request failures (with retry logic)
- ❌ Invalid AI responses (with fallback)

## Output Files

When `save_results=True` (default), creates:

```json
{
  "selection_metadata": {
    "total_templates_analyzed": 50,
    "top_selections": 2,
    "selection_timestamp": "2024-01-01 12:00:00"
  },
  "selections": [
    {
      "rank": 1,
      "match_details": { ... },
      "template_details": { ... }
    }
  ]
}
```

## Integration with Main Workflow

Use selected template IDs in the main presentation generation workflow:

```python
# Get template recommendations
matches = select_dual_templates(user_content="your content")

if matches:
    # Use the best template ID
    best_template_id = matches[0].template_id
    
    # Continue with main workflow using this template
    # (integration with existing presentation generation system)
```

## Best Practices

1. **Be Specific**: Provide detailed content descriptions
2. **Include Context**: Mention audience, purpose, and requirements
3. **Use Requirements**: Add specific design or functional requirements
4. **Handle Errors**: Always check if matches are returned
5. **Save Results**: Keep results for reference and debugging

## Examples in Action

See `example_dual_selector_usage.py` for comprehensive examples demonstrating:
- Basic usage patterns
- Advanced parameter configurations  
- Silent mode operation
- Programmatic content generation
- Error handling strategies

---

**Quick Start**: Pass your presentation content as the `user_content` parameter to get AI-powered template recommendations! 