#!/usr/bin/env python3
"""
Improved Microsoft Template Downloader
====================================

This script downloads PowerPoint templates from Microsoft Create using Selenium
to properly navigate the website and handle downloads.

Requirements:
    - selenium
    - webdriver-manager
    - ChromeDriver (automatically managed)

Usage:
    python improved_template_downloader.py
    python improved_template_downloader.py --selections-file custom_selections.json
"""

import json
import os
import time
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
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TemplateDownloadInfo:
    """Information about a template to download"""
    template_id: str
    template_title: str
    template_url: str
    local_filename: str
    download_status: str = "pending"  # pending, downloading, completed, failed

class ImprovedTemplateDownloader:
    """
    Improved template downloader using Selenium to navigate Microsoft Create
    and properly handle template downloads.
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
        logger.info(f"Downloads will be saved to: {self.downloads_dir}")
    
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with download preferences"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Cannot setup web driver.")
            return False
        
        try:
            chrome_options = Options()
            
            # Server-side optimizations
            if self.headless:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            # Configure download preferences
            download_prefs = {
                "download.default_directory": str(self.downloads_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", download_prefs)
            
            # Security and stability options for server environments
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # User agent for better compatibility (Linux server UA)
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Memory and performance optimizations
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            
            # Use webdriver-manager for automatic driver management
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info(f"Chrome WebDriver setup completed successfully (headless: {self.headless})")
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
                    # Create template URL
                    template_url = f"{self.base_url}{template_id}"
                    
                    # Create safe filename
                    safe_title = "".join(c for c in template_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    filename = f"{safe_title}_{template_id[:8]}.pptx"
                    
                    template_info = TemplateDownloadInfo(
                        template_id=template_id,
                        template_title=template_title,
                        template_url=template_url,
                        local_filename=filename
                    )
                    templates.append(template_info)
            
            logger.info(f"Loaded {len(templates)} templates for download")
            return templates
            
        except Exception as e:
            logger.error(f"Error loading template selections: {e}")
            return []
    
    def navigate_to_template(self, template_info: TemplateDownloadInfo) -> bool:
        """Navigate to template page and wait for it to load"""
        try:
            logger.info(f"Navigating to: {template_info.template_url}")
            self.driver.get(template_info.template_url)
            
            # Wait for page to load and check if it's a valid template page
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for dynamic content to load
            time.sleep(3)
            
            # Check if we're on a valid template page
            page_title = self.driver.title.lower()
            if "template" not in page_title and template_info.template_title.lower() not in page_title:
                logger.warning(f"May not be on correct template page. Title: {self.driver.title}")
            
            return True
            
        except TimeoutException:
            logger.error(f"Timeout loading template page: {template_info.template_url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to template: {e}")
            return False
    
    def find_and_click_download(self, template_info: TemplateDownloadInfo) -> bool:
        """Find and click the download button or link"""
        try:
            # Common selectors for download buttons/links on Microsoft Create
            download_selectors = [
                # Direct download buttons
                "button[aria-label*='Download']",
                "a[aria-label*='Download']", 
                "button[title*='Download']",
                "a[title*='Download']",
                "button:contains('Download')",
                "a:contains('Download')",
                
                # PowerPoint specific buttons
                "button[aria-label*='PowerPoint']",
                "a[aria-label*='PowerPoint']",
                "button[title*='PowerPoint']",
                "a[title*='PowerPoint']",
                
                # Customize buttons (which might lead to download)
                "button[aria-label*='Customize']",
                "a[aria-label*='Customize']",
                "button:contains('Customize')",
                "a:contains('Customize')",
                
                # Generic download classes
                ".download-button",
                ".btn-download",
                ".download-link",
                "[data-action='download']",
                "[data-testid*='download']"
            ]
            
            download_clicked = False
            
            for selector in download_selectors:
                try:
                    # Try CSS selector first
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Scroll to element and click
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            
                            try:
                                element.click()
                                logger.info(f"Successfully clicked download element: {selector}")
                                download_clicked = True
                                break
                            except:
                                # Try JavaScript click if regular click fails
                                self.driver.execute_script("arguments[0].click();", element)
                                logger.info(f"Successfully clicked download element via JavaScript: {selector}")
                                download_clicked = True
                                break
                    
                    if download_clicked:
                        break
                        
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no specific download button found, try text-based search
            if not download_clicked:
                try:
                    # Look for elements containing download-related text
                    download_texts = ["Download", "Get template", "Use template", "Open in PowerPoint"]
                    
                    for text in download_texts:
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                try:
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    element.click()
                                    logger.info(f"Successfully clicked element with text: {text}")
                                    download_clicked = True
                                    break
                                except:
                                    continue
                        if download_clicked:
                            break
                            
                except Exception as e:
                    logger.debug(f"Text-based search failed: {e}")
            
            if download_clicked:
                # Wait for download to potentially start
                time.sleep(5)
                template_info.download_status = "downloading"
                return True
            else:
                logger.warning(f"Could not find download button for template: {template_info.template_title}")
                template_info.download_status = "failed"
                return False
                
        except Exception as e:
            logger.error(f"Error finding/clicking download button: {e}")
            template_info.download_status = "failed"
            return False
    
    def wait_for_download_completion(self, template_info: TemplateDownloadInfo, max_wait: int = 120) -> bool:
        """Wait for download to complete and verify the file"""
        logger.info(f"Waiting for download completion: {template_info.template_title}")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            # Check for downloaded files
            download_files = list(self.downloads_dir.glob("*.pptx"))
            temp_files = list(self.downloads_dir.glob("*.crdownload")) + list(self.downloads_dir.glob("*.tmp"))
            
            # If we have .pptx files and no temporary files, download might be complete
            if download_files and not temp_files:
                # Find the most recent file
                latest_file = max(download_files, key=lambda f: f.stat().st_mtime)
                
                # Check if it's a valid PowerPoint file (not HTML)
                try:
                    with open(latest_file, 'rb') as f:
                        header = f.read(8)
                        # Check for ZIP signature (PowerPoint files are ZIP archives)
                        if header.startswith(b'PK\x03\x04') or header.startswith(b'PK\x05\x06'):
                            # Rename to our desired filename
                            target_path = self.downloads_dir / template_info.local_filename
                            
                            if target_path.exists():
                                target_path.unlink()  # Remove existing file
                            
                            latest_file.rename(target_path)
                            template_info.download_status = "completed"
                            logger.info(f"Download completed: {target_path}")
                            return True
                        else:
                            # File is not a valid PowerPoint file (probably HTML)
                            logger.warning(f"Downloaded file is not a valid PowerPoint file: {latest_file}")
                            latest_file.unlink()  # Remove invalid file
                            
                except Exception as e:
                    logger.error(f"Error verifying downloaded file: {e}")
            
            time.sleep(2)
        
        logger.warning(f"Download timeout for template: {template_info.template_title}")
        template_info.download_status = "failed"
        return False
    
    def download_template(self, template_info: TemplateDownloadInfo) -> bool:
        """Download a single template"""
        logger.info(f"Downloading template: {template_info.template_title}")
        
        # Check if file already exists
        target_file = self.downloads_dir / template_info.local_filename
        if target_file.exists():
            logger.info(f"Template already exists, skipping: {target_file}")
            template_info.download_status = "completed"
            return True
        
        # Navigate to template page
        if not self.navigate_to_template(template_info):
            return False
        
        # Find and click download button
        if not self.find_and_click_download(template_info):
            return False
        
        # Wait for download to complete
        if self.wait_for_download_completion(template_info):
            return True
        else:
            # If download failed, try alternative approach
            logger.info(f"Trying alternative download approach for: {template_info.template_title}")
            return self.try_alternative_download(template_info)
    
    def try_alternative_download(self, template_info: TemplateDownloadInfo) -> bool:
        """Try alternative download methods"""
        try:
            # Look for "Customize in PowerPoint" or similar buttons
            customize_selectors = [
                "a[href*='powerpoint']",
                "button[aria-label*='Customize in PowerPoint']",
                "a[aria-label*='Customize in PowerPoint']",
                "a:contains('Customize in PowerPoint')",
                "button:contains('Customize in PowerPoint')"
            ]
            
            for selector in customize_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            href = element.get_attribute('href')
                            if href and ('powerpoint' in href.lower() or 'office' in href.lower()):
                                logger.info(f"Found PowerPoint link: {href}")
                                # This might trigger a download or open PowerPoint
                                element.click()
                                time.sleep(5)
                                
                                # Check if download started
                                if self.wait_for_download_completion(template_info, max_wait=30):
                                    return True
                except Exception as e:
                    logger.debug(f"Alternative method failed: {e}")
                    continue
            
            template_info.download_status = "failed"
            return False
            
        except Exception as e:
            logger.error(f"Alternative download failed: {e}")
            template_info.download_status = "failed"
            return False
    
    def download_templates(self, templates: List[TemplateDownloadInfo]) -> Dict[str, int]:
        """Download all selected templates"""
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
                
                if self.download_template(template_info):
                    stats["completed"] += 1
                else:
                    stats["failed"] += 1
                
                # Add delay between downloads
                time.sleep(3)
            
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
            "📊 IMPROVED TEMPLATE DOWNLOAD REPORT",
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
            report_lines.append(f"   URL: {template_info.template_url}")
            report_lines.append(f"   Status: {template_info.download_status}")
            if template_info.download_status == "completed":
                report_lines.append(f"   File: {template_info.local_filename}")
            report_lines.append("")
        
        if stats['failed'] > 0:
            report_lines.extend([
                "🔧 MANUAL DOWNLOAD INSTRUCTIONS FOR FAILED TEMPLATES:",
                "-"*50,
                "For templates that failed to download automatically, you can:",
                "1. Visit the template URL in your browser",
                "2. Look for 'Download' or 'Customize in PowerPoint' buttons",
                "3. Save the file with the specified filename",
                "4. Place the file in the downloads directory",
                ""
            ])
        
        report_lines.extend([
            "="*60,
            "🎯 Download process completed!",
            "="*60
        ])
        
        return "\n".join(report_lines)

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description="Improved Microsoft PowerPoint template downloader")
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
        help="Run browser in headless mode (default: True for server operation)"
    )
    parser.add_argument(
        "--show-browser", 
        action="store_true",
        help="Show browser window (disable headless mode for debugging)"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="Timeout for web operations in seconds"
    )
    
    args = parser.parse_args()
    
    print("🚀 Improved Microsoft Template Downloader")
    print("=" * 50)
    
    # Check dependencies
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available. Install with:")
        print("   pip install selenium webdriver-manager")
        return
    
    # Determine headless mode (default True unless --show-browser is specified)
    headless_mode = not args.show_browser if hasattr(args, 'show_browser') else args.headless
    
    # Initialize downloader
    downloader = ImprovedTemplateDownloader(
        output_dir=args.output_dir,
        headless=headless_mode,
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
        print("\n🔄 Starting improved download process...")
        stats = downloader.download_templates(templates)
        
        # Generate and display report
        report = downloader.generate_download_report(templates, stats)
        print("\n" + report)
        
        # Save report to file
        report_file = Path(args.output_dir) / "improved_download_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        downloader.cleanup()

if __name__ == "__main__":
    main() 