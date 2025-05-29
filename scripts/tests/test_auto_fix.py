#!/usr/bin/env python3
"""
Test script for Content Verification Auto-Fix functionality

This script demonstrates how the auto-fix feature works by:
1. Loading a presentation and JSON file
2. Running verification to find critical issues
3. Attempting to fix critical issues automatically
4. Re-verifying to show improvement

Usage:
    python3 test_auto_fix.py <presentation_path> <json_path>
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_verification import ContentVerifier, verify_presentation_content

def test_auto_fix(presentation_path: str, json_path: str):
    """Test the auto-fix functionality"""
    
    print("🔧 CONTENT VERIFICATION AUTO-FIX TEST")
    print("=" * 60)
    
    # Validate input files
    if not os.path.exists(presentation_path):
        print(f"❌ Presentation file not found: {presentation_path}")
        return False
        
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found: {json_path}")
        return False
    
    print(f"📄 Presentation: {os.path.basename(presentation_path)}")
    print(f"📋 JSON Source: {os.path.basename(json_path)}")
    print("=" * 60)
    
    # Step 1: Initial verification without auto-fix
    print("\n🔍 STEP 1: INITIAL VERIFICATION (no auto-fix)")
    print("-" * 50)
    
    initial_result = verify_presentation_content(
        presentation_path, json_path, 
        debug=True, auto_fix_critical=False
    )
    
    critical_issues = [m for m in initial_result.mismatches if m.severity == "critical"]
    warning_issues = [m for m in initial_result.mismatches if m.severity == "warning"]
    
    print(f"\n📊 Initial Status: {initial_result.overall_status.upper()}")
    print(f"   Success rate: {initial_result.success_rate:.1f}%")
    print(f"   Critical issues: {len(critical_issues)}")
    print(f"   Warning issues: {len(warning_issues)}")
    
    # Step 2: Auto-fix verification
    if critical_issues:
        print("\n🔧 STEP 2: AUTO-FIX VERIFICATION")
        print("-" * 50)
        print(f"Found {len(critical_issues)} critical issues - attempting auto-fix...")
        
        auto_fix_result = verify_presentation_content(
            presentation_path, json_path,
            debug=True, auto_fix_critical=True
        )
        
        print(f"\n📊 Post Auto-Fix Status: {auto_fix_result.overall_status.upper()}")
        
        if auto_fix_result.repair_results:
            successful_repairs = sum(1 for r in auto_fix_result.repair_results if r.repair_successful)
            total_repairs = len(auto_fix_result.repair_results)
            
            print(f"   Repair attempts: {total_repairs}")
            print(f"   Successful repairs: {successful_repairs}")
            
            if auto_fix_result.post_repair_success_rate is not None:
                improvement = auto_fix_result.post_repair_success_rate - initial_result.success_rate
                print(f"   Initial success rate: {initial_result.success_rate:.1f}%")
                print(f"   Post-repair success rate: {auto_fix_result.post_repair_success_rate:.1f}%")
                print(f"   Improvement: {improvement:+.1f}%")
                
                remaining_critical = sum(1 for m in (auto_fix_result.post_repair_mismatches or []) if m.severity == "critical")
                remaining_warnings = sum(1 for m in (auto_fix_result.post_repair_mismatches or []) if m.severity == "warning")
                
                print(f"   Remaining critical issues: {remaining_critical}")
                print(f"   Remaining warning issues: {remaining_warnings}")
        
        # Step 3: Summary and recommendations
        print("\n📈 STEP 3: SUMMARY & RECOMMENDATIONS")
        print("-" * 50)
        
        if auto_fix_result.post_repair_success_rate and auto_fix_result.post_repair_success_rate > initial_result.success_rate:
            print("✅ Auto-fix was successful!")
            print("   The presentation has been improved and critical issues were resolved.")
            
            if auto_fix_result.post_repair_success_rate >= 90:
                print("🎉 Excellent: Success rate is now 90% or higher")
            elif auto_fix_result.post_repair_success_rate >= 70:
                print("👍 Good: Success rate is now 70% or higher")
            else:
                print("⚠️  Fair: Some issues remain but critical ones were addressed")
                
        else:
            print("❌ Auto-fix had limited success")
            print("   Manual review and correction may be needed for remaining issues.")
        
        return True
        
    else:
        print("\n✅ No critical issues found - auto-fix not needed!")
        print("   The presentation content verification already passed.")
        return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 test_auto_fix.py <presentation_path> <json_path>")
        print("\nExample:")
        print("  python3 test_auto_fix.py output/presentation_template_1.pptx content/slide_details_updated_template_1.json")
        sys.exit(1)
    
    presentation_path = sys.argv[1]
    json_path = sys.argv[2]
    
    success = test_auto_fix(presentation_path, json_path)
    
    if success:
        print("\n🎯 Auto-fix test completed successfully!")
    else:
        print("\n❌ Auto-fix test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 