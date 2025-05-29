import os
import shutil
import json
import argparse
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()

# Import all the required modules for the complete workflow
from extract_slide_details import extract_slide_details
from intelligent_slide_organizer import intelligent_slide_organization_step
from create_presentation_from_reorganized_json import create_and_update_reorganized_presentation
from template_management import select_dual_templates, TemplateMatch, ImprovedTemplateDownloader
from content_verification import verify_presentation_content

# --- Configuration: File Paths ---
# Updated paths to match the actual codebase structure
TEMPLATES_DATABASE_JSON = "./scrapers/content/microsoft_templates.json"  # Microsoft templates database
DUAL_TEMPLATE_SELECTIONS_JSON = "./scrapers/content/dual_template_selections.json"  # AI-selected templates
DOWNLOADED_TEMPLATES_DIR = "./template/downloaded_templates"  # Where downloaded templates are stored
CONTENT_DIR = "./content"  # Directory for intermediate JSON files
OUTPUT_DIR = "./output"  # Directory for final presentations
USER_CONTENT_FILE = "./user/user_content.txt"  # User content input file

# --- Gemini AI Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-05-20")

# Validate that required environment variables are set
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file.")

def ensure_directories_exist():
    """Ensure all required directories exist"""
    directories = [CONTENT_DIR, OUTPUT_DIR, DOWNLOADED_TEMPLATES_DIR]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def load_user_content() -> str:
    """Load user content from file"""
    try:
        if os.path.exists(USER_CONTENT_FILE):
            with open(USER_CONTENT_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            print(f"📝 Loaded user content ({len(content)} characters)")
            return content
        else:
            print(f"❌ User content file not found: {USER_CONTENT_FILE}")
            return ""
    except Exception as e:
        print(f"❌ Error loading user content: {e}")
        return ""

def run_dual_template_selection(user_content: str) -> List[TemplateMatch]:
    """
    Step 1: Select two best templates using AI analysis
    
    Args:
        user_content: User's presentation content
        
    Returns:
        List of selected TemplateMatch objects
    """
    print("=" * 80)
    print("🎯 STEP 1: DUAL TEMPLATE SELECTION")
    print("=" * 80)
    
    try:
        # Run dual template selection
        matches = select_dual_templates(
            user_content=user_content,
            templates_db_path=TEMPLATES_DATABASE_JSON,
            user_requirements="",
            api_key=GOOGLE_API_KEY,
            model_name=MODEL_NAME,
            verbose=True,
            save_results=True
        )
        
        if matches and len(matches) >= 2:
            print(f"✅ Successfully selected {len(matches)} templates:")
            for i, match in enumerate(matches, 1):
                print(f"   {i}. {match.template_title} (confidence: {match.confidence_score:.1%})")
            return matches
        else:
            print(f"❌ Template selection failed or insufficient templates found")
            return []
            
    except Exception as e:
        print(f"❌ Error during template selection: {e}")
        return []

def run_template_download(selections_file: str) -> bool:
    """
    Step 2: Download selected templates using headless Chrome
    
    Args:
        selections_file: Path to the template selections JSON file
        
    Returns:
        True if download was successful
    """
    print("=" * 80)
    print("🔽 STEP 2: TEMPLATE DOWNLOAD")
    print("=" * 80)
    
    try:
        # Initialize headless Chrome downloader (server-optimized)
        downloader = ImprovedTemplateDownloader(
            output_dir="./template",
            headless=True,  # Server-side headless mode
            timeout=45
        )
        
        # Load templates from selections
        templates = downloader.load_template_selections(selections_file)
        
        if not templates:
            print("❌ No templates found in selections file")
            return False
        
        print(f"📋 Found {len(templates)} templates to download:")
        for i, template in enumerate(templates, 1):
            print(f"   {i}. {template.template_title}")
        
        # Download templates
        stats = downloader.download_templates(templates)
        
        # Generate report
        report = downloader.generate_download_report(templates, stats)
        print("\n" + report)
        
        success = stats["completed"] > 0
        if success:
            print(f"✅ Successfully downloaded {stats['completed']}/{stats['total']} templates")
        else:
            print(f"❌ Failed to download templates")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during template download: {e}")
        return False

def get_downloaded_template_paths() -> List[str]:
    """Get paths to all downloaded template files"""
    try:
        template_dir = Path(DOWNLOADED_TEMPLATES_DIR)
        if not template_dir.exists():
            return []
        
        template_files = list(template_dir.glob("*.pptx"))
        template_paths = [str(f) for f in template_files]
        
        print(f"📁 Found {len(template_paths)} downloaded templates:")
        for i, path in enumerate(template_paths, 1):
            filename = os.path.basename(path)
            print(f"   {i}. {filename}")
        
        return template_paths
        
    except Exception as e:
        print(f"❌ Error getting template paths: {e}")
        return []

def process_single_template(template_path: str, template_index: int, user_content: str, auto_fix: bool) -> bool:
    """
    Process a single template through the complete workflow:
    - Extract slide details
    - Reorganize slides
    - Add content
    - Create final presentation
    
    Args:
        template_path: Path to the template file
        template_index: Index of the template (1 or 2)
        user_content: User's presentation content
        auto_fix: Whether to automatically fix critical content issues
        
    Returns:
        True if processing was successful
    """
    template_name = os.path.splitext(os.path.basename(template_path))[0]
    
    print(f"\n📋 PROCESSING TEMPLATE {template_index}: {template_name}")
    print("-" * 60)
    
    # Define file paths for this template
    slide_details_json = f"{CONTENT_DIR}/slide_details_template_{template_index}.json"
    reorganized_json = f"{CONTENT_DIR}/slide_details_reorganized_template_{template_index}.json"
    updated_json = f"{CONTENT_DIR}/slide_details_updated_template_{template_index}.json"
    final_output = f"{OUTPUT_DIR}/presentation_template_{template_index}_{template_name}.pptx"
    
    try:
        # Step 3.1: Extract slide details
        print(f"🔍 Step 3.{template_index}.1: Extracting slide details...")
        details = extract_slide_details(template_path)
        
        if not details:
            print(f"❌ Failed to extract details from template {template_index}")
            return False
        
        with open(slide_details_json, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=4)
        print(f"✅ Extracted {len(details)} slides to {slide_details_json}")
        
        # Step 3.2: Reorganize slides based on user content
        print(f"🔄 Step 3.{template_index}.2: Reorganizing slides...")
        reorganize_success = intelligent_slide_organization_step(
            slide_details_json, 
            reorganized_json, 
            user_content, 
            GOOGLE_API_KEY, 
            MODEL_NAME
        )
        
        if not reorganize_success:
            print(f"❌ Failed to reorganize slides for template {template_index}")
            return False
        
        print(f"✅ Slides reorganized and saved to {reorganized_json}")
        
        # Step 3.3: Add content to slides using AI
        print(f"✨ Step 3.{template_index}.3: Adding content with AI...")
        content_success = modify_json_content_with_ai(reorganized_json, updated_json, user_content)
        
        if not content_success:
            print(f"❌ Failed to add content for template {template_index}")
            return False
        
        print(f"✅ Content added and saved to {updated_json}")
        
        # Step 3.4: Create final presentation
        print(f"🎯 Step 3.{template_index}.4: Creating final presentation...")
        presentation_success = create_and_update_reorganized_presentation(
            template_path, 
            updated_json, 
            final_output
        )
        
        if presentation_success:
            print(f"✅ Final presentation created: {final_output}")
            
            # Step 3.5: Verify content was correctly applied
            print(f"🔍 Step 3.{template_index}.5: Verifying content application...")
            verification_result = verify_presentation_content(final_output, updated_json, debug=False, auto_fix_critical=auto_fix)
            
            if verification_result.overall_status == "pass":
                print(f"✅ Content verification passed ({verification_result.success_rate:.1f}% success rate)")
                
                # Show auto-fix summary if it was used
                if auto_fix and verification_result.repair_results:
                    successful_repairs = sum(1 for r in verification_result.repair_results if r.repair_successful)
                    total_critical = len(verification_result.repair_results)
                    if successful_repairs > 0:
                        improvement = (verification_result.post_repair_success_rate or verification_result.success_rate) - verification_result.success_rate
                        print(f"🔧 Auto-fix: {successful_repairs}/{total_critical} critical issues resolved (+{improvement:.1f}%)")
                
                return True
            elif verification_result.overall_status == "warning":
                print(f"⚠️  Content verification passed with warnings ({verification_result.success_rate:.1f}% success rate)")
                print(f"   Found {len(verification_result.mismatches)} minor issues")
                
                # Show auto-fix summary if it was used
                if auto_fix and verification_result.repair_results:
                    successful_repairs = sum(1 for r in verification_result.repair_results if r.repair_successful)
                    total_critical = len(verification_result.repair_results)
                    if successful_repairs > 0:
                        improvement = (verification_result.post_repair_success_rate or verification_result.success_rate) - verification_result.success_rate
                        print(f"🔧 Auto-fix: {successful_repairs}/{total_critical} critical issues resolved (+{improvement:.1f}%)")
                
                return True  # Still consider successful but with warnings
            else:
                print(f"❌ Content verification failed ({verification_result.success_rate:.1f}% success rate)")
                print(f"   Found {len(verification_result.mismatches)} critical issues")
                critical_issues = sum(1 for m in verification_result.mismatches if m.severity == "critical")
                print(f"   Critical issues: {critical_issues}")
                
                # Show auto-fix summary if it was used  
                if auto_fix and verification_result.repair_results:
                    successful_repairs = sum(1 for r in verification_result.repair_results if r.repair_successful)
                    total_critical = len(verification_result.repair_results)
                    if successful_repairs > 0:
                        improvement = (verification_result.post_repair_success_rate or verification_result.success_rate) - verification_result.success_rate
                        print(f"🔧 Auto-fix attempted: {successful_repairs}/{total_critical} critical issues resolved (+{improvement:.1f}%)")
                        remaining_critical = sum(1 for m in (verification_result.post_repair_mismatches or []) if m.severity == "critical")
                        print(f"   Remaining critical issues: {remaining_critical}")
                    else:
                        print(f"🔧 Auto-fix attempted but failed to resolve critical issues")
                
                # Still return True as presentation was created, but user is warned about content issues
                return True
        else:
            print(f"❌ Failed to create final presentation for template {template_index}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing template {template_index}: {e}")
        return False

def modify_json_content_with_ai(input_json_path: str, output_json_path: str, user_content: str) -> bool:
    """
    Modify JSON content using Gemini AI to add relevant content
    
    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to save modified JSON
        user_content: User's presentation content
        
    Returns:
        True if successful
    """
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        original_json_string = json.dumps(original_data, indent=2)

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = f"""
I want to update the existing content of the slides in the JSON file to create a presentation.
I want to create a presentation about this content: {user_content}

The text you add should be relevant to the content, theme, tone and style of the presentation.
Keep the text concise and to the point, avoid writing long paragraphs and prefer concise bullet points using \\n to create new lines.
The JSON data represents a list of slides, and each slide contains shapes with text.
Your task is to make creative and relevant modifications to the text content in the provided JSON as per the requirements of the presentation.

Here is the JSON data:
```json
{original_json_string}
```

Return the ENTIRE JSON data with your modifications. 
Ensure your output is ONLY the modified JSON data, valid and parsable, starting with `[` and ending with `]`.
Do not include any markdown in the text you write, just the JSON data with text content. Avoid the the usage of **bold** or *italic* or any other markdown formatting for text content.
Do not include any explanatory text or markdown formatting like ```json before or after the JSON output.
"""
        
        response = model.generate_content(prompt)
        
        # Clean the response: remove potential markdown code block fences
        modified_json_string = response.text.strip()
        if modified_json_string.startswith("```json"):
            modified_json_string = modified_json_string[7:]
        if modified_json_string.startswith("```"):
            modified_json_string = modified_json_string[3:]
        if modified_json_string.endswith("```"):
            modified_json_string = modified_json_string[:-3]
        
        modified_data = json.loads(modified_json_string.strip())

        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=4)
        
        return True

    except Exception as e:
        print(f"❌ Error during AI content modification: {e}")
        return False

def run_template_processing_workflow(user_content: str, auto_fix: bool) -> Dict[str, bool]:
    """
    Step 3: Process all downloaded templates through the complete workflow
    
    Args:
        user_content: User's presentation content
        auto_fix: Whether to automatically fix critical content issues
        
    Returns:
        Dictionary with processing results for each template
    """
    print("=" * 80)
    print("⚙️  STEP 3: TEMPLATE PROCESSING WORKFLOW")
    print("=" * 80)
    
    # Get downloaded template paths
    template_paths = get_downloaded_template_paths()
    
    if not template_paths:
        print("❌ No downloaded templates found")
        return {}
    
    results = {}
    
    # Process each template
    for i, template_path in enumerate(template_paths, 1):
        template_name = os.path.basename(template_path)
        print(f"\n🔄 Processing template {i}/{len(template_paths)}: {template_name}")
        
        success = process_single_template(template_path, i, user_content, auto_fix)
        results[template_name] = success
        
        if success:
            print(f"✅ Template {i} processed successfully")
        else:
            print(f"❌ Template {i} processing failed")
    
    return results

def cleanup_intermediate_files():
    """Clean up intermediate files and cache"""
    print("\n🧹 CLEANUP")
    print("-" * 30)
    
    try:
        # Clean up __pycache__ directories
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pycache_path = os.path.join(script_dir, "__pycache__")
        
        if os.path.exists(pycache_path):
            shutil.rmtree(pycache_path)
            print(f"✅ Removed {pycache_path}")
        
        # Clean up any additional cache directories
        current_dir = os.getcwd()
        current_pycache = os.path.join(current_dir, "__pycache__")
        
        if os.path.exists(current_pycache) and current_pycache != pycache_path:
            shutil.rmtree(current_pycache)
            print(f"✅ Removed {current_pycache}")
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def cleanup_downloaded_templates():
    """Clean up downloaded template files"""
    print("\n🗑️  TEMPLATE CLEANUP")
    print("-" * 30)
    
    try:
        template_dir = Path(DOWNLOADED_TEMPLATES_DIR)
        if not template_dir.exists():
            print(f"📁 Template directory does not exist: {DOWNLOADED_TEMPLATES_DIR}")
            return
        
        # Find all .pptx files in the downloaded templates directory
        pptx_files = list(template_dir.glob("*.pptx"))
        
        if not pptx_files:
            print(f"📁 No .pptx files found in {DOWNLOADED_TEMPLATES_DIR}")
            return
        
        print(f"🔍 Found {len(pptx_files)} template files to delete:")
        
        # Delete each .pptx file
        deleted_count = 0
        for pptx_file in pptx_files:
            try:
                file_size = pptx_file.stat().st_size / (1024 * 1024)  # Size in MB
                pptx_file.unlink()  # Delete the file
                deleted_count += 1
                print(f"   ✅ Deleted: {pptx_file.name} ({file_size:.1f} MB)")
            except Exception as e:
                print(f"   ❌ Failed to delete {pptx_file.name}: {e}")
        
        print(f"🗑️  Template cleanup completed: {deleted_count}/{len(pptx_files)} files deleted")
        
        # Calculate space freed (estimate)
        if deleted_count > 0:
            print(f"💾 Freed up storage space from downloaded templates")
        
    except Exception as e:
        print(f"❌ Error during template cleanup: {e}")

def cleanup_all_generated_files():
    """Clean up ALL generated files from content, output, and downloaded_templates directories"""
    print("\n🗑️  COMPREHENSIVE CLEANUP (ALL GENERATED FILES)")
    print("-" * 50)
    
    total_deleted = 0
    total_size_freed = 0.0
    
    directories_to_clean = [
        (CONTENT_DIR, "Content files (JSON intermediates)"),
        (OUTPUT_DIR, "Output files (Final presentations)"),
        (DOWNLOADED_TEMPLATES_DIR, "Downloaded templates")
    ]
    
    for directory, description in directories_to_clean:
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                print(f"📁 {description}: Directory does not exist - {directory}")
                continue
            
            # Get all files in the directory
            all_files = [f for f in dir_path.iterdir() if f.is_file()]
            
            if not all_files:
                print(f"📁 {description}: No files to delete - {directory}")
                continue
            
            print(f"\n🔍 {description} ({len(all_files)} files):")
            
            deleted_count = 0
            dir_size_freed = 0.0
            
            for file_path in all_files:
                try:
                    # Get file size before deletion
                    file_size = file_path.stat().st_size / (1024 * 1024)  # Size in MB
                    
                    # Delete the file
                    file_path.unlink()
                    deleted_count += 1
                    dir_size_freed += file_size
                    
                    # Show file type for better clarity
                    file_type = file_path.suffix.upper() if file_path.suffix else "NO EXT"
                    print(f"   ✅ Deleted: {file_path.name} ({file_type}, {file_size:.2f} MB)")
                    
                except Exception as e:
                    print(f"   ❌ Failed to delete {file_path.name}: {e}")
            
            print(f"   📊 {description}: {deleted_count}/{len(all_files)} files deleted ({dir_size_freed:.2f} MB freed)")
            total_deleted += deleted_count
            total_size_freed += dir_size_freed
            
        except Exception as e:
            print(f"❌ Error cleaning {description}: {e}")
    
    # Summary
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"   Total files deleted: {total_deleted}")
    print(f"   Total space freed: {total_size_freed:.2f} MB")
    
    if total_deleted > 0:
        print("✅ Comprehensive cleanup completed successfully!")
        print("💾 All generated files have been removed")
        print("🔄 Ready for fresh workflow execution")
    else:
        print("📁 No files were found to delete")
    
    return total_deleted

def display_final_summary(template_results: Dict[str, bool]):
    """Display final workflow summary"""
    print("\n" + "=" * 80)
    print("🎉 WORKFLOW COMPLETED")
    print("=" * 80)
    
    total_templates = len(template_results)
    successful_templates = sum(1 for success in template_results.values() if success)
    
    print(f"📊 SUMMARY:")
    print(f"   Total templates processed: {total_templates}")
    print(f"   Successful: {successful_templates}")
    print(f"   Failed: {total_templates - successful_templates}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for template_name, success in template_results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {status}: {template_name}")
    
    if successful_templates > 0:
        print(f"\n📁 OUTPUT LOCATION:")
        print(f"   Final presentations saved in: {OUTPUT_DIR}/")
        
        # List generated files
        output_path = Path(OUTPUT_DIR)
        if output_path.exists():
            output_files = list(output_path.glob("presentation_template_*.pptx"))
            for file_path in output_files:
                print(f"   - {file_path.name}")
        
        print(f"\n🔍 CONTENT VERIFICATION:")
        print(f"   All generated presentations underwent content verification")
        print(f"   Each presentation was checked for:")
        print(f"   • Empty placeholders")
        print(f"   • Default template text")
        print(f"   • Content accuracy vs. intended content")
        print(f"   • Successful content application rates")
    
    print(f"\n🎯 WORKFLOW STATUS: {'SUCCESS' if successful_templates > 0 else 'FAILED'}")

# --- Main Workflow Execution ---
def main():
    """Main workflow execution"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="JuniorAI - AI-Powered Presentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py                           # Run normal workflow
  python3 main.py --template_clean          # Run workflow and clean up downloaded templates
  python3 main.py --auto-fix-critical       # Run workflow with auto-fix for critical content issues
  python3 main.py --auto-fix-critical --template_clean  # Run workflow with auto-fix and cleanup
  python3 main.py --cleanall                # ONLY clean up ALL generated files (no workflow)
        """
    )
    
    parser.add_argument(
        "--template_clean", 
        action="store_true", 
        help="Delete downloaded template files after workflow completion"
    )
    
    parser.add_argument(
        "--auto-fix-critical",
        action="store_true",
        help="Automatically attempt to fix critical content verification issues"
    )
    
    parser.add_argument(
        "--cleanall",
        action="store_true",
        help="Delete ALL generated files (content/, output/, downloaded_templates/) - NO WORKFLOW EXECUTION"
    )
    
    args = parser.parse_args()
    
    # Handle --cleanall as standalone operation (no workflow execution)
    if args.cleanall:
        print("🗑️  JUNIORAI CLEANUP ONLY MODE")
        print("=" * 80)
        print("Performing comprehensive cleanup of all generated files...")
        print("No workflow will be executed.")
        print("=" * 80)
        
        # Perform comprehensive cleanup
        cleanup_intermediate_files()
        total_deleted = cleanup_all_generated_files()
        
        # Summary for cleanup-only mode
        print("\n" + "=" * 80)
        print("🗑️  CLEANUP COMPLETED")
        print("=" * 80)
        
        if total_deleted > 0:
            print("✅ All generated files have been successfully removed!")
            print("🔄 Environment is now clean and ready for fresh workflow execution")
        else:
            print("📁 No generated files were found to delete")
            print("💡 Environment was already clean")
        
        print("\n🎯 CLEANUP STATUS: SUCCESS")
        return  # Exit without running workflow
    
    # Normal workflow execution (when --cleanall is not provided)
    print("🚀 JUNIORAI COMPLETE PRESENTATION WORKFLOW")
    print("=" * 80)
    print("Workflow: AI Template Selection → Download → Process Both Templates → Verify Content")
    print(f"Working directory: {os.getcwd()}")
    if args.template_clean:
        print("🗑️  Template cleanup: ENABLED (will delete downloaded templates after workflow)")
    if args.auto_fix_critical:
        print("🔧 Auto-fix: ENABLED (will automatically repair critical content issues)")
    print("=" * 80)
    
    overall_success = False
    template_results = {}
    
    try:
        # Ensure required directories exist
        ensure_directories_exist()
        
        # Load user content
        user_content = load_user_content()
        if not user_content:
            print("❌ No user content available. Workflow cannot proceed.")
            return
        
        print(f"📝 User content preview: {user_content[:100]}{'...' if len(user_content) > 100 else ''}")
        
        # Step 1: Select two best templates using AI
        template_matches = run_dual_template_selection(user_content)
        if not template_matches:
            print("❌ Template selection failed. Workflow aborted.")
            return
        
        # Step 2: Download selected templates
        download_success = run_template_download(DUAL_TEMPLATE_SELECTIONS_JSON)
        if not download_success:
            print("❌ Template download failed. Workflow aborted.")
            return
        
        # Step 3: Process both templates through complete workflow
        template_results = run_template_processing_workflow(user_content, args.auto_fix_critical)
        
        if template_results:
            overall_success = any(template_results.values())
        
    except Exception as e:
        print(f"❌ Unexpected error in main workflow: {e}")
    
    finally:
        # Always clean up and show summary (only for workflow execution)
        cleanup_intermediate_files()
        
        # Clean up downloaded templates if requested (only when workflow was executed)
        if args.template_clean:
            cleanup_downloaded_templates()
        
        if template_results:
            display_final_summary(template_results)
        
        if overall_success:
            print("\n🎉 JuniorAI workflow completed successfully!")
        else:
            print("\n😞 JuniorAI workflow failed to complete successfully.")

if __name__ == "__main__":
    main() 