"""
Template Management Package
==========================

This package contains all template selection and downloading functionality for JuniorAI.

Main Components:
- intelligent_template_selector_dual: AI-powered dual template selection
- improved_template_downloader: Server-optimized template downloading with Selenium
- simple_template_downloader: Lightweight template downloading with requests
- select_and_download_templates: Integrated workflow for selection and download

Usage:
    from template_management import select_dual_templates, ImprovedTemplateDownloader
"""

# Import main functions for easy access
from .intelligent_template_selector_dual import (
    select_dual_templates,
    select_templates_for_content,
    TemplateMatch,
    DualTemplateSelector
)

from .improved_template_downloader import (
    ImprovedTemplateDownloader,
    TemplateDownloadInfo
)

from .simple_template_downloader import (
    SimpleTemplateDownloader,
    SimpleTemplateInfo
)

from .select_and_download_templates import (
    select_templates
)

__all__ = [
    # Template Selection
    'select_dual_templates',
    'select_templates_for_content', 
    'TemplateMatch',
    'DualTemplateSelector',
    
    # Template Downloading
    'ImprovedTemplateDownloader',
    'SimpleTemplateDownloader',
    'TemplateDownloadInfo',
    'SimpleTemplateInfo',
    
    # Integrated Workflow
    'select_templates'
]

__version__ = "1.0.0"
__author__ = "JuniorAI Team" 