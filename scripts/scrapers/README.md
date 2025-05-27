# Scrapers Directory

This directory contains all web scraping scripts and related files for the JuniorAI project.

## Files Overview

### Core Scraping Scripts
- **`template_scraper.py`** - Main Microsoft PowerPoint template scraper
  - Extracts template metadata, descriptions, features, and preview images
  - Supports both headless and GUI modes
  - Optimized for server deployment
  - Includes rate limiting and error handling

### Testing and Validation
- **`test_template_scraper.py`** - Comprehensive test suite for the template scraper
  - Tests template data structure validation
  - Tests JSON database format
  - Tests scraper functionality with different configurations

### Documentation
- **`SERVER_DEPLOYMENT_GUIDE.md`** - Complete guide for deploying scrapers on servers
  - Server setup instructions
  - Chrome/ChromeDriver installation
  - Performance optimization tips
  - Troubleshooting guide

## Usage

### Running the Template Scraper

Basic usage:
```bash
python3 template_scraper.py --headless --max-templates 20
```

With custom output location:
```bash
python3 template_scraper.py --headless --max-templates 50 --output ../content/templates.json
```

For debugging:
```bash
python3 template_scraper.py --headless --max-templates 5 --log-level DEBUG
```

### Running Tests

```bash
python3 test_template_scraper.py
```

## Output

The scrapers generate JSON files containing structured template data that can be used by:
- `intelligent_template_selector.py` - AI-powered template selection
- `create_presentation_from_reorganized_json.py` - Presentation generation
- Other components in the JuniorAI pipeline

## Dependencies

All scraping scripts require the dependencies listed in the main `requirements.txt` file:
- selenium
- beautifulsoup4
- webdriver-manager
- requests

## Server Deployment

For production deployment, refer to `SERVER_DEPLOYMENT_GUIDE.md` for detailed instructions on setting up the scraping environment on various server platforms. 