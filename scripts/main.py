import os
import shutil
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Assuming extract_slide_details.py and update_presentation_from_json.py are in the same directory
# and can be imported directly by Python's module search path.
# If they are in a subdirectory or need specific path manipulation, adjust sys.path if necessary, 
# but for sibling files, direct import should work if the CWD is this directory.
from extract_slide_details import extract_slide_details
from update_presentation_from_json import update_presentation_from_json

# --- Configuration: File Paths ---
# All paths are relative to the script's location (learning/template/)
ORIGINAL_TEMPLATE_PPTX = "./template/template.pptx" # The master template
SLIDE_DETAILS_JSON = "./content/slide_details.json" # Intermediate JSON with extracted details
USER_UPDATED_JSON_CONTENT = "./content/slide_details_updated.json" # JSON after user (or placeholder) updates
FINAL_UPDATED_PPTX = "./output/template_updated.pptx" # Final presentation with content updates

# --- Gemini AI Configuration ---
# Load API key and model configuration from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-05-20")  # Default fallback

# Validate that required environment variables are set
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your .env file.")

# --- 1. Extract Slide Details ---
def run_extraction_step(input_pptx_path, output_json_path):
    """Extracts details from the presentation and saves them to a JSON file."""
    print(f"--- Step 1: Extracting slide details from '{input_pptx_path}' ---")
    details = extract_slide_details(input_pptx_path)
    if details:
        try:
            with open(output_json_path, 'w') as f:
                json.dump(details, f, indent=4)
            print(f"Successfully extracted details to '{output_json_path}'")
            return True
        except IOError as e:
            print(f"Error writing JSON to '{output_json_path}': {e}")
            return False
    else:
        print(f"Failed to extract details from '{input_pptx_path}'.")
        return False

# --- 2. Placeholder for Updating JSON Content ---
def placeholder_modify_json_content(original_json_path, updated_json_path, user_content):
    """
    Modifies JSON content using Gemini AI.
    Loads content from original_json_path, sends it to Gemini AI for modification,
    and saves the result to updated_json_path.
    """
    print(f"--- Step 2: Modifying JSON content using Gemini AI ---")
    try:
        with open(original_json_path, 'r') as f_orig:
            original_data = json.load(f_orig)
        
        original_json_string = json.dumps(original_data, indent=2)

        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = f"""
I want to udpate the existing content of the slides in the JSON file to create a presentation.
I want to create a presentation about this content: ${user_content}
The text you add should be relevant to the content, theme tone and style of the presentation.
Keep the text concise and to the point, avoid writing long paragraphs and prefer concise bullet points using \\n to create new lines.
The JSON data represents a list of slides, and each slide contains shapes with text.
Your task is to make creative and relevant modification to the text content in the provided JSON as per the requirements of presentation.
 

Here is the JSON data:
```json
{original_json_string}
```

Return the ENTIRE JSON data with your modification. 
Ensure your output is ONLY the modified JSON data, valid and parsable, starting with `[` and ending with `]`.
Do not include any explanatory text or markdown formatting like ```json before or after the JSON output.
"""
        print("Sending content to Gemini AI for modification...")
        print(prompt)
        response = model.generate_content(prompt)
        
        # Clean the response: remove potential markdown code block fences
        modified_json_string = response.text.strip()
        if modified_json_string.startswith("```json"):
            modified_json_string = modified_json_string[7:]
        if modified_json_string.endswith("```"):
            modified_json_string = modified_json_string[:-3]
        
        modified_data = json.loads(modified_json_string.strip())

        with open(updated_json_path, 'w') as f_upd:
            json.dump(modified_data, f_upd, indent=4)
        print(f"Successfully modified JSON content using Gemini AI and saved to '{updated_json_path}'")
        return True

    except FileNotFoundError:
        print(f"Error: Original JSON '{original_json_path}' not found for modification.")
        return False
    except Exception as e:
        print(f"Error during Gemini AI JSON modification: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print("--- Raw LLM Response Text That May Have Caused Error ---")
            print(response.text)
            print("-------------------------------------------------------")
        return False

# --- 3. Update Presentation from JSON ---
def run_presentation_update_step(source_pptx_path, target_pptx_path, updated_json_path):
    """Copies the source PPTX and updates it using the modified JSON file."""
    print(f"--- Step 3: Updating presentation content ---")
    try:
        shutil.copy(source_pptx_path, target_pptx_path)
        print(f"Successfully copied '{source_pptx_path}' to '{target_pptx_path}'")
    except FileNotFoundError:
        print(f"Error: Source presentation '{source_pptx_path}' not found for copying.")
        return False
    except Exception as e:
        print(f"Error copying presentation: {e}")
        return False

    success = update_presentation_from_json(updated_json_path, target_pptx_path)
    if success:
        print(f"Presentation update based on '{updated_json_path}' completed.")
    else:
        print(f"Failed to update presentation using '{updated_json_path}'.")
    return success

# --- Main Workflow Execution ---
if __name__ == "__main__":
    print("Starting Presentation Update Workflow...")
    print(f"Working directory: {os.getcwd()}")

    pycache_dir_name = "__pycache__" # Name of the directory to be cleaned up
    workflow_status_message = "Workflow did not complete successfully."
    overall_success = False # Flag to track if the main workflow steps succeeded
    user_content = open("user_content.txt", "r").read()
    print(f"found user content: {user_content[:10]}") 
    try:
        if not os.path.exists(ORIGINAL_TEMPLATE_PPTX):
            workflow_status_message = f"Error: Original template '{ORIGINAL_TEMPLATE_PPTX}' not found. Please ensure it exists in the script's directory."
        elif not run_extraction_step(ORIGINAL_TEMPLATE_PPTX, SLIDE_DETAILS_JSON):
            workflow_status_message = "Workflow aborted at extraction step."
        else:
            print("\n") 
            if not placeholder_modify_json_content(SLIDE_DETAILS_JSON, USER_UPDATED_JSON_CONTENT, user_content):
                workflow_status_message = "Workflow aborted at JSON modification step."
            else:
                print("\n")
                if not run_presentation_update_step(ORIGINAL_TEMPLATE_PPTX, FINAL_UPDATED_PPTX, USER_UPDATED_JSON_CONTENT):
                    workflow_status_message = "Workflow aborted at presentation update step."
                else:
                    workflow_status_message = "\nPresentation Update Workflow completed successfully!"
                    overall_success = True # Mark success only if all steps complete
        
        print(workflow_status_message) # Print final status of the core workflow

    except Exception as e:
        print(f"An unexpected error occurred during the main workflow: {e}")
        # workflow_status_message will reflect the last failure or the generic error
    finally:
        print("\n--- Starting Cleanup --- ")
        # Construct path to __pycache__ relative to the script's directory
        # __file__ might not be defined if run in some environments (e.g. exec), so fallback to CWD
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError: # __file__ is not defined
            script_dir = os.getcwd()
        
        pycache_path_in_script_dir = os.path.join(script_dir, pycache_dir_name)

        # Check in script's directory
        if os.path.exists(pycache_path_in_script_dir):
            try:
                shutil.rmtree(pycache_path_in_script_dir)
                print(f"Successfully removed '{pycache_path_in_script_dir}'.")
            except OSError as e:
                print(f"Error removing '{pycache_path_in_script_dir}': {e}")
            except Exception as e:
                print(f"An unexpected error during '{pycache_path_in_script_dir}' cleanup: {e}")
        else:
            print(f"Directory '{pycache_path_in_script_dir}' not found (checked in script's dir). No cleanup needed for it there.")

        # Additionally, check if __pycache__ is in CWD, if CWD is different from script_dir
        # This covers cases where __pycache__ might be created based on CWD rather than script location.
        current_working_dir = os.getcwd()
        if script_dir != current_working_dir:
            pycache_path_in_cwd = os.path.join(current_working_dir, pycache_dir_name)
            if os.path.exists(pycache_path_in_cwd):
                try:
                    shutil.rmtree(pycache_path_in_cwd)
                    print(f"Successfully removed '{pycache_path_in_cwd}' (found in CWD).")
                except OSError as e:
                    print(f"Error removing '{pycache_path_in_cwd}' from CWD: {e}")
                except Exception as e:
                    print(f"An unexpected error during '{pycache_path_in_cwd}' (CWD) cleanup: {e}")
            else:
                print(f"Directory '{pycache_path_in_cwd}' also not found in CWD '{current_working_dir}'.")

        print("--- Cleanup Finished --- ")

    # If you need to signal overall success/failure to an external process:
    # if not overall_success:
    #     import sys
    #     sys.exit(1) 