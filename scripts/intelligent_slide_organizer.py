import json
import google.generativeai as genai
from typing import List, Dict, Any

def analyze_and_reorganize_slides(original_slides_json_path: str, user_content: str, api_key: str, model_name: str) -> Dict[str, Any]:
    """
    Uses Gemini AI to analyze slides and determine optimal organization based on user requirements.
    
    Args:
        original_slides_json_path: Path to the extracted slide details JSON
        user_content: User's content requirements
        api_key: Google API key for Gemini
        model_name: Gemini model name to use
    
    Returns:
        Dictionary containing reorganization decisions and reasoning
    """
    try:
        with open(original_slides_json_path, 'r') as f:
            original_slides = json.load(f)
    except Exception as e:
        print(f"Error reading original slides JSON: {e}")
        return None
    
    # Configure Gemini AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Use the complete slide details instead of creating a summary
    # This gives the AI access to all shape information, positioning, IDs, etc.
    
    # Create prompt for AI analysis
    prompt = f"""
You are an expert presentation consultant. Analyze the following presentation slides and user requirements to determine the optimal slide organization.

IMPORTANT: Your goal is to PRESERVE USEFUL SLIDE STRUCTURES that can be repurposed with new content, not to remove slides based on current content mismatch.

Focus on:
- Keep slides with useful LAYOUTS (Title, Content, Agenda, etc.) that can be repurposed
- Remove only slides with very specific/unusable structures (like financial tables, specific charts)
- Ensure you keep enough slides to cover the user's content requirements
- Prioritize structural utility over current content relevance

USER REQUIREMENTS:
{user_content}

CURRENT SLIDES COMPLETE DETAILS:
{json.dumps(original_slides, indent=2)}

Your task is to:
1. Count how many content slides the user needs (look for numbered lists, topics, etc.)
2. Keep slides with flexible layouts (Title, Content, Agenda, Closing) that can be repurposed
3. Remove only slides with very specific/rigid structures that cannot be adapted
4. Ensure the final slide count can accommodate the user's content requirements
5. Reorder slides for logical presentation flow
6. Focus on LAYOUT UTILITY rather than current content relevance

Respond with a JSON object in this exact format:
{{
    "analysis": {{
        "user_content_theme": "brief description of what the user wants to present about",
        "total_original_slides": {len(original_slides)},
        "recommended_action": "keep_all|remove_some|reorder_only"
    }},
    "slide_decisions": [
        {{
            "original_index": 0,
            "action": "keep|remove",
            "new_position": 0,
            "relevance_score": 0.9,
            "reasoning": "why this slide should be kept/removed and its position"
        }}
    ],
    "final_slide_order": [0, 2, 1],
    "removed_slides": [3, 4],
    "organization_reasoning": "Overall explanation of the reorganization strategy"
}}

Rules:
- Only include slides with action "keep" in final_slide_order
- new_position should reflect the position in the reorganized presentation (0-indexed)
- relevance_score should be 0.0-1.0 based on LAYOUT UTILITY (not current content)
- Be CONSERVATIVE - keep slides that can be repurposed even if current content is irrelevant
- Ensure you keep enough slides to cover all user requirements (count the topics/sections needed)
- Prioritize keeping: Title slides, Content slides, Agenda slides, Closing slides
- Remove only: Financial tables, specific charts, very rigid/specialized layouts

Return ONLY the JSON response, no additional text or markdown formatting.
"""
    
    try:
        print("Analyzing slides with Gemini AI for optimal organization...")
        response = model.generate_content(prompt)
        
        # Clean the response and extract only the JSON part
        response_text = response.text.strip()
        
        # Remove markdown code block markers
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # Find the JSON object boundaries more carefully
        # Look for the opening brace and count braces to find the matching closing brace
        start_idx = response_text.find('{')
        if start_idx == -1:
            json_text = response_text.strip()
        else:
            brace_count = 0
            end_idx = start_idx
            for i, char in enumerate(response_text[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            json_text = response_text[start_idx:end_idx]
        
        analysis_result = json.loads(json_text)
        
        # Validate the response structure
        required_keys = ["analysis", "slide_decisions", "final_slide_order", "removed_slides", "organization_reasoning"]
        if not all(key in analysis_result for key in required_keys):
            raise ValueError("AI response missing required keys")
        
        # Handle edge case where AI removes too many slides
        if len(analysis_result["final_slide_order"]) < 3:
            print(f"Warning: AI kept only {len(analysis_result['final_slide_order'])} slides. Ensuring minimum viable presentation.")
            
            # Count how many topics the user needs (rough estimate)
            user_topics = user_content.lower().count('\n') + user_content.count('1.') + user_content.count('2.') + user_content.count('3.') + user_content.count('4.') + user_content.count('5.')
            min_slides_needed = max(3, min(user_topics + 2, 6))  # At least 3, at most 6 slides
            
            # Find slides with useful layouts to keep
            useful_layouts = ["title", "content", "agenda", "closing", "section"]
            slides_to_add = []
            
            for i, slide in enumerate(original_slides):
                if i not in analysis_result["final_slide_order"]:
                    layout_name = slide.get("slide_layout_name", "").lower()
                    if any(useful in layout_name for useful in useful_layouts):
                        slides_to_add.append(i)
                        if len(analysis_result["final_slide_order"]) + len(slides_to_add) >= min_slides_needed:
                            break
            
            # Add the useful slides back
            for slide_idx in slides_to_add:
                analysis_result["final_slide_order"].append(slide_idx)
                # Update the decision for this slide
                for decision in analysis_result["slide_decisions"]:
                    if decision["original_index"] == slide_idx:
                        decision["action"] = "keep"
                        decision["new_position"] = len(analysis_result["final_slide_order"]) - 1
                        decision["relevance_score"] = 0.6
                        decision["reasoning"] += " (Added back for layout utility)"
                        break
                # Remove from removed_slides if it's there
                if slide_idx in analysis_result["removed_slides"]:
                    analysis_result["removed_slides"].remove(slide_idx)
            
            print(f"Added {len(slides_to_add)} slides back. Final count: {len(analysis_result['final_slide_order'])} slides.")
        
        return analysis_result
        
    except Exception as e:
        print(f"Error during AI slide analysis: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print("--- Raw AI Response ---")
            print(response.text)
            print("----------------------")
        return None

def apply_slide_reorganization(original_slides_json_path: str, reorganized_slides_json_path: str, analysis_result: Dict[str, Any]) -> bool:
    """
    Applies the AI's reorganization decisions to create a new slides JSON file.
    
    Args:
        original_slides_json_path: Path to original slides JSON
        reorganized_slides_json_path: Path where reorganized slides JSON will be saved
        analysis_result: Result from analyze_and_reorganize_slides
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(original_slides_json_path, 'r') as f:
            original_slides = json.load(f)
    except Exception as e:
        print(f"Error reading original slides: {e}")
        return False
    
    try:
        final_order = analysis_result["final_slide_order"]
        reorganized_slides = []
        
        # Create reorganized slides list based on AI decisions
        for new_index, original_index in enumerate(final_order):
            if original_index < len(original_slides):
                slide_copy = original_slides[original_index].copy()
                # Update the slide index to reflect new position
                slide_copy["slide_index"] = new_index
                # Add metadata about the reorganization
                slide_copy["original_index"] = original_index
                slide_copy["reorganization_applied"] = True
                reorganized_slides.append(slide_copy)
            else:
                print(f"Warning: Original index {original_index} is out of bounds")
        
        # Save reorganized slides
        with open(reorganized_slides_json_path, 'w') as f:
            json.dump(reorganized_slides, f, indent=4)
        
        print(f"Successfully created reorganized slides JSON with {len(reorganized_slides)} slides")
        print(f"Original slides: {len(original_slides)} -> Final slides: {len(reorganized_slides)}")
        
        if analysis_result.get("removed_slides"):
            print(f"Removed slides (original indices): {analysis_result['removed_slides']}")
        
        return True
        
    except Exception as e:
        print(f"Error applying slide reorganization: {e}")
        return False

def intelligent_slide_organization_step(original_json_path: str, reorganized_json_path: str, user_content: str, api_key: str, model_name: str) -> bool:
    """
    Complete workflow step for intelligent slide organization.
    
    Args:
        original_json_path: Path to extracted slide details
        reorganized_json_path: Path where reorganized slides will be saved
        user_content: User's content requirements
        api_key: Google API key
        model_name: Gemini model name
    
    Returns:
        True if successful, False otherwise
    """
    print("--- Step 1.5: Intelligent Slide Organization ---")
    
    # Analyze slides with AI
    analysis_result = analyze_and_reorganize_slides(original_json_path, user_content, api_key, model_name)
    
    if not analysis_result:
        print("Failed to analyze slides. Proceeding with original slide order.")
        # Copy original file as fallback
        try:
            import shutil
            shutil.copy(original_json_path, reorganized_json_path)
            return True
        except Exception as e:
            print(f"Error copying original slides as fallback: {e}")
            return False
    
    # Print analysis summary
    analysis = analysis_result.get("analysis", {})
    print(f"Content Theme: {analysis.get('user_content_theme', 'Unknown')}")
    print(f"Recommended Action: {analysis.get('recommended_action', 'Unknown')}")
    print(f"Organization Reasoning: {analysis_result.get('organization_reasoning', 'No reasoning provided')}")
    
    # Apply reorganization
    success = apply_slide_reorganization(original_json_path, reorganized_json_path, analysis_result)
    
    if success:
        print("Slide organization completed successfully!")
    else:
        print("Failed to apply slide reorganization.")
    
    return success

if __name__ == "__main__":
    # Test the module independently
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-05-20")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        exit(1)
    
    # Test with sample data
    original_json = "./content/slide_details.json"
    reorganized_json = "./content/slide_details_reorganized.json"
    user_content = "I want to create a presentation about machine learning fundamentals"
    
    success = intelligent_slide_organization_step(original_json, reorganized_json, user_content, api_key, model_name)
    print(f"Test completed. Success: {success}") 