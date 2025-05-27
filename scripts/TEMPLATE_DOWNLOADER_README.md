# Template Downloader Documentation

## Overview

This documentation covers the template downloading functionality for the JuniorAI project. The system provides multiple approaches to automatically download PowerPoint templates selected by the AI-powered dual template selector.

## 🎯 Features

✅ **Automated Downloads**: Download templates directly from Microsoft Create  
✅ **Multiple Strategies**: Selenium automation + direct HTTP requests  
✅ **Smart Fallbacks**: Automatic retry with different methods  
✅ **Integration Ready**: Works seamlessly with dual template selector  
✅ **Manual Backup**: Provides manual download instructions for failed cases  
✅ **Progress Tracking**: Detailed reporting and status tracking  

## 📁 File Structure

```
scripts/
├── template_downloader.py              # Full-featured Selenium downloader
├── simple_template_downloader.py       # Lightweight requests-based downloader
├── select_and_download_templates.py    # Integrated workflow script
├── dual_template_selections.json       # AI-selected templates (input)
└── template/
    ├── downloaded_templates/            # Downloaded .pptx files
    ├── download_report.txt             # Download status report
    └── simple_download_report.txt      # Simple downloader report
```

## 🚀 Quick Start

### Option 1: Complete Workflow (Recommended)
```bash
# Interactive mode - guides you through the process
python select_and_download_templates.py --interactive

# Direct content input
python select_and_download_templates.py "Business presentation about quarterly results for executives"

# From content file
echo "Educational presentation about AI for beginners" > my_content.txt
python select_and_download_templates.py --content-file my_content.txt
```

### Option 2: Download Only (if you already have selections)
```bash
# Simple downloader (no dependencies)
python simple_template_downloader.py

# Full-featured downloader (requires Selenium)
python template_downloader.py
```

## 📋 Available Scripts

### 1. `select_and_download_templates.py` - Complete Workflow

**Purpose**: End-to-end solution from content to downloaded templates  
**Dependencies**: All modules + Gemini AI API key  

```bash
# Usage examples
python select_and_download_templates.py --interactive
python select_and_download_templates.py "Your content here"
python select_and_download_templates.py --content-file content.txt --output-dir ./my_templates
python select_and_download_templates.py --interactive --use-selenium --skip-download
```

**Arguments**:
- `content`: Direct content input (positional)
- `--interactive`: Interactive mode for content input
- `--content-file`: Path to text file with content
- `--requirements`: Additional requirements
- `--output-dir`: Directory to save templates (default: `./template`)
- `--use-selenium`: Use Selenium downloader instead of simple downloader
- `--skip-download`: Only run template selection

### 2. `template_downloader.py` - Full-Featured Downloader

**Purpose**: Advanced downloader using Selenium web automation  
**Dependencies**: `selenium`, `webdriver-manager`, Chrome browser  

```bash
# Basic usage
python template_downloader.py

# Custom settings
python template_downloader.py --selections-file custom_selections.json --output-dir ./templates --headless --timeout 60
```

**Features**:
- Automated web browsing and clicking
- Handles JavaScript-heavy sites
- Automatic Chrome driver management
- Configurable timeouts and options
- Full error handling and retries

### 3. `simple_template_downloader.py` - Lightweight Downloader

**Purpose**: Simple HTTP-based downloader with minimal dependencies  
**Dependencies**: `requests` (included in Python)  

```bash
# Basic usage
python simple_template_downloader.py

# Custom settings
python simple_template_downloader.py --selections-file custom_selections.json --output-dir ./templates
```

**Features**:
- Fast and lightweight
- Direct HTTP requests
- Multiple URL patterns
- Manual download instructions for failures
- No browser automation required

## 🔧 Setup & Installation

### 1. Basic Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up Gemini AI API key (for template selection)
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### 2. Selenium Setup (for advanced downloader)
```bash
# Chrome browser is required (will be detected automatically)
# ChromeDriver will be downloaded automatically by webdriver-manager

# For headless operation (no browser window), no additional setup needed
# For debugging with visible browser, ensure Chrome is installed
```

### 3. Verify Setup
```bash
# Test the simple downloader
python simple_template_downloader.py --help

# Test the complete workflow (requires API key)
python select_and_download_templates.py --help
```

## 📊 Download Strategies

### Strategy 1: Direct URL Patterns
The downloaders try common Microsoft Create URL patterns:
- `https://create.microsoft.com/api/template/{id}/download`
- `https://create.microsoft.com/en-us/template/{id}/download`
- `https://create.microsoft.com/download/{id}`
- `https://templates.office.com/en-us/templates/{id}`

### Strategy 2: Preview URL Analysis
Constructs download URLs from preview image URLs in the template database.

### Strategy 3: Web Automation (Selenium only)
- Navigates to template pages
- Finds and clicks download buttons
- Handles authentication if needed
- Waits for download completion

### Strategy 4: Manual Fallback
Provides detailed instructions for manual download of failed templates.

## 📄 Input Format

The downloaders read from `dual_template_selections.json` with this structure:

```json
{
  "selection_metadata": {
    "total_templates_analyzed": 50,
    "top_selections": 2,
    "selection_timestamp": "2025-01-27 12:28:52"
  },
  "selections": [
    {
      "rank": 1,
      "match_details": {
        "template_id": "geometric-annual-presentation-d3b75063-ff25-434d-b12c-efeaf07d16c3",
        "template_title": "Geometric annual presentation",
        "confidence_score": 0.95
      },
      "template_details": {
        "id": "geometric-annual-presentation-d3b75063-ff25-434d-b12c-efeaf07d16c3",
        "title": "Geometric annual presentation",
        "preview_url": "https://cdn.create.microsoft.com/...",
        "category": "Business",
        "theme": "Modern"
      }
    }
  ]
}
```

## 📁 Output Structure

```
template/
├── downloaded_templates/
│   ├── Geometric_annual_presentation_d3b75063.pptx
│   ├── Shapes_presentation_ab1f0ecd.pptx
│   └── ...
├── download_report.txt
└── simple_download_report.txt
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "Selenium not available"
```bash
pip install selenium webdriver-manager
```

#### 2. "Chrome driver issues"
- Ensure Chrome browser is installed
- Driver is downloaded automatically by webdriver-manager
- For corporate environments, check firewall/proxy settings

#### 3. "No templates found to download"
- Verify `dual_template_selections.json` exists
- Check file has valid template selections
- Ensure file path is correct

#### 4. "Download failures"
- Microsoft Create may have changed their URL structure
- Some templates may require authentication
- Use manual download instructions provided in reports

#### 5. "API key errors" (for template selection)
```bash
# Set up your Gemini API key
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### Debug Mode

```bash
# Run with visible browser (Selenium)
python template_downloader.py --no-headless

# Check detailed logs
python template_downloader.py --verbose

# Test single template manually
python -c "from template_downloader import MicrosoftTemplateDownloader; d=MicrosoftTemplateDownloader('./test'); print(d.get_download_url('template-id-here'))"
```

## 🎯 Integration Examples

### With Existing Workflow
```python
# In your main presentation generation script
from select_and_download_templates import select_templates, download_templates

# Get user content (from your UI/CLI)
user_content = get_user_presentation_content()

# Select and download templates
selections_file = select_templates(user_content)
if selections_file:
    download_templates(selections_file, "./output/templates")
    
# Continue with your presentation generation...
```

### Batch Processing
```python
# Process multiple content files
import os
from pathlib import Path

content_dir = Path("./content_files")
for content_file in content_dir.glob("*.txt"):
    with open(content_file) as f:
        content = f.read()
    
    selections_file = select_templates(content)
    if selections_file:
        output_dir = f"./templates/{content_file.stem}"
        download_templates(selections_file, output_dir)
```

## 📝 Best Practices

1. **Start Simple**: Use `simple_template_downloader.py` first
2. **Check Dependencies**: Ensure all required packages are installed
3. **Monitor Downloads**: Check reports for failed downloads
4. **Backup Plan**: Always have manual download instructions ready
5. **Rate Limiting**: Add delays between downloads to be respectful
6. **Error Handling**: Implement proper error handling in integrations
7. **File Management**: Organize downloads by project/date

## 🔄 Future Improvements

- [ ] Support for other template sources (beyond Microsoft Create)
- [ ] Parallel downloading for better performance
- [ ] Template caching to avoid re-downloads
- [ ] Better authentication handling
- [ ] Template preview generation
- [ ] Integration with cloud storage services

## 📞 Support

For issues with template downloading:

1. Check this documentation
2. Review error messages and logs
3. Try the simple downloader first
4. Use manual download instructions as backup
5. Check if Microsoft Create website structure has changed

---

**Ready to download templates?** Start with:
```bash
python select_and_download_templates.py --interactive
``` 