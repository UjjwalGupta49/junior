#!/usr/bin/env python3
"""
Server-optimized test script for the Microsoft Templates Scraper
This script validates scraper functionality in server environments.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from template_scraper import MicrosoftTemplatesScraper, TemplateInfo

def test_scraper_basic(logger: logging.Logger, max_templates: int = 5):
    """Test basic scraper functionality with server optimizations"""
    logger.info("Testing Microsoft Templates Scraper...")
    
    # Initialize scraper for server environment
    scraper = MicrosoftTemplatesScraper(headless=True, log_level="INFO")
    
    try:
        # Test scraping a limited number of templates for faster testing
        logger.info("Starting template scraping test...")
        templates = scraper.scrape_all_templates(max_templates=max_templates)
        
        if templates:
            logger.info(f"Successfully scraped {len(templates)} templates")
            
            # Display first few templates
            logger.info("Sample Templates:")
            for i, template in enumerate(templates[:3]):
                logger.info(f"{i+1}. {template.title}")
                logger.info(f"   Category: {template.category}")
                logger.info(f"   Theme: {template.theme}")
                logger.info(f"   Features: {', '.join(template.features[:3])}")
                logger.info(f"   Use Cases: {', '.join(template.use_cases[:2])}")
            
            # Save test results
            output_path = "./content/test_templates.json"
            scraper.save_to_json(output_path)
            logger.info(f"Test results saved to {output_path}")
            
            return True
        else:
            logger.error("No templates were scraped")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False

def test_template_data_structure(logger: logging.Logger):
    """Test the template data structure and validation"""
    logger.info("Testing template data structure...")
    
    # Create a sample template for testing
    sample_template = TemplateInfo(
        id="test_template_001",
        title="Test Business Template",
        description="A sample template for testing purposes",
        category="Business",
        theme="Professional",
        features=["Charts", "Tables", "Infographics"],
        preview_url="https://example.com/preview.jpg",
        download_url="https://example.com/download.pptx",
        tags=["business", "professional", "modern"],
        color_scheme="Blue",
        layout_types=["Title Slide", "Content Slide"],
        difficulty_level="Intermediate",
        use_cases=["Business Presentation", "Meeting"]
    )
    
    # Test serialization
    try:
        template_dict = sample_template.__dict__
        json_str = json.dumps(template_dict, indent=2)
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        
        logger.info("Template data structure is valid")
        logger.info(f"Sample template: {sample_template.title}")
        logger.info(f"JSON serialization: Success")
        logger.info(f"Data fields: {len(template_dict)} fields")
        
        return True
        
    except Exception as e:
        logger.error(f"Template data structure test failed: {e}")
        return False

def test_json_database_format(logger: logging.Logger):
    """Test the JSON database format"""
    logger.info("Testing JSON database format...")
    
    # Check if test database exists
    test_db_path = "./content/test_templates.json"
    
    if not os.path.exists(test_db_path):
        logger.warning("Test database not found. Run test_scraper_basic() first.")
        return False
    
    try:
        with open(test_db_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Validate database structure
        required_keys = ["metadata", "templates"]
        if not all(key in database for key in required_keys):
            logger.error("Database missing required keys")
            return False
        
        metadata = database["metadata"]
        templates = database["templates"]
        
        logger.info("JSON database format is valid")
        logger.info(f"Total templates: {metadata.get('total_templates', 0)}")
        logger.info(f"Source: {metadata.get('source', 'Unknown')}")
        logger.info(f"Templates array length: {len(templates)}")
        
        # Validate first template structure
        if templates:
            first_template = templates[0]
            required_template_keys = [
                "id", "title", "description", "category", "theme",
                "features", "use_cases"
            ]
            
            missing_keys = [key for key in required_template_keys if key not in first_template]
            if missing_keys:
                logger.warning(f"Template missing keys: {missing_keys}")
            else:
                logger.info("Template structure is complete")
        
        return True
        
    except Exception as e:
        logger.error(f"JSON database test failed: {e}")
        return False

def demonstrate_scraper_usage():
    """Demonstrate how to use the scraper in practice"""
    print("\n🎯 Demonstrating scraper usage...")
    
    # Example 1: Basic usage
    print("\n1️⃣ Basic Scraper Usage:")
    print("""
    from template_scraper import MicrosoftTemplatesScraper
    
    # Initialize scraper
    scraper = MicrosoftTemplatesScraper(headless=True)
    
    # Scrape templates
    templates = scraper.scrape_all_templates()
    
    # Save to JSON
    scraper.save_to_json("./content/microsoft_templates.json")
    """)
    
    # Example 2: Custom configuration
    print("\n2️⃣ Custom Configuration:")
    print("""
    # Run with visible browser for debugging
    scraper = MicrosoftTemplatesScraper(headless=False)
    
    # Custom save location
    scraper.save_to_json("./custom/path/templates.json")
    """)
    
    # Example 3: Error handling
    print("\n3️⃣ Error Handling:")
    print("""
    try:
        scraper = MicrosoftTemplatesScraper()
        templates = scraper.scrape_all_templates()
        
        if templates:
            print(f"Success! Scraped {len(templates)} templates")
            scraper.save_to_json("./content/templates.json")
        else:
            print("No templates found")
            
    except Exception as e:
        print(f"Scraping failed: {e}")
    """)

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging for server environment"""
    logger = logging.getLogger("template_scraper_test")
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

def run_all_tests(max_templates: int = 5, log_level: str = "INFO"):
    """Run all tests with server-optimized settings"""
    logger = setup_logging(log_level)
    
    logger.info("Running Template Scraper Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("Data Structure Test", lambda: test_template_data_structure(logger)),
        ("Basic Scraper Test", lambda: test_scraper_basic(logger, max_templates)),
        ("JSON Database Test", lambda: test_json_database_format(logger)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"{test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! Scraper is ready for server deployment.")
        return 0  # Success exit code
    else:
        logger.warning("Some tests failed. Check the output above for details.")
        return 1  # Error exit code

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Server-optimized Template Scraper Test Suite')
    parser.add_argument('--max-templates', type=int, default=5,
                       help='Maximum number of templates to test (default: 5)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Ensure content directory exists
    Path("./content").mkdir(parents=True, exist_ok=True)
    
    # Run test suite with server optimizations
    exit_code = run_all_tests(
        max_templates=args.max_templates,
        log_level=args.log_level
    )
    
    logger = setup_logging(args.log_level)
    logger.info("=" * 50)
    logger.info("Next Steps for Server Deployment:")
    logger.info("1. Run 'python template_scraper.py --headless --max-templates 100'")
    logger.info("2. Run 'python main.py' to use the enhanced workflow")
    logger.info("3. Check './content/microsoft_templates.json' for results")
    logger.info("4. Monitor logs for any server-side issues")
    logger.info("=" * 50)
    
    sys.exit(exit_code) 