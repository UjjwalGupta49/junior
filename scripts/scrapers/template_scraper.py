import json
import time
import requests
import logging
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class TemplateInfo:
    """Data structure for PowerPoint template information"""
    id: str
    title: str
    description: str
    category: str
    theme: str
    features: List[str]
    preview_url: str
    download_url: Optional[str]
    tags: List[str]
    color_scheme: str
    layout_types: List[str]
    difficulty_level: str
    use_cases: List[str]

class MicrosoftTemplatesScraper:
    """Server-side scraper for Microsoft Create PowerPoint templates"""
    
    def __init__(self, headless: bool = True, log_level: str = "INFO"):
        self.base_url = "https://create.microsoft.com/en-us/search?filters=powerpoint"
        self.templates = []
        self.driver = None
        self.wait = None
        self.logger = self._setup_logging(log_level)
        self.setup_driver(headless)
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging for server environment"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create console handler if not already exists
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def setup_driver(self, headless: bool):
        """Setup Chrome WebDriver with server-optimized options"""
        try:
            chrome_options = Options()
            
            # Server-side optimizations
            if headless:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            # Security and stability options for server environments
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--disable-javascript")  # We don't need JS for basic scraping
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # User agent for better compatibility
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
            self.driver.set_page_load_timeout(30)  # 30 second timeout
            self.wait = WebDriverWait(self.driver, 15)  # Increased timeout for server
            
            self.logger.info("Chrome WebDriver initialized successfully")
            
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during WebDriver setup: {e}")
            raise
    
    def scrape_all_templates(self, max_templates: int = None) -> List[TemplateInfo]:
        """Main method to scrape PowerPoint templates with server-side optimizations"""
        try:
            self.logger.info("Starting Microsoft PowerPoint templates scraping...")
            
            # Navigate to the page with retry logic
            self._navigate_with_retry(self.base_url, max_retries=3)
            
            # Wait for page to load with better error handling
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
                self.logger.info("Template cards loaded successfully")
            except TimeoutException:
                self.logger.warning("Template cards not found, trying alternative selectors...")
                # Try alternative selectors
                alternative_selectors = [
                    "a[href*='template']",
                    "div[class*='item']",
                    "div[data-testid='template-card']",
                    ".template-item",
                    "[class*='template']",
                    ".card"
                ]
                
                for selector in alternative_selectors:
                    try:
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        self.logger.info(f"Found templates using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                else:
                    raise Exception("No template elements found with any selector")
            
            # Load all templates with rate limiting
            self._load_all_templates_with_rate_limiting()
            
            # Get initial count of templates
            initial_elements = self._get_template_elements()
            total_found = len(initial_elements)
            self.logger.info(f"Found {total_found} template cards")
            
            # Determine how many to process
            templates_to_process = min(max_templates, total_found) if max_templates else total_found
            self.logger.info(f"Will process {templates_to_process} templates")
            
            # Process templates with dynamic element finding to avoid stale references
            for i in range(templates_to_process):
                try:
                    self.logger.debug(f"Processing template {i+1}/{templates_to_process}")
                    
                    # Re-find elements each time to avoid stale references
                    current_elements = self._get_template_elements()
                    if i >= len(current_elements):
                        self.logger.warning(f"Template {i+1} not found in current elements")
                        continue
                    
                    element = current_elements[i]
                    template_info = self._extract_template_info_safe(element, i)
                    
                    if template_info:
                        self.templates.append(template_info)
                        self.logger.info(f"✅ Extracted template {i+1}/{templates_to_process}: {template_info.title}")
                        
                        # Progress logging for server monitoring
                        if (i + 1) % 5 == 0:
                            self.logger.info(f"📊 Progress: {i+1}/{templates_to_process} processed, {len(self.templates)} successful")
                    else:
                        self.logger.warning(f"❌ Failed to extract template {i+1}/{templates_to_process}")
                            
                except Exception as e:
                    self.logger.error(f"💥 Critical error extracting template {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully scraped {len(self.templates)} templates")
            return self.templates
            
        except Exception as e:
            self.logger.error(f"Critical error during scraping: {e}")
            return []
        finally:
            self._cleanup_driver()
    
    def _navigate_with_retry(self, url: str, max_retries: int = 3):
        """Navigate to URL with retry logic for server stability"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                self.logger.info(f"Successfully navigated to {url}")
                return
            except Exception as e:
                self.logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _get_template_elements(self) -> list:
        """Get template elements with fallback selectors"""
        selectors = [
            "a[href*='/template/']",   # Primary: direct template links
            "div[class*='TemplateThumbnailCard_container']",  # Secondary: actual template cards
            "div[role='listitem']",  # Tertiary: wrapper elements
            "div[class*='item']",    # Fallback for item wrappers
            "template-card",         # Original selectors as fallback
            "div[data-testid='template-card']",
            ".template-item",
            "[class*='template']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith('.') or selector.startswith('[') or selector.startswith('div') or selector.startswith('a'):
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                else:
                    elements = self.driver.find_elements(By.CLASS_NAME, selector)
                
                if elements:
                    self.logger.info(f"Found {len(elements)} elements using selector: {selector}")
                    return elements
            except Exception as e:
                self.logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        return []
    
    def _cleanup_driver(self):
        """Safely cleanup WebDriver resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during WebDriver cleanup: {e}")
    
    def _load_all_templates_with_rate_limiting(self):
        """Scroll and load all templates with server-friendly rate limiting"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        
        self.logger.info("Starting template loading with pagination...")
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll to bottom with smooth scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Server-friendly delay
            time.sleep(3)  # Increased delay for server stability
            
            # Try to click "Load More" button if present
            load_more_clicked = self._try_load_more_button()
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height and not load_more_clicked:
                self.logger.info("No more content to load")
                break
                
            if new_height > last_height:
                self.logger.debug(f"Page height increased from {last_height} to {new_height}")
                
            last_height = new_height
            scroll_attempts += 1
            
            # Progress logging
            if scroll_attempts % 10 == 0:
                self.logger.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")
        
        if scroll_attempts >= max_scroll_attempts:
            self.logger.warning(f"Reached maximum scroll attempts ({max_scroll_attempts})")
    
    def _try_load_more_button(self) -> bool:
        """Try to click load more button with multiple selectors"""
        load_more_selectors = [
            "//button[contains(text(), 'Load more')]",
            "//button[contains(text(), 'Show more')]",
            "//button[contains(text(), 'See more')]",
            "//a[contains(text(), 'Load more')]",
            "//div[contains(@class, 'load-more')]//button",
            "[data-testid='load-more']",
            ".load-more-button"
        ]
        
        for selector in load_more_selectors:
            try:
                if selector.startswith('//'):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed() and element.is_enabled():
                    self.driver.execute_script("arguments[0].click();", element)
                    self.logger.debug(f"Clicked load more button using selector: {selector}")
                    time.sleep(4)  # Wait for content to load
                    return True
                    
            except (NoSuchElementException, Exception):
                continue
        
        return False
    
    def _extract_template_info_safe(self, element, index: int) -> Optional[TemplateInfo]:
        """Extract template info with enhanced error handling for server environments"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return self._extract_template_info(element, index)
            except Exception as e:
                self.logger.warning(f"Template extraction attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to extract template {index} after {max_retries} attempts")
                    return None
                time.sleep(1)  # Brief delay before retry
        
        return None
    
    def _extract_template_info(self, element, index: int) -> Optional[TemplateInfo]:
        """Extract detailed information from a template card element"""
        try:
            # Extract basic information from the element
            template_link = None
            title = "Untitled Template"
            preview_url = ""
            
            # Check if the element itself is a template link
            if element.tag_name == 'a':
                href = element.get_attribute("href")
                if href and '/template/' in href:
                    template_link = href
                    # Extract title from URL
                    title = href.split('/')[-1].replace('-', ' ').title()
                    
                    # Try to find preview image in parent or nearby elements
                    try:
                        # Look for image in parent container
                        parent = element.find_element(By.XPATH, "..")
                        img_element = parent.find_element(By.CSS_SELECTOR, "img")
                        preview_url = img_element.get_attribute("src") or ""
                    except:
                        try:
                            # Look for image within the link itself
                            img_element = element.find_element(By.CSS_SELECTOR, "img")
                            preview_url = img_element.get_attribute("src") or ""
                        except:
                            preview_url = ""
            else:
                # If element is not a direct link, try to find template link within it
                try:
                    link_selectors = [
                        "a[href*='/template/']",
                        "a[href*='template']", 
                        "a",  # Any link within the element
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, selector)
                            href = link_element.get_attribute("href")
                            if href and ('/template/' in href or 'template' in href):
                                template_link = href
                                break
                        except:
                            continue
                    
                    # Extract title from the element or nearby elements
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h3, h2, [class*='title'], [class*='name']")
                        title = title_element.text.strip() or "Untitled Template"
                    except:
                        if template_link:
                            title = template_link.split('/')[-1].replace('-', ' ').title()
                    
                    # Extract preview image
                    try:
                        img_element = element.find_element(By.CSS_SELECTOR, "img")
                        preview_url = img_element.get_attribute("src") or ""
                    except:
                        preview_url = ""
                        
                except:
                    self.logger.warning(f"Could not find template link in element {index}")
                    return None
            
            # If we have a template link, try to get detailed information
            if template_link:
                template_id = template_link.split('/')[-1] if template_link else f"ms_template_{index:03d}"
                
                # Try to visit template detail page for detailed information
                detailed_info_extracted = False
                detailed_title = title
                description = ""
                category = "PowerPoint"
                theme = "Modern"
                features = ["Customizable Template", "Professional Design"]
                tags = ["powerpoint", "template"]
                download_url = None
                color_scheme = "Professional"
                layout_types = ["Title Slide", "Content Slide"]
                
                try:
                    self.logger.debug(f"Visiting template detail page: {template_link}")
                    self.driver.get(template_link)
                    time.sleep(3)
                    
                    # Extract detailed information from template page
                    detailed_title = self._safe_extract_text(By.CSS_SELECTOR, "h1, [class*='title']", title)
                    description = self._extract_detailed_description()
                    
                    # Extract other information
                    category = self._extract_category_from_page()
                    theme = self._extract_theme_from_page()
                    features = self._extract_features_from_page()
                    tags = self._extract_tags_from_page()
                    download_url = self._extract_download_url_from_page()
                    
                    # Extract design characteristics
                    color_scheme = self._extract_color_scheme_from_page()
                    layout_types = self._extract_layout_types_from_page()
                    
                    detailed_info_extracted = True
                    self.logger.debug(f"Successfully extracted detailed info for: {detailed_title}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract detailed info for template {index}, using basic info: {e}")
                
                finally:
                    # Always try to go back to main page
                    try:
                        self.driver.back()
                        time.sleep(1)
                    except:
                        # If back fails, navigate to main page
                        try:
                            self.driver.get(self.base_url)
                            time.sleep(2)
                        except:
                            pass
                
                # Create template info with available data
                difficulty_level = self._determine_difficulty_level(features)
                use_cases = self._extract_use_cases(description, tags)
                
                template_info = TemplateInfo(
                    id=template_id,
                    title=detailed_title,
                    description=description,
                    category=category,
                    theme=theme,
                    features=features,
                    preview_url=preview_url,
                    download_url=download_url,
                    tags=tags,
                    color_scheme=color_scheme,
                    layout_types=layout_types,
                    difficulty_level=difficulty_level,
                    use_cases=use_cases
                )
                
                self.logger.debug(f"Created template info for: {template_info.title} (detailed: {detailed_info_extracted})")
                return template_info
            else:
                self.logger.warning(f"No template link found for element {index}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting template info for element {index}: {e}")
            return None
    
    def _safe_extract_text(self, by: By, selector: str, default: str = "") -> str:
        """Safely extract text from an element"""
        try:
            element = self.wait.until(EC.presence_of_element_located((by, selector)))
            return element.text.strip()
        except (TimeoutException, NoSuchElementException):
            return default
    
    def _extract_detailed_description(self) -> str:
        """Extract the detailed description from template detail page"""
        try:
            # Multiple selectors to find the description text
            description_selectors = [
                # Look for paragraphs that contain template description keywords
                "//p[contains(text(), 'template') and contains(text(), 'presentation')]",
                "//p[contains(text(), 'Create') and contains(text(), 'template')]",
                "//p[contains(text(), 'slide') and string-length(text()) > 50]",
                # Look for description in common locations
                "//div[contains(@class, 'description')]//p",
                "//div[contains(@class, 'content')]//p[string-length(text()) > 50]",
                "//section//p[string-length(text()) > 50]",
                # Look for the main content paragraph
                "//main//p[string-length(text()) > 50]",
                # Generic paragraph with substantial text
                "//p[string-length(text()) > 100]"
            ]
            
            for selector in description_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        text = element.text.strip()
                        # Filter out unwanted text (navigation, headers, etc.)
                        if (len(text) > 50 and 
                            'template' in text.lower() and 
                            'presentation' in text.lower() and
                            not text.lower().startswith('home') and
                            not text.lower().startswith('powerpoint') and
                            not 'sign in' in text.lower() and
                            not 'create' == text.lower()):
                            
                            self.logger.debug(f"Found description: {text[:100]}...")
                            return text
                except Exception as e:
                    self.logger.debug(f"Description selector failed: {selector} - {e}")
                    continue
            
            # Fallback: look for any substantial paragraph text
            try:
                paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
                for p in paragraphs:
                    text = p.text.strip()
                    if (len(text) > 80 and 
                        ('template' in text.lower() or 'presentation' in text.lower()) and
                        not text.lower().startswith('home') and
                        not 'sign in' in text.lower()):
                        self.logger.debug(f"Fallback description found: {text[:100]}...")
                        return text
            except Exception as e:
                self.logger.debug(f"Fallback description extraction failed: {e}")
            
            # If no description found, return empty string
            self.logger.warning("No detailed description found on template page")
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed description: {e}")
            return ""
    
    def _extract_category_from_page(self) -> str:
        """Extract template category from detail page"""
        try:
            # Look for breadcrumb navigation
            breadcrumb = self._safe_extract_text(By.CSS_SELECTOR, "nav, [class*='breadcrumb']", "")
            if breadcrumb:
                if "powerpoint" in breadcrumb.lower():
                    return "PowerPoint"
                elif "business" in breadcrumb.lower():
                    return "Business"
                elif "education" in breadcrumb.lower():
                    return "Education"
            
            # Fallback to analyzing page content
            categories = ["Business", "Education", "Personal", "Creative", "Professional", "Marketing"]
            page_text = self.driver.page_source.lower()
            for category in categories:
                if category.lower() in page_text:
                    return category
            return "PowerPoint"
        except:
            return "PowerPoint"
    
    def _extract_theme_from_page(self) -> str:
        """Extract template theme/style from detail page"""
        try:
            # Look for theme in title or description
            title = self._safe_extract_text(By.CSS_SELECTOR, "h1", "").lower()
            description = self._safe_extract_text(By.CSS_SELECTOR, "p", "").lower()
            
            themes = ["modern", "classic", "minimalist", "creative", "professional", "colorful", "dark", "light"]
            
            # Check title first
            for theme in themes:
                if theme in title:
                    return theme.title()
            
            # Check description
            for theme in themes:
                if theme in description:
                    return theme.title()
            
            # Analyze page content
            page_text = self.driver.page_source.lower()
            for theme in themes:
                if theme in page_text:
                    return theme.title()
            
            return "Modern"
        except:
            return "Modern"
    
    def _extract_features_from_page(self) -> List[str]:
        """Extract template features from detail page"""
        features = []
        
        try:
            # Look for features in bullet points or lists
            feature_elements = self.driver.find_elements(By.CSS_SELECTOR, "li, [class*='feature']")
            for element in feature_elements:
                text = element.text.strip()
                if text and len(text) < 100:  # Reasonable feature length
                    features.append(text)
            
            # If no specific features found, look for common PowerPoint features
            if not features:
                feature_keywords = [
                    "customizable", "animations", "transitions", "charts", "graphs", "tables", 
                    "images", "icons", "infographics", "timeline", "agenda",
                    "title slide", "content slides", "professional"
                ]
                
                page_text = self.driver.page_source.lower()
                for keyword in feature_keywords:
                    if keyword in page_text:
                        features.append(keyword.title())
            
            return features[:5] if features else ["Customizable Template", "Professional Design"]
        except:
            return ["Customizable Template", "Professional Design"]
    
    def _extract_tags_from_page(self) -> List[str]:
        """Extract template tags from detail page"""
        try:
            # Look for tags in various locations
            tag_selectors = ["[class*='tag']", "[class*='keyword']", "[class*='category']"]
            tags = []
            
            for selector in tag_selectors:
                tag_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in tag_elements:
                    text = element.text.strip()
                    if text and len(text) < 50:
                        tags.append(text)
            
            # Extract tags from title and description
            title = self._safe_extract_text(By.CSS_SELECTOR, "h1", "").lower()
            if "business" in title:
                tags.append("business")
            if "modern" in title:
                tags.append("modern")
            if "professional" in title:
                tags.append("professional")
            
            return list(set(tags))[:5] if tags else ["powerpoint", "template"]
        except:
            return ["powerpoint", "template"]
    
    def _extract_preview_url(self) -> str:
        """Extract preview image URL"""
        try:
            preview_img = self.driver.find_element(By.CLASS_NAME, "template-preview-image")
            return preview_img.get_attribute("src") or ""
        except Exception:
            return ""
    
    def _extract_download_url_from_page(self) -> Optional[str]:
        """Extract download URL from template detail page"""
        try:
            # Look for download or customize buttons
            download_selectors = [
                "//a[contains(text(), 'Download')]",
                "//button[contains(text(), 'Download')]",
                "//a[contains(text(), 'Customize')]",
                "//button[contains(text(), 'Customize')]",
                "//a[contains(@href, 'download')]"
            ]
            
            for selector in download_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    href = element.get_attribute("href")
                    if href:
                        return href
                except:
                    continue
            
            return None
        except:
            return None
    
    def _extract_color_scheme_from_page(self) -> str:
        """Analyze and extract color scheme from template detail page"""
        try:
            # Look for color information in title or description
            title = self._safe_extract_text(By.CSS_SELECTOR, "h1", "").lower()
            description = self._safe_extract_text(By.CSS_SELECTOR, "p", "").lower()
            
            color_keywords = {
                "blue": "Blue",
                "red": "Red", 
                "green": "Green",
                "purple": "Purple",
                "orange": "Orange",
                "yellow": "Yellow",
                "black": "Dark",
                "white": "Light",
                "gray": "Neutral",
                "grey": "Neutral"
            }
            
            # Check title first
            for keyword, color in color_keywords.items():
                if keyword in title:
                    return color
            
            # Check description
            for keyword, color in color_keywords.items():
                if keyword in description:
                    return color
            
            return "Professional"
        except:
            return "Professional"
    
    def _extract_layout_types_from_page(self) -> List[str]:
        """Extract types of layouts available from template detail page"""
        try:
            layout_types = ["Title Slide", "Content Slide", "Two Column", "Image with Text", "Chart Slide", "Timeline", "Agenda"]
            
            # Look for layout indicators in the template description
            page_text = self.driver.page_source.lower()
            found_layouts = []
            
            for layout in layout_types:
                if layout.lower() in page_text:
                    found_layouts.append(layout)
            
            # Add common PowerPoint layouts
            if not found_layouts:
                found_layouts = ["Title Slide", "Content Slide", "Image with Text"]
            
            return found_layouts[:4]  # Limit to 4 layout types
        except:
            return ["Title Slide", "Content Slide"]
    
    def _determine_difficulty_level(self, features: List[str]) -> str:
        """Determine template complexity/difficulty level based on features"""
        if len(features) > 5:
            return "Advanced"
        elif len(features) > 2:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _extract_use_cases(self, description: str, tags: List[str]) -> List[str]:
        """Extract potential use cases for the template"""
        use_case_keywords = {
            "presentation": ["Business Presentation", "Meeting"],
            "pitch": ["Pitch Deck", "Investor Presentation"],
            "training": ["Training Material", "Workshop"],
            "report": ["Report", "Analysis"],
            "proposal": ["Proposal", "Project Plan"],
            "education": ["Educational Content", "Lesson"],
            "marketing": ["Marketing Presentation", "Sales"]
        }
        
        use_cases = []
        text_to_analyze = (description + " " + " ".join(tags)).lower()
        
        for keyword, cases in use_case_keywords.items():
            if keyword in text_to_analyze:
                use_cases.extend(cases)
        
        return list(set(use_cases)) if use_cases else ["General Presentation"]
    
    def save_to_json(self, filename: str = "microsoft_templates.json"):
        """Save scraped templates to JSON file"""
        templates_dict = [asdict(template) for template in self.templates]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_templates": len(templates_dict),
                    "source": "Microsoft Create PowerPoint Templates",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "url": self.base_url
                },
                "templates": templates_dict
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(templates_dict)} templates to {filename}")

def main():
    """Main function optimized for server execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Microsoft Templates Scraper for Server')
    parser.add_argument('--headless', action='store_true', default=True, 
                       help='Run in headless mode (default: True)')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level')
    parser.add_argument('--max-templates', type=int, default=None,
                       help='Maximum number of templates to scrape (for testing)')
    parser.add_argument('--output', default='./content/microsoft_templates.json',
                       help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize scraper with server-optimized settings
    scraper = MicrosoftTemplatesScraper(
        headless=args.headless, 
        log_level=args.log_level
    )
    
    try:
        templates = scraper.scrape_all_templates(max_templates=args.max_templates)
        
        if templates:
            scraper.save_to_json(args.output)
            scraper.logger.info(f"Scraping completed successfully! Found {len(templates)} templates.")
            return 0  # Success exit code
        else:
            scraper.logger.error("No templates were scraped.")
            return 1  # Error exit code
            
    except KeyboardInterrupt:
        scraper.logger.info("Scraping interrupted by user")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        scraper.logger.error(f"Scraping failed with error: {e}")
        return 1  # Error exit code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 