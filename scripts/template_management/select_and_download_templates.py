#!/usr/bin/env python3
"""
Select and Download Templates
============================

Integrated script that combines AI-powered template selection with automatic downloading.
This script:
1. Runs the dual template selector to find the best templates
2. Downloads the selected templates automatically
3. Provides a complete workflow from content to downloaded PowerPoint files

Usage:
    python select_and_download_templates.py "Your presentation content here"
    python select_and_download_templates.py --content-file content.txt
    python select_and_download_templates.py --interactive
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Add the scripts directory to the Python path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Import our modules
try:
    from .intelligent_template_selector_dual import select_dual_templates, TemplateMatch
    SELECTOR_AVAILABLE = True
except ImportError:
    SELECTOR_AVAILABLE = False
    print("⚠️  Dual template selector not available")

try:
    from .simple_template_downloader import SimpleTemplateDownloader
    SIMPLE_DOWNLOADER_AVAILABLE = True
except ImportError:
    SIMPLE_DOWNLOADER_AVAILABLE = False
    print("⚠️  Simple downloader not available")

try:
    from .template_downloader import MicrosoftTemplateDownloader
    SELENIUM_DOWNLOADER_AVAILABLE = True
except ImportError:
    SELENIUM_DOWNLOADER_AVAILABLE = False
    print("⚠️  Selenium downloader not available")

def get_user_content_interactive() -> str:
    """Get user content through interactive input"""
    print("📝 INTERACTIVE CONTENT INPUT")
    print("=" * 40)
    print("Please describe your presentation content:")
    print("(Press Ctrl+D or Ctrl+Z when finished, or type 'END' on a new line)")
    print()
    
    content_lines = []
    try:
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            content_lines.append(line)
    except EOFError:
        pass
    
    return '\n'.join(content_lines)

def get_user_requirements_interactive() -> str:
    """Get additional requirements through interactive input"""
    print("\n📋 ADDITIONAL REQUIREMENTS (optional)")
    print("=" * 40)
    print("Any specific design or layout requirements?")
    print("(Press Enter to skip, or describe your requirements)")
    
    try:
        requirements = input("> ")
        return requirements.strip()
    except EOFError:
        return ""

def load_content_from_file(file_path: str) -> str:
    """Load content from a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ Error reading content file {file_path}: {e}")
        return ""

def select_templates(user_content: str, user_requirements: str = "") -> Optional[str]:
    """
    Run template selection and return path to selections file
    
    Args:
        user_content: User's presentation content
        user_requirements: Additional requirements
        
    Returns:
        Path to selections file if successful, None otherwise
    """
    if not SELECTOR_AVAILABLE:
        print("❌ Template selector not available")
        return None
    
    if not user_content.strip():
        print("❌ User content is required")
        return None
    
    print("🧠 Running AI-powered template selection...")
    
    try:
        # Run dual template selection
        matches = select_dual_templates(
            user_content=user_content,
            user_requirements=user_requirements,
            verbose=True,
            save_results=True
        )
        
        if matches:
            # Return path to the selections file
            selections_file = "./scrapers/content/dual_template_selections.json"
            if os.path.exists(selections_file):
                return selections_file
            else:
                print(f"❌ Selections file not found: {selections_file}")
                return None
        else:
            print("❌ No templates selected")
            return None
            
    except Exception as e:
        print(f"❌ Error during template selection: {e}")
        return None

def download_templates(selections_file: str, output_dir: str, use_selenium: bool = False) -> bool:
    """
    Download templates from selections file
    
    Args:
        selections_file: Path to template selections JSON file
        output_dir: Directory to save templates
        use_selenium: Whether to use Selenium-based downloader
        
    Returns:
        True if download was successful
    """
    print(f"\n📥 Starting template download...")
    print(f"Selections file: {selections_file}")
    print(f"Output directory: {output_dir}")
    
    try:
        if use_selenium and SELENIUM_DOWNLOADER_AVAILABLE:
            print("🔧 Using Selenium-based downloader (headless mode)")
            downloader = MicrosoftTemplateDownloader(output_dir=output_dir, headless=True)
            templates = downloader.load_template_selections(selections_file)
            if templates:
                stats = downloader.download_templates(templates)
                success = stats["completed"] > 0
                return success
            else:
                print("❌ No templates found in selections file")
                return False
                
        elif SIMPLE_DOWNLOADER_AVAILABLE:
            print("🔧 Using simple request-based downloader (server-optimized)")
            downloader = SimpleTemplateDownloader(output_dir=output_dir)
            templates = downloader.load_template_selections(selections_file)
            if templates:
                stats = downloader.download_templates(templates)
                
                # Generate and display report
                report = downloader.generate_download_report(templates, stats)
                print("\n" + report)
                
                success = stats["completed"] > 0
                return success
            else:
                print("❌ No templates found in selections file")
                return False
        else:
            print("❌ No downloaders available")
            return False
            
    except Exception as e:
        print(f"❌ Error during template download: {e}")
        return False

def main():
    """Main function with comprehensive argument support"""
    parser = argparse.ArgumentParser(
        description="Select and download PowerPoint templates using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Direct content input
    python select_and_download_templates.py "Business presentation about Q4 results"
    
    # Interactive mode
    python select_and_download_templates.py --interactive
    
    # From content file
    python select_and_download_templates.py --content-file my_content.txt
    
    # With custom output directory
    python select_and_download_templates.py --interactive --output-dir ./my_templates
    
    # Use Selenium downloader
    python select_and_download_templates.py --interactive --use-selenium
        """
    )
    
    # Content input options (mutually exclusive)
    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument(
        "content", 
        nargs="?", 
        help="Presentation content as a string"
    )
    content_group.add_argument(
        "--content-file", 
        help="Path to text file containing presentation content"
    )
    content_group.add_argument(
        "--interactive", 
        action="store_true", 
        help="Interactive mode for content input"
    )
    
    # Optional arguments
    parser.add_argument(
        "--requirements", 
        default="", 
        help="Additional requirements or preferences"
    )
    parser.add_argument(
        "--output-dir", 
        default="./template",
        help="Directory to save downloaded templates"
    )
    parser.add_argument(
        "--use-selenium", 
        action="store_true",
        help="Use Selenium-based downloader (requires Selenium installation)"
    )
    parser.add_argument(
        "--skip-download", 
        action="store_true",
        help="Only run template selection, skip download"
    )
    
    args = parser.parse_args()
    
    print("🚀 AI-Powered Template Selection & Download")
    print("=" * 60)
    
    # Check dependencies
    if not SELECTOR_AVAILABLE:
        print("❌ Template selector not available")
        print("Please ensure intelligent_template_selector_dual.py is available")
        return
    
    # Get user content
    user_content = ""
    user_requirements = args.requirements
    
    if args.interactive:
        user_content = get_user_content_interactive()
        if not user_requirements:
            user_requirements = get_user_requirements_interactive()
    elif args.content_file:
        user_content = load_content_from_file(args.content_file)
    elif args.content:
        user_content = args.content
    
    if not user_content.strip():
        print("❌ No content provided")
        return
    
    print(f"\n📄 CONTENT SUMMARY:")
    print(f"Content length: {len(user_content)} characters")
    print(f"Content preview: {user_content[:200]}{'...' if len(user_content) > 200 else ''}")
    if user_requirements:
        print(f"Requirements: {user_requirements}")
    
    # Step 1: Select templates
    print(f"\n{'='*60}")
    print("STEP 1: AI TEMPLATE SELECTION")
    print(f"{'='*60}")
    
    selections_file = select_templates(user_content, user_requirements)
    if not selections_file:
        print("❌ Template selection failed")
        return
    
    print(f"✅ Template selection completed")
    print(f"📄 Selections saved to: {selections_file}")
    
    # Step 2: Download templates (unless skipped)
    if not args.skip_download:
        print(f"\n{'='*60}")
        print("STEP 2: TEMPLATE DOWNLOAD")
        print(f"{'='*60}")
        
        download_success = download_templates(
            selections_file=selections_file,
            output_dir=args.output_dir,
            use_selenium=args.use_selenium
        )
        
        if download_success:
            print("✅ Template download completed successfully!")
            print(f"📁 Downloaded templates are in: {args.output_dir}/downloaded_templates")
        else:
            print("⚠️  Template download had issues. Check the report for details.")
            print("💡 You may need to download some templates manually.")
    else:
        print("\n⏭️  Skipping download step as requested")
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 PROCESS COMPLETED")
    print(f"{'='*60}")
    print(f"✅ Template selection: Completed")
    if not args.skip_download:
        print(f"📥 Template download: {'Completed' if download_success else 'Partially completed'}")
    print(f"📄 Selection details: {selections_file}")
    if not args.skip_download:
        print(f"📁 Download directory: {args.output_dir}/downloaded_templates")
    
    print("\n🎉 Ready to create your presentation!")

if __name__ == "__main__":
    main() 