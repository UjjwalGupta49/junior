#!/usr/bin/env python3
"""
Debug script to test template loading functionality
"""

import sys
import os
import json
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from template_management.improved_template_downloader import ImprovedTemplateDownloader

def debug_template_loading():
    """Debug the template loading process"""
    print("🔍 DEBUG: Template Loading")
    print("=" * 50)
    
    selections_file = "./scrapers/content/dual_template_selections.json"
    
    print(f"1. Checking if file exists: {selections_file}")
    if os.path.exists(selections_file):
        print("   ✅ File exists")
        
        # Check file size
        file_size = os.path.getsize(selections_file)
        print(f"   📏 File size: {file_size} bytes")
        
        # Try to read raw content
        print("2. Reading raw file content...")
        try:
            with open(selections_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            print(f"   ✅ Raw content length: {len(raw_content)} characters")
            print(f"   📄 First 200 chars: {raw_content[:200]}...")
        except Exception as e:
            print(f"   ❌ Error reading raw content: {e}")
            return
        
        # Try to parse JSON
        print("3. Parsing JSON...")
        try:
            with open(selections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("   ✅ JSON parsing successful")
            print(f"   🔍 Data type: {type(data)}")
            print(f"   🔍 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if data is None:
                print("   ❌ Data is None!")
                return
            
            # Check selections
            selections = data.get('selections', [])
            print(f"   📋 Selections count: {len(selections)}")
            
            for i, selection in enumerate(selections, 1):
                print(f"   📄 Selection {i}:")
                if selection is None:
                    print("      ❌ Selection is None!")
                    continue
                
                template_details = selection.get('template_details', {})
                if template_details is None:
                    print("      ❌ template_details is None!")
                    continue
                
                template_id = template_details.get('id', '')
                template_title = template_details.get('title', 'Unknown Template')
                print(f"      🆔 ID: {template_id}")
                print(f"      📝 Title: {template_title}")
                
        except Exception as e:
            print(f"   ❌ Error parsing JSON: {e}")
            return
        
        # Try with downloader using EXACT same methodology as main.py
        print("4. Testing with ImprovedTemplateDownloader...")
        try:
            downloader = ImprovedTemplateDownloader(
                output_dir="./template",
                headless=True,
                timeout=45
            )
            
            # Add detailed debugging to exactly replicate what happens in load_template_selections
            print("   🔍 Debugging load_template_selections step by step...")
            
            # Step 1: Check file exists
            if not os.path.exists(selections_file):
                print("      ❌ Selections file not found")
                return
            print("      ✅ File exists check passed")
            
            # Step 2: Open and load JSON
            try:
                with open(selections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"      ✅ JSON loaded, type: {type(data)}")
            except Exception as e:
                print(f"      ❌ JSON load error: {e}")
                return
            
            # Step 3: Get selections array  
            templates = []
            selections_array = data.get('selections', [])
            print(f"      ✅ Got selections array with {len(selections_array)} items")
            
            # Step 4: Process each selection
            for idx, selection in enumerate(selections_array):
                print(f"      🔍 Processing selection {idx + 1}:")
                print(f"         Selection type: {type(selection)}")
                print(f"         Selection is None: {selection is None}")
                
                if selection is None:
                    print("         ❌ Selection is None, skipping")
                    continue
                
                # This is where the error occurs: selection.get('template_details', {})
                try:
                    template_details = selection.get('template_details', {})
                    print(f"         ✅ Got template_details, type: {type(template_details)}")
                    print(f"         template_details is None: {template_details is None}")
                except AttributeError as e:
                    print(f"         ❌ AttributeError getting template_details: {e}")
                    print(f"         selection content: {selection}")
                    continue
                except Exception as e:
                    print(f"         ❌ Other error getting template_details: {e}")
                    continue
                
                if template_details is None:
                    print("         ❌ template_details is None, skipping")
                    continue
                    
                try:
                    template_id = template_details.get('id', '')
                    template_title = template_details.get('title', 'Unknown Template')
                    print(f"         ✅ ID: {template_id}")
                    print(f"         ✅ Title: {template_title}")
                except Exception as e:
                    print(f"         ❌ Error getting ID/title: {e}")
                    continue
            
            # Now call the actual method
            templates = downloader.load_template_selections(selections_file)
            print(f"   ✅ Downloader loaded {len(templates)} templates")
            
            for i, template in enumerate(templates, 1):
                print(f"   📄 Template {i}: {template.template_title}")
                
        except Exception as e:
            print(f"   ❌ Error with downloader: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("   ❌ File does not exist")

if __name__ == "__main__":
    debug_template_loading() 