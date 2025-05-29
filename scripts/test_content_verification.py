#!/usr/bin/env python3
"""
Test script for content verification functionality.
Demonstrates how to use the content verification module independently.
"""

import os
import sys
import json
from pathlib import Path
from content_verification import verify_presentation_content, ContentVerifier

def test_verification_with_sample_data():
    """Test verification with sample data"""
    print("🧪 TESTING CONTENT VERIFICATION")
    print("=" * 50)
    
    # Check if we have sample files in the expected locations
    sample_presentation = "./output/presentation_template_1_sample.pptx"
    sample_json = "./content/slide_details_updated_template_1.json"
    
    if os.path.exists(sample_presentation) and os.path.exists(sample_json):
        print(f"📁 Found sample files:")
        print(f"   Presentation: {sample_presentation}")
        print(f"   JSON: {sample_json}")
        
        # Run verification
        result = verify_presentation_content(sample_presentation, sample_json, debug=True)
        
        # Display detailed results
        print(f"\n📊 DETAILED TEST RESULTS:")
        print(f"   Overall Status: {result.overall_status.upper()}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Slides Processed: {result.total_slides}")
        print(f"   Shapes Checked: {result.total_shapes_checked}")
        print(f"   Successful Matches: {result.successful_matches}")
        print(f"   Issues Found: {len(result.mismatches)}")
        
        if result.mismatches:
            print(f"\n🔍 ISSUE DETAILS:")
            for i, mismatch in enumerate(result.mismatches[:5], 1):
                print(f"   {i}. Slide {mismatch.slide_index + 1} - {mismatch.shape_name}")
                print(f"      Issue: {mismatch.description}")
                print(f"      Severity: {mismatch.severity}")
                print(f"      Type: {mismatch.issue_type}")
                if mismatch.intended_content:
                    print(f"      Intended: '{mismatch.intended_content[:50]}...'")
                if mismatch.actual_content:
                    print(f"      Actual: '{mismatch.actual_content[:50]}...'")
                print()
        
        return result.overall_status == "pass"
    else:
        print(f"❌ Sample files not found:")
        print(f"   Expected presentation: {sample_presentation}")
        print(f"   Expected JSON: {sample_json}")
        print(f"\n💡 To test verification:")
        print(f"   1. Run the main workflow first: python3 main.py")
        print(f"   2. Then run this test: python3 test_content_verification.py")
        return False

def create_mock_verification_test():
    """Create a mock test scenario for demonstration"""
    print("\n🎭 CREATING MOCK VERIFICATION TEST")
    print("-" * 40)
    
    # Create mock intended content
    mock_intended = [
        {
            "slide_index": 0,
            "slide_layout_name": "Title Slide",
            "shapes": [
                {
                    "name": "Title 1",
                    "placeholder_type": "TITLE",
                    "has_text_frame": True,
                    "text": "My Amazing Presentation",
                    "left_inches": 1.0,
                    "top_inches": 2.0
                },
                {
                    "name": "Subtitle 2",
                    "placeholder_type": "SUBTITLE",
                    "has_text_frame": True,
                    "text": "A comprehensive overview of our project",
                    "left_inches": 1.0,
                    "top_inches": 3.0
                }
            ]
        },
        {
            "slide_index": 1,
            "slide_layout_name": "Content Slide",
            "shapes": [
                {
                    "name": "Title 1",
                    "placeholder_type": "TITLE",
                    "has_text_frame": True,
                    "text": "Introduction",
                    "left_inches": 1.0,
                    "top_inches": 1.0
                },
                {
                    "name": "Content Placeholder 2",
                    "placeholder_type": "OBJECT",
                    "has_text_frame": True,
                    "text": "• Key point 1\n• Key point 2\n• Key point 3",
                    "left_inches": 1.0,
                    "top_inches": 2.5
                }
            ]
        }
    ]
    
    # Create mock actual content (with some issues for testing)
    mock_actual = [
        {
            "slide_index": 0,
            "slide_layout_name": "Title Slide",
            "shapes": [
                {
                    "name": "Title 1",
                    "placeholder_type": "TITLE",
                    "has_text_frame": True,
                    "text": "My Amazing Presentation",  # Perfect match
                    "left_inches": 1.0,
                    "top_inches": 2.0
                },
                {
                    "name": "Subtitle 2",
                    "placeholder_type": "SUBTITLE",
                    "has_text_frame": True,
                    "text": "Click to add subtitle",  # Default text issue
                    "left_inches": 1.0,
                    "top_inches": 3.0
                }
            ]
        },
        {
            "slide_index": 1,
            "slide_layout_name": "Content Slide",
            "shapes": [
                {
                    "name": "Title 1",
                    "placeholder_type": "TITLE",
                    "has_text_frame": True,
                    "text": "",  # Empty placeholder issue
                    "left_inches": 1.0,
                    "top_inches": 1.0
                },
                {
                    "name": "Content Placeholder 2",
                    "placeholder_type": "OBJECT",
                    "has_text_frame": True,
                    "text": "• Key point 1\n• Key point 2\n• Different point 3",  # Partial match
                    "left_inches": 1.0,
                    "top_inches": 2.5
                }
            ]
        }
    ]
    
    # Test the verification logic directly
    verifier = ContentVerifier(debug=True)
    mismatches = verifier._compare_content(mock_actual, mock_intended)
    
    print(f"🔍 Mock Test Results:")
    print(f"   Issues found: {len(mismatches)}")
    
    for mismatch in mismatches:
        print(f"   • {mismatch.issue_type}: {mismatch.description}")
    
    return len(mismatches) > 0  # Should find issues in our mock data

def main():
    """Main test function"""
    print("🔬 CONTENT VERIFICATION TEST SUITE")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Real file verification (if available)
    print("\n🧪 TEST 1: Real File Verification")
    if test_verification_with_sample_data():
        success_count += 1
        print("✅ Test 1 PASSED")
    else:
        print("⚠️  Test 1 SKIPPED (no sample files)")
    
    # Test 2: Mock verification logic
    print("\n🧪 TEST 2: Mock Verification Logic")
    if create_mock_verification_test():
        success_count += 1
        print("✅ Test 2 PASSED (issues detected as expected)")
    else:
        print("❌ Test 2 FAILED (should have detected issues)")
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Tests run: {total_tests}")
    print(f"   Tests passed: {success_count}")
    print(f"   Success rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed or were skipped")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 