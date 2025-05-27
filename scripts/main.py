import os
import shutil
import json
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

def process_single_template(template_path: str, template_index: int, user_content: str) -> bool:
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

def run_template_processing_workflow(user_content: str) -> Dict[str, bool]:
    """
    Step 3: Process all downloaded templates through the complete workflow
    
    Args:
        user_content: User's presentation content
        
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
        
        success = process_single_template(template_path, i, user_content)
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
    
    print(f"\n🎯 WORKFLOW STATUS: {'SUCCESS' if successful_templates > 0 else 'FAILED'}")

# --- Main Workflow Execution ---
def main():
    """Main workflow execution"""
    print("🚀 JUNIORAI COMPLETE PRESENTATION WORKFLOW")
    print("=" * 80)
    print("Workflow: AI Template Selection → Download → Process Both Templates")
    print(f"Working directory: {os.getcwd()}")
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
        template_results = run_template_processing_workflow(user_content)
        
        if template_results:
            overall_success = any(template_results.values())
        
    except Exception as e:
        print(f"❌ Unexpected error in main workflow: {e}")
    
    finally:
        # Always clean up and show summary
        cleanup_intermediate_files()
        
        if template_results:
            display_final_summary(template_results)
        
        if overall_success:
            print("\n🎉 JuniorAI workflow completed successfully!")
        else:
            print("\n😞 JuniorAI workflow failed to complete successfully.")

if __name__ == "__main__":
    main() 