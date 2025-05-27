# Template Management Package

This package contains all template selection and downloading functionality for the JuniorAI project. The codebase has been organized into a dedicated package for better maintainability and modular design.

## 📁 Package Structure

```
scripts/
├── template_management/
│   ├── __init__.py                           # Package initialization with exports
│   ├── intelligent_template_selector_dual.py # AI-powered dual template selection
│   ├── intelligent_template_selector.py      # Original template selector
│   ├── improved_template_downloader.py       # Server-optimized Selenium downloader
│   ├── simple_template_downloader.py         # Lightweight requests-based downloader
│   ├── template_downloader.py                # Original template downloader
│   ├── select_and_download_templates.py      # Integrated workflow script
│   ├── run_dual_template_selector.py         # Standalone dual selector script
│   ├── example_dual_selector_usage.py        # Usage examples
│   ├── DUAL_TEMPLATE_SELECTOR_USAGE.md      # Dual selector documentation
│   ├── SERVER_OPTIMIZED_TEMPLATE_DOWNLOADER.md # Server optimization docs
│   └── README.md                             # This file
└── main.py                                   # Main workflow integration
```

## 🎯 Main Components

### 1. Template Selection

#### Dual Template Selector (`intelligent_template_selector_dual.py`)
- **Primary Function**: `select_dual_templates(user_content, templates_db_path, ...)`
- **Features**: 
  - AI-powered analysis using Google Gemini
  - Finds the two best matching templates
  - Detailed confidence scoring and reasoning
  - Saves results to JSON for downstream processing

#### Template Selector (`intelligent_template_selector.py`)
- **Primary Function**: `intelligent_template_selection_step(...)`
- **Features**: Single template selection with AI analysis

### 2. Template Downloading

#### Improved Template Downloader (`improved_template_downloader.py`)
- **Primary Class**: `ImprovedTemplateDownloader`
- **Features**:
  - Server-optimized headless Chrome automation
  - Selenium WebDriver for complex interactions
  - Auto-retry mechanisms
  - File validation and progress tracking

#### Simple Template Downloader (`simple_template_downloader.py`)
- **Primary Class**: `SimpleTemplateDownloader`
- **Features**:
  - Lightweight HTTP requests-based approach
  - Server-optimized headers
  - Fallback for environments without Selenium

### 3. Integrated Workflows

#### Select and Download (`select_and_download_templates.py`)
- **Primary Function**: `select_templates(user_content, ...)`
- **Features**: End-to-end template selection and download workflow

## 🚀 Usage

### Quick Start (Recommended)

```python
from template_management import select_dual_templates, ImprovedTemplateDownloader

# 1. Select templates using AI
user_content = "Create a business presentation about quarterly results"
matches = select_dual_templates(
    user_content=user_content,
    templates_db_path="./scrapers/content/microsoft_templates.json",
    verbose=True,
    save_results=True
)

# 2. Download selected templates
downloader = ImprovedTemplateDownloader(
    output_dir="./template",
    headless=True  # Server-optimized
)
templates = downloader.load_template_selections("./scrapers/content/dual_template_selections.json")
stats = downloader.download_templates(templates)
```

### Main Workflow Integration

The main workflow in `main.py` demonstrates the complete integration:

```python
from template_management import select_dual_templates, ImprovedTemplateDownloader

# Complete workflow:
# 1. Select two templates using AI
# 2. Download templates with headless Chrome
# 3. Process both templates through presentation pipeline
```

### Available Imports

```python
# Template Selection
from template_management import (
    select_dual_templates,
    select_templates_for_content,
    TemplateMatch,
    DualTemplateSelector
)

# Template Downloading
from template_management import (
    ImprovedTemplateDownloader,
    SimpleTemplateDownloader,
    TemplateDownloadInfo,
    SimpleTemplateInfo
)

# Integrated Workflow
from template_management import select_templates
```

## 🔧 Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key
MODEL_NAME=gemini-2.5-flash-preview-05-20  # optional
```

### File Paths
- **Templates Database**: `./scrapers/content/microsoft_templates.json`
- **Selection Results**: `./scrapers/content/dual_template_selections.json`
- **Download Directory**: `./template/downloaded_templates/`

## 📊 Server Optimization

All downloaders are optimized for server-side operation:
- **Headless by default**: No GUI requirements
- **Memory optimized**: Efficient Chrome options
- **Network optimized**: Smart retry and timeout handling
- **Error resilient**: Comprehensive error handling and reporting

## 🧪 Testing

```bash
# Test package imports
python3 -c "from template_management import select_dual_templates, ImprovedTemplateDownloader; print('✅ Imports working')"

# Test main workflow
python3 -c "from main import main; print('✅ Main workflow imports working')"

# Run standalone template selection
cd template_management
python3 run_dual_template_selector.py

# Run integrated workflow
python3 select_and_download_templates.py --interactive
```

## 📋 Migration Notes

### From Old Structure
If you had imports like:
```python
# OLD
from intelligent_template_selector_dual import select_dual_templates
from improved_template_downloader import ImprovedTemplateDownloader

# NEW
from template_management import select_dual_templates, ImprovedTemplateDownloader
```

### Path Updates
All scripts within the `template_management` package now use relative imports:
```python
# Within package files
from .intelligent_template_selector_dual import select_dual_templates
from .improved_template_downloader import ImprovedTemplateDownloader
```

## 🎯 Benefits of Reorganization

1. **Modular Design**: Clear separation of template functionality
2. **Easy Imports**: Single package for all template operations
3. **Better Maintainability**: Organized structure with clear dependencies
4. **Consistent Interface**: Unified API through package exports
5. **Documentation**: Centralized documentation and examples

## 📝 Version

- **Package Version**: 1.0.0
- **Author**: JuniorAI Team
- **Last Updated**: May 2024

---

For more detailed documentation, see the individual files and their docstrings within the package. 