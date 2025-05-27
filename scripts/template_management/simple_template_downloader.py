#!/usr/bin/env python3
"""
Simple Template Downloader
==========================

A lightweight alternative to download PowerPoint templates from the selections file.
This version uses requests to attempt direct downloads and provides fallback methods.

Usage:
    python simple_template_downloader.py
    python simple_template_downloader.py --selections-file custom_selections.json
"""

import json
import os
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import argparse

@dataclass
class SimpleTemplateInfo:
    """Simple template information for downloading"""
    template_id: str
    template_title: str
    preview_url: str
    local_filename: str
    download_status: str = "pending"

class SimpleTemplateDownloader:
    """
    Simple template downloader using requests and known URL patterns.
    """
    
    def __init__(self, output_dir: str = "./template"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create downloads subdirectory
        self.downloads_dir = self.output_dir / "downloaded_templates"
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Session for requests with server-optimized headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print(f"📁 Downloads will be saved to: {self.downloads_dir}")
    
    def load_template_selections(self, selections_file: str) -> List[SimpleTemplateInfo]:
        """Load template selections from JSON file"""
        try:
            if not os.path.exists(selections_file):
                print(f"❌ Selections file not found: {selections_file}")
                return []
            
            with open(selections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            templates = []
            for selection in data.get('selections', []):
                template_details = selection.get('template_details', {})
                template_id = template_details.get('id', '')
                template_title = template_details.get('title', 'Unknown Template')
                preview_url = template_details.get('preview_url', '')
                
                if template_id:
                    # Create safe filename
                    safe_title = "".join(c for c in template_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    filename = f"{safe_title}_{template_id[:8]}.pptx"
                    
                    template_info = SimpleTemplateInfo(
                        template_id=template_id,
                        template_title=template_title,
                        preview_url=preview_url,
                        local_filename=filename
                    )
                    templates.append(template_info)
            
            print(f"📋 Loaded {len(templates)} templates for download")
            return templates
            
        except Exception as e:
            print(f"❌ Error loading template selections: {e}")
            return []
    
    def try_direct_download(self, template_info: SimpleTemplateInfo) -> bool:
        """
        Try to download template using known URL patterns
        
        Args:
            template_info: Template information
            
        Returns:
            True if download was successful
        """
        # Common Microsoft Create download URL patterns
        download_url_patterns = [
            f"https://create.microsoft.com/api/template/{template_info.template_id}/download",
            f"https://create.microsoft.com/en-us/template/{template_info.template_id}/download",
            f"https://create.microsoft.com/download/{template_info.template_id}",
            f"https://templates.office.com/en-us/templates/{template_info.template_id}",
        ]
        
        target_file = self.downloads_dir / template_info.local_filename
        
        for url_pattern in download_url_patterns:
            try:
                print(f"🔄 Trying download URL: {url_pattern}")
                response = self.session.get(url_pattern, timeout=30, allow_redirects=True)
                
                # Check if response contains PowerPoint data
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Check for PowerPoint content
                    if ('application/vnd.openxmlformats-officedocument.presentationml.presentation' in content_type or
                        'application/vnd.ms-powerpoint' in content_type or
                        '.pptx' in response.url.lower() or
                        len(response.content) > 10000):  # Assume files > 10KB might be valid
                        
                        # Save the file
                        with open(target_file, 'wb') as f:
                            f.write(response.content)
                        
                        # Verify file size is reasonable
                        if target_file.stat().st_size > 5000:  # At least 5KB
                            print(f"✅ Successfully downloaded: {template_info.template_title}")
                            template_info.download_status = "completed"
                            return True
                        else:
                            target_file.unlink()  # Remove small/invalid file
                
            except Exception as e:
                print(f"⚠️  Failed to download from {url_pattern}: {e}")
                continue
        
        return False
    
    def download_via_preview_url(self, template_info: SimpleTemplateInfo) -> bool:
        """
        Try to find download link by analyzing preview URL structure
        
        Args:
            template_info: Template information
            
        Returns:
            True if download was successful
        """
        if not template_info.preview_url:
            return False
        
        try:
            # Extract base URL and try to construct download URL
            base_parts = template_info.preview_url.split('/')
            if len(base_parts) >= 7:
                # Try to construct download URL from preview URL pattern
                base_url = '/'.join(base_parts[:7])  # Keep protocol + domain + path parts
                download_url = f"{base_url}/download"
                
                print(f"🔄 Trying constructed download URL: {download_url}")
                response = self.session.get(download_url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200 and len(response.content) > 10000:
                    target_file = self.downloads_dir / template_info.local_filename
                    
                    with open(target_file, 'wb') as f:
                        f.write(response.content)
                    
                    if target_file.stat().st_size > 5000:
                        print(f"✅ Successfully downloaded via preview URL: {template_info.template_title}")
                        template_info.download_status = "completed"
                        return True
                    else:
                        target_file.unlink()
        
        except Exception as e:
            print(f"⚠️  Failed to download via preview URL: {e}")
        
        return False
    
    def generate_manual_download_instructions(self, templates: List[SimpleTemplateInfo]) -> str:
        """Generate manual download instructions for failed templates"""
        failed_templates = [t for t in templates if t.download_status == "failed"]
        
        if not failed_templates:
            return ""
        
        instructions = [
            "",
            "🔧 MANUAL DOWNLOAD INSTRUCTIONS",
            "="*50,
            "The following templates could not be downloaded automatically.",
            "Please download them manually from the Microsoft Create website:",
            ""
        ]
        
        for template_info in failed_templates:
            template_url = f"https://create.microsoft.com/en-us/template/{template_info.template_id}"
            instructions.extend([
                f"📄 {template_info.template_title}",
                f"   URL: {template_url}",
                f"   Save as: {template_info.local_filename}",
                f"   Location: {self.downloads_dir}",
                ""
            ])
        
        instructions.extend([
            "Instructions:",
            "1. Visit each URL in your browser",
            "2. Click the 'Download' button",
            "3. Save the file with the specified filename",
            "4. Place the file in the specified location",
            ""
        ])
        
        return "\n".join(instructions)
    
    def download_templates(self, templates: List[SimpleTemplateInfo]) -> Dict[str, int]:
        """
        Download all selected templates
        
        Args:
            templates: List of template information objects
            
        Returns:
            Dictionary with download statistics
        """
        if not templates:
            print("❌ No templates to download")
            return {"total": 0, "completed": 0, "failed": 0}
        
        stats = {"total": len(templates), "completed": 0, "failed": 0}
        
        for i, template_info in enumerate(templates, 1):
            print(f"\n📥 Processing template {i}/{len(templates)}: {template_info.template_title}")
            
            # Check if file already exists
            target_file = self.downloads_dir / template_info.local_filename
            if target_file.exists():
                print(f"✅ Template already exists, skipping: {target_file}")
                template_info.download_status = "completed"
                stats["completed"] += 1
                continue
            
            # Try different download methods
            success = False
            
            # Method 1: Try direct download URLs
            if self.try_direct_download(template_info):
                success = True
            # Method 2: Try via preview URL
            elif self.download_via_preview_url(template_info):
                success = True
            
            if success:
                stats["completed"] += 1
            else:
                print(f"❌ Failed to download: {template_info.template_title}")
                template_info.download_status = "failed"
                stats["failed"] += 1
            
            # Small delay between downloads
            time.sleep(1)
        
        return stats
    
    def generate_download_report(self, templates: List[SimpleTemplateInfo], stats: Dict[str, int]) -> str:
        """Generate a download report"""
        report_lines = [
            "="*60,
            "📊 SIMPLE TEMPLATE DOWNLOAD REPORT",
            "="*60,
            f"Total templates: {stats['total']}",
            f"✅ Successfully downloaded: {stats['completed']}",
            f"❌ Failed downloads: {stats['failed']}",
            f"📁 Download directory: {self.downloads_dir}",
            "",
            "📋 DETAILED RESULTS:",
            "-"*40
        ]
        
        for template_info in templates:
            status_emoji = "✅" if template_info.download_status == "completed" else "❌"
            report_lines.append(f"{status_emoji} {template_info.template_title}")
            report_lines.append(f"   ID: {template_info.template_id}")
            report_lines.append(f"   Status: {template_info.download_status}")
            if template_info.download_status == "completed":
                report_lines.append(f"   File: {template_info.local_filename}")
            report_lines.append("")
        
        # Add manual download instructions if needed
        manual_instructions = self.generate_manual_download_instructions(templates)
        if manual_instructions:
            report_lines.append(manual_instructions)
        
        report_lines.extend([
            "="*60,
            "🎯 Download process completed!",
            "="*60
        ])
        
        return "\n".join(report_lines)

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description="Simple PowerPoint template downloader")
    parser.add_argument(
        "--selections-file", 
        default="./scrapers/content/dual_template_selections.json",
        help="Path to the template selections JSON file"
    )
    parser.add_argument(
        "--output-dir", 
        default="./template",
        help="Directory to save downloaded templates"
    )
    
    args = parser.parse_args()
    
    print("🚀 Simple Microsoft Template Downloader")
    print("=" * 50)
    
    # Initialize downloader
    downloader = SimpleTemplateDownloader(output_dir=args.output_dir)
    
    try:
        # Load template selections
        print(f"📂 Loading template selections from: {args.selections_file}")
        templates = downloader.load_template_selections(args.selections_file)
        
        if not templates:
            print("❌ No templates found to download")
            return
        
        print(f"📋 Found {len(templates)} templates to download:")
        for i, template_info in enumerate(templates, 1):
            print(f"   {i}. {template_info.template_title}")
        
        # Download templates
        print("\n🔄 Starting download process...")
        stats = downloader.download_templates(templates)
        
        # Generate and display report
        report = downloader.generate_download_report(templates, stats)
        print("\n" + report)
        
        # Save report to file
        report_file = Path(args.output_dir) / "simple_download_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")

if __name__ == "__main__":
    main() 