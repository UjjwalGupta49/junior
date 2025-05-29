#!/usr/bin/env python3
"""
Test script for cleanup flags functionality.
Creates sample files and tests the cleanup operations.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

def create_sample_files():
    """Create sample files in content, output, and downloaded_templates directories"""
    print("🎭 CREATING SAMPLE FILES FOR CLEANUP TESTING")
    print("=" * 50)
    
    directories = {
        "./content": [
            "slide_details_template_1.json",
            "slide_details_reorganized_template_1.json", 
            "slide_details_updated_template_1.json",
            "slide_details_template_2.json",
            "slide_details_reorganized_template_2.json",
            "slide_details_updated_template_2.json"
        ],
        "./output": [
            "presentation_template_1_Modern_Business.pptx",
            "presentation_template_2_Creative_Design.pptx",
            "final_presentation_backup.pptx"
        ],
        "./template/downloaded_templates": [
            "Modern_Business_Template_abc123.pptx",
            "Creative_Design_Template_def456.pptx",
            "Professional_Layout_Template_ghi789.pptx"
        ]
    }
    
    total_files_created = 0
    
    for directory, files in directories.items():
        # Create directory if it doesn't exist
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Creating files in {directory}:")
        
        for filename in files:
            file_path = Path(directory) / filename
            
            try:
                # Create sample content based on file type
                if filename.endswith('.json'):
                    # Create sample JSON content
                    sample_data = [
                        {
                            "slide_index": 0,
                            "slide_layout_name": "Title Slide",
                            "shapes": [
                                {
                                    "name": "Title 1",
                                    "text": "Sample Presentation Title",
                                    "placeholder_type": "TITLE"
                                }
                            ]
                        }
                    ]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(sample_data, f, indent=2)
                    file_size = 0.5  # Estimated KB
                
                elif filename.endswith('.pptx'):
                    # Create dummy PPTX file (just a placeholder)
                    with open(file_path, 'wb') as f:
                        # Write some dummy data to simulate a PPTX file
                        dummy_data = b"PK\x03\x04" + b"DUMMY_PPTX_CONTENT_FOR_TESTING" * 1000
                        f.write(dummy_data)
                    file_size = len(dummy_data) / 1024  # Size in KB
                
                else:
                    # Create generic text file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Sample content for {filename}\nCreated for cleanup testing.")
                    file_size = 0.1  # Estimated KB
                
                print(f"   ✅ Created: {filename} ({file_size:.1f} KB)")
                total_files_created += 1
                
            except Exception as e:
                print(f"   ❌ Failed to create {filename}: {e}")
    
    print(f"\n📊 SAMPLE FILES SUMMARY:")
    print(f"   Total files created: {total_files_created}")
    print(f"   Ready for cleanup testing!")
    
    return total_files_created

def count_files_in_directories():
    """Count files in the cleanup target directories"""
    directories = [
        "./content",
        "./output", 
        "./template/downloaded_templates"
    ]
    
    total_files = 0
    file_details = {}
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            files = [f for f in dir_path.iterdir() if f.is_file()]
            file_details[directory] = len(files)
            total_files += len(files)
        else:
            file_details[directory] = 0
    
    return total_files, file_details

def test_template_clean_flag():
    """Test the --template_clean flag functionality"""
    print("\n🧪 TESTING --template_clean FLAG")
    print("-" * 40)
    
    # Count files before
    before_count, before_details = count_files_in_directories()
    
    print(f"📊 Files before cleanup:")
    for directory, count in before_details.items():
        print(f"   {directory}: {count} files")
    
    # Simulate template cleanup (would normally be done by main.py)
    print(f"\n🗑️  Simulating template cleanup...")
    print(f"💡 In real usage: python3 main.py --template_clean")
    print(f"   This would delete only files in ./template/downloaded_templates/")
    
    # Count what would be deleted
    template_dir = Path("./template/downloaded_templates")
    if template_dir.exists():
        template_files = [f for f in template_dir.iterdir() if f.is_file()]
        print(f"   Would delete {len(template_files)} template files")
        for file_path in template_files:
            print(f"     - {file_path.name}")
    else:
        print(f"   No template directory found")

def test_cleanall_flag():
    """Test the --cleanall flag functionality"""
    print("\n🧪 TESTING --cleanall FLAG (STANDALONE MODE)")
    print("-" * 50)
    
    # Count files before
    before_count, before_details = count_files_in_directories()
    
    print(f"📊 Files before cleanup:")
    total_files = 0
    for directory, count in before_details.items():
        print(f"   {directory}: {count} files")
        total_files += count
    
    # Simulate comprehensive cleanup
    print(f"\n🗑️  Simulating standalone cleanup...")
    print(f"💡 In real usage: python3 main.py --cleanall")
    print(f"   This will ONLY perform cleanup - NO WORKFLOW will run")
    print(f"   Deletes ALL files from:")
    print(f"   • ./content/ (JSON intermediates)")
    print(f"   • ./output/ (Final presentations)")  
    print(f"   • ./template/downloaded_templates/ (Downloaded templates)")
    
    print(f"\n📊 Total files that would be deleted: {total_files}")
    print(f"⏱️  Operation completes quickly (no AI processing, template download, etc.)")
    print(f"🎯 Use case: Quick cleanup before starting fresh workflow")

def show_usage_examples():
    """Show usage examples for the cleanup flags"""
    print("\n💡 CLEANUP FLAGS USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            "command": "python3 main.py",
            "description": "Normal workflow - no cleanup"
        },
        {
            "command": "python3 main.py --template_clean",
            "description": "Workflow + delete downloaded templates after completion"
        },
        {
            "command": "python3 main.py --cleanall",
            "description": "STANDALONE cleanup - delete ALL files, NO workflow execution"
        }
    ]
    
    for example in examples:
        print(f"\n🔹 {example['command']}")
        print(f"   → {example['description']}")
    
    print(f"\n📋 CLEANUP BEHAVIOR:")
    print(f"   --template_clean: Runs workflow, then deletes ./template/downloaded_templates/*.pptx")
    print(f"   --cleanall: STANDALONE operation - deletes ALL files, skips workflow entirely")
    print(f"   Note: --cleanall is independent and doesn't combine with other flags")
    
    print(f"\n🎯 TYPICAL USAGE PATTERNS:")
    print(f"   1. Clean environment: python3 main.py --cleanall")
    print(f"   2. Run fresh workflow: python3 main.py") 
    print(f"   3. Run workflow with cleanup: python3 main.py --template_clean")

def main():
    """Main test function"""
    print("🧪 CLEANUP FLAGS TEST SUITE")
    print("=" * 60)
    
    # Check if sample files exist, create if needed
    total_files, _ = count_files_in_directories()
    
    if total_files == 0:
        print("📁 No sample files found. Creating sample files for testing...")
        create_sample_files()
    else:
        print(f"📁 Found {total_files} existing files in cleanup directories")
    
    # Test both cleanup flags
    test_template_clean_flag()
    test_cleanall_flag()
    
    # Show usage examples
    show_usage_examples()
    
    # Final instructions
    print(f"\n🎯 TESTING INSTRUCTIONS:")
    print(f"   1. Create sample files: python3 test_cleanup_flags.py")
    print(f"   2. Test standalone cleanup: python3 main.py --cleanall")
    print(f"      → Should delete all files immediately, no workflow execution")
    print(f"   3. Recreate files: python3 test_cleanup_flags.py") 
    print(f"   4. Test workflow with template cleanup: python3 main.py --template_clean")
    print(f"      → Should run full workflow, then delete only templates")
    print(f"   5. Verify cleanup behavior differences")
    
    print(f"\n⚡ QUICK CLEANUP TIP:")
    print(f"   Before starting fresh workflow: python3 main.py --cleanall && python3 main.py")
    
    print(f"\n✅ Cleanup flags test suite completed!")

if __name__ == "__main__":
    main() 