#!/usr/bin/env python3
"""
Microsoft Template Downloader
============================

This script downloads PowerPoint templates selected by the AI-powered dual template selector.
It reads template IDs from dual_template_selections.json and downloads the actual .pptx files
from Microsoft Create.

Requirements:
    - selenium: For web automation
    - webdriver-manager: For automatic driver management
    - requests: For HTTP requests
    - beautifulsoup4: For HTML parsing

Usage:
    python template_downloader.py
    python template_downloader.py --selections-file custom_selections.json
    python template_downloader.py --output-dir custom_template_folder
"""

import json
import os
import time
import requests
import logging
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import argparse

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")

# BeautifulSoup for HTML parsing
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️  BeautifulSoup not available. Install with: pip install beautifulsoup4")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TemplateDownloadInfo:
    """Information about a template to download"""
    template_id: str
    template_title: str
    download_url: Optional[str] = None
    local_filename: str = ""
    download_status: str = "pending"  # pending, downloading, completed, failed

class MicrosoftTemplateDownloader:
    """
    Downloads PowerPoint templates from Microsoft Create based on AI selections.
    
    Uses Selenium to automate the download process from the Microsoft Create website.
    """
    
    def __init__(self, output_dir: str = "./template", headless: bool = True, timeout: int = 30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.base_url = "https://create.microsoft.com/en-us/template/"
        
        # Create downloads subdirectory
        self.downloads_dir = self.output_dir / "downloaded_templates"
        self.downloads_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized downloader with output directory: {self.output_dir}")
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with appropriate options"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Cannot setup web driver.")
            return False
        
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Configure download preferences
            download_prefs = {
                "download.default_directory": str(self.downloads_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", download_prefs)
            
            # Additional options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Setup driver with automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info("Chrome WebDriver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            return False
    
    def load_template_selections(self, selections_file: str) -> List[TemplateDownloadInfo]:
        """Load template selections from JSON file"""
        try:
            if not os.path.exists(selections_file):
                logger.error(f"Selections file not found: {selections_file}")
                return []
            
            with open(selections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            templates = []
            for selection in data.get('selections', []):
                template_details = selection.get('template_details', {})
                template_id = template_details.get('id', '')
                template_title = template_details.get('title', 'Unknown Template')
                
                if template_id:
                    # Create safe filename
                    safe_title = "".join(c for c in template_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    filename = f"{safe_title}_{template_id[:8]}.pptx"
                    
                    template_info = TemplateDownloadInfo(
                        template_id=template_id,
                        template_title=template_title,
                        local_filename=filename
                    )
                    templates.append(template_info)
            
            logger.info(f"Loaded {len(templates)} templates for download")
            return templates
            
        except Exception as e:
            logger.error(f"Error loading template selections: {e}")
            return []
    
    def get_download_url(self, template_id: str) -> Optional[str]:
        """
        Navigate to template page and extract download URL
        
        Args:
            template_id: The Microsoft template ID
            
        Returns:
            Download URL if found, None otherwise
        """
        if not self.driver:
            logger.error("WebDriver not initialized")
            return None
        
        try:
            template_url = f"{self.base_url}{template_id}"
            logger.info(f"Navigating to: {template_url}")
            
            self.driver.get(template_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for download button or link
            download_selectors = [
                "a[href*='download']",
                "button[aria-label*='Download']",
                "a[download]",
                ".download-button",
                ".btn-download",
                "[data-action='download']",
                "a[href*='.pptx']",
                "a[href*='powerpoint']"
            ]
            
            download_url = None
            for selector in download_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and ('.pptx' in href.lower() or 'download' in href.lower()):
                            download_url = href
                            break
                    if download_url:
                        break
                except:
                    continue
            
            # Alternative: Look for any PowerPoint-related links
            if not download_url:
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '.pptx' in href.lower():
                            download_url = href
                            break
                except:
                    pass
            
            if download_url:
                logger.info(f"Found download URL: {download_url}")
                return download_url
            else:
                logger.warning(f"No download URL found for template {template_id}")
                return None
                
        except TimeoutException:
            logger.error(f"Timeout loading template page: {template_id}")
            return None
        except Exception as e:
            logger.error(f"Error extracting download URL for {template_id}: {e}")
            return None
    
    def trigger_download(self, template_info: TemplateDownloadInfo) -> bool:
        """
        Trigger download for a template using Selenium
        
        Args:
            template_info: Template information including ID and title
            
        Returns:
            True if download was triggered successfully
        """
        if not self.driver:
            logger.error("WebDriver not initialized")
            return False
        
        try:
            template_url = f"{self.base_url}{template_info.template_id}"
            logger.info(f"Downloading template: {template_info.template_title}")
            logger.info(f"Template URL: {template_url}")
            
            self.driver.get(template_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for and click download button
            download_selectors = [
                "button[aria-label*='Download']",
                "a[download]",
                ".download-button",
                ".btn-download",
                "[data-action='download']",
                "button:contains('Download')",
                "a:contains('Download')"
            ]
            
            download_clicked = False
            for selector in download_selectors:
                try:
                    # Try to find and click download element
                    wait = WebDriverWait(self.driver, 5)
                    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    element.click()
                    download_clicked = True
                    logger.info(f"Successfully clicked download button: {selector}")
                    break
                except:
                    continue
            
            # Alternative: Look for any clickable download elements
            if not download_clicked:
                try:
                    elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') or contains(@aria-label, 'Download')]")
                    for element in elements:
                        if element.is_enabled() and element.is_displayed():
                            element.click()
                            download_clicked = True
                            logger.info("Successfully clicked download element via text search")
                            break
                except:
                    pass
            
            if download_clicked:
                # Wait a bit for download to start
                time.sleep(3)
                template_info.download_status = "downloading"
                return True
            else:
                logger.warning(f"Could not find download button for template {template_info.template_id}")
                template_info.download_status = "failed"
                return False
                
        except Exception as e:
            logger.error(f"Error triggering download for {template_info.template_id}: {e}")
            template_info.download_status = "failed"
            return False
    
    def wait_for_download_completion(self, template_info: TemplateDownloadInfo, max_wait: int = 120) -> bool:
        """
        Wait for download to complete and rename file appropriately
        
        Args:
            template_info: Template information
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if download completed successfully
        """
        logger.info(f"Waiting for download completion: {template_info.template_title}")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            # Check for downloaded files
            download_files = list(self.downloads_dir.glob("*.pptx"))
            temp_files = list(self.downloads_dir.glob("*.crdownload")) + list(self.downloads_dir.glob("*.tmp"))
            
            # If we have .pptx files and no temporary files, download is likely complete
            if download_files and not temp_files:
                # Find the most recent file
                latest_file = max(download_files, key=lambda f: f.stat().st_mtime)
                
                # Rename to our desired filename
                target_path = self.downloads_dir / template_info.local_filename
                
                try:
                    if target_path.exists():
                        target_path.unlink()  # Remove existing file
                    
                    latest_file.rename(target_path)
                    template_info.download_status = "completed"
                    logger.info(f"Download completed: {target_path}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error renaming downloaded file: {e}")
                    template_info.download_status = "failed"
                    return False
            
            time.sleep(2)
        
        logger.warning(f"Download timeout for template: {template_info.template_title}")
        template_info.download_status = "failed"
        return False
    
    def download_templates(self, templates: List[TemplateDownloadInfo]) -> Dict[str, int]:
        """
        Download all selected templates
        
        Args:
            templates: List of template information objects
            
        Returns:
            Dictionary with download statistics
        """
        if not templates:
            logger.warning("No templates to download")
            return {"total": 0, "completed": 0, "failed": 0}
        
        # Setup web driver
        if not self.setup_driver():
            logger.error("Failed to setup web driver")
            return {"total": len(templates), "completed": 0, "failed": len(templates)}
        
        stats = {"total": len(templates), "completed": 0, "failed": 0}
        
        try:
            for i, template_info in enumerate(templates, 1):
                logger.info(f"Processing template {i}/{len(templates)}: {template_info.template_title}")
                
                # Check if file already exists
                target_file = self.downloads_dir / template_info.local_filename
                if target_file.exists():
                    logger.info(f"Template already exists, skipping: {target_file}")
                    template_info.download_status = "completed"
                    stats["completed"] += 1
                    continue
                
                # Trigger download
                if self.trigger_download(template_info):
                    # Wait for completion
                    if self.wait_for_download_completion(template_info):
                        stats["completed"] += 1
                    else:
                        stats["failed"] += 1
                else:
                    stats["failed"] += 1
                
                # Add delay between downloads
                time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error during template downloads: {e}")
        finally:
            self.cleanup()
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Web driver closed successfully")
            except:
                pass
            self.driver = None
    
    def generate_download_report(self, templates: List[TemplateDownloadInfo], stats: Dict[str, int]) -> str:
        """Generate a download report"""
        report_lines = [
            "="*60,
            "📊 TEMPLATE DOWNLOAD REPORT",
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
        
        report_lines.extend([
            "="*60,
            "🎯 Download process completed!",
            "="*60
        ])
        
        return "\n".join(report_lines)

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description="Download Microsoft PowerPoint templates selected by AI")
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
    parser.add_argument(
        "--headless", 
        action="store_true", 
        default=True,
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="Timeout for web operations in seconds"
    )
    
    args = parser.parse_args()
    
    print("🚀 Microsoft Template Downloader")
    print("=" * 50)
    
    # Check dependencies
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available. Install with:")
        print("   pip install selenium webdriver-manager")
        return
    
    # Initialize downloader
    downloader = MicrosoftTemplateDownloader(
        output_dir=args.output_dir,
        headless=args.headless,
        timeout=args.timeout
    )
    
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
        report_file = Path(args.output_dir) / "download_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        downloader.cleanup()

if __name__ == "__main__":
    main() 