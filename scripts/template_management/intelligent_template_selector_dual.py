import json
import os
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TemplateMatch:
    """Represents a template match with detailed scoring"""
    template_id: str
    template_title: str
    confidence_score: float
    reasoning: str
    matching_factors: Dict[str, float]
    use_case_alignment: float
    design_suitability: float
    content_compatibility: float

class DualTemplateSelector:
    """
    Intelligent template selector that finds the two best matching templates
    using Gemini AI analysis of user content and template characteristics.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-preview-05-20"):
        self.api_key = api_key
        self.model_name = model_name
        self.templates_data = None
        
        # Initialize Gemini AI
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            print(f"✅ Initialized Gemini AI model: {model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini AI: {e}")
            raise
    
    def load_templates_database(self, templates_path: str) -> bool:
        """Load the Microsoft templates database"""
        try:
            if not os.path.exists(templates_path):
                print(f"❌ Templates database not found: {templates_path}")
                return False
            
            with open(templates_path, 'r', encoding='utf-8') as f:
                self.templates_data = json.load(f)
            
            total_templates = len(self.templates_data.get('templates', []))
            print(f"📚 Loaded {total_templates} templates from database")
            return True
            
        except Exception as e:
            print(f"❌ Error loading templates database: {e}")
            return False
    
    def select_best_two_templates(self, user_content: str, user_requirements: str = "") -> List[TemplateMatch]:
        """
        Select the two best matching templates based on user content and requirements
        
        Args:
            user_content: The content that will be used in the presentation
            user_requirements: Additional user requirements or preferences
        
        Returns:
            List of top 2 TemplateMatch objects
        """
        if not self.templates_data:
            print("❌ Templates database not loaded")
            return []
        
        try:
            print("🧠 Analyzing user content and selecting best templates...")
            
            # Prepare templates summary for AI analysis
            templates_summary = self._prepare_templates_summary()
            
            # Create comprehensive prompt for dual template selection
            prompt = self._create_dual_selection_prompt(user_content, user_requirements, templates_summary)
            
            # Make AI request with retry logic
            response = self._make_ai_request_with_retry(prompt)
            if not response:
                return []
            
            # Parse AI response to get top 2 recommendations
            matches = self._parse_dual_ai_response(response.text)
            
            if matches:
                print(f"🎯 Successfully selected {len(matches)} template matches:")
                for i, match in enumerate(matches, 1):
                    print(f"   {i}. {match.template_title} (confidence: {match.confidence_score:.2f})")
                return matches
            else:
                print("❌ Failed to parse AI recommendations")
                return []
                
        except Exception as e:
            print(f"❌ Error during template selection: {e}")
            return []
    
    def _prepare_templates_summary(self) -> str:
        """Prepare a comprehensive summary of available templates for AI analysis"""
        templates = self.templates_data.get('templates', [])
        
        summary_parts = []
        for template in templates:
            template_info = f"""
Template ID: {template['id']}
Title: {template['title']}
Description: {template['description']}
Category: {template['category']}
Theme: {template['theme']}
Use Cases: {', '.join(template['use_cases'])}
Color Scheme: {template['color_scheme']}
"""
            summary_parts.append(template_info.strip())
        
        return '\n---\n'.join(summary_parts)
    
    def _create_dual_selection_prompt(self, user_content: str, user_requirements: str, templates_summary: str) -> str:
        """Create a comprehensive prompt for AI to select the two best templates"""
        
        prompt = f"""
You are an expert presentation designer with deep knowledge of visual communication, business presentations, and template selection. Your task is to analyze user content and select the TWO BEST matching PowerPoint templates from a database of Microsoft templates.

USER CONTENT TO ANALYZE:
{user_content}

ADDITIONAL USER REQUIREMENTS:
{user_requirements if user_requirements else "None specified"}

AVAILABLE TEMPLATES:
{templates_summary}

SELECTION CRITERIA:
Please evaluate each template based on these factors:
1. **Content Compatibility** (0.0-1.0): How well the template structure suits the user's content type
2. **Use Case Alignment** (0.0-1.0): How well the template's intended use cases match the user's needs
3. **Design Suitability** (0.0-1.0): How appropriate the visual design is for the content and audience
4. **Layout Appropriateness** (0.0-1.0): How well the template's layout types support the content structure
5. **Professional Fit** (0.0-1.0): How well the template matches the professional context

ANALYSIS INSTRUCTIONS:
1. Analyze the user's content to understand:
   - Content type (business, educational, technical, creative, etc.)
   - Presentation purpose (pitch, report, training, overview, etc.)
   - Target audience (executives, students, general public, etc.)
   - Content structure (data-heavy, narrative, visual, etc.)

2. For each template, consider:
   - Does the template category match the content type?
   - Are the layout types suitable for the content structure?
   - Do the use cases align with the presentation purpose?
   - Is the design theme appropriate for the audience?
   - Do the features support the content requirements?

3. Select the TWO BEST templates that offer:
   - Highest overall compatibility
   - Complementary strengths (e.g., one data-focused, one narrative-focused)
   - Professional appropriateness
   - Design variety while maintaining quality

OUTPUT FORMAT:
Return EXACTLY this JSON structure with no additional text:

[
    {{
        "template_id": "exact-template-id-from-database",
        "template_title": "Template Name",
        "confidence_score": 0.95,
        "reasoning": "Detailed explanation of why this template is the best choice, including specific alignment with user content, use case match, and design appropriateness",
        "matching_factors": {{
            "content_compatibility": 0.9,
            "use_case_alignment": 0.95,
            "design_suitability": 0.85,
            "layout_appropriateness": 0.9,
            "professional_fit": 0.95
        }},
        "use_case_alignment": 0.95,
        "design_suitability": 0.85,
        "content_compatibility": 0.9
    }},
    {{
        "template_id": "exact-template-id-from-database-2",
        "template_title": "Second Template Name",
        "confidence_score": 0.88,
        "reasoning": "Detailed explanation of why this is the second-best choice, highlighting different strengths or complementary features",
        "matching_factors": {{
            "content_compatibility": 0.85,
            "use_case_alignment": 0.9,
            "design_suitability": 0.9,
            "layout_appropriateness": 0.85,
            "professional_fit": 0.9
        }},
        "use_case_alignment": 0.9,
        "design_suitability": 0.9,
        "content_compatibility": 0.85
    }}
]

IMPORTANT:
- Return ONLY the JSON array, no markdown formatting or additional text
- Ensure template_id exactly matches the ID from the database
- Confidence scores should reflect realistic assessment (typically 0.7-0.95)
- Provide detailed, specific reasoning for each selection
- Consider complementary strengths between the two selections
"""
        return prompt
    
    def _make_ai_request_with_retry(self, prompt: str, max_retries: int = 3):
        """Make AI request with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                print(f"⚠️  AI request attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"❌ AI request failed after {max_retries} attempts")
                    return None
                
                # Exponential backoff
                wait_time = 2 ** attempt
                print(f"🔄 Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return None
    
    def _parse_dual_ai_response(self, response_text: str) -> List[TemplateMatch]:
        """Parse AI response to extract the two template recommendations"""
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Find JSON array boundaries
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                print("❌ No JSON array found in AI response")
                return []
            
            json_text = response_text[start_idx:end_idx]
            data = json.loads(json_text)
            
            matches = []
            for item in data:
                match = TemplateMatch(
                    template_id=item["template_id"],
                    template_title=item["template_title"],
                    confidence_score=item["confidence_score"],
                    reasoning=item["reasoning"],
                    matching_factors=item["matching_factors"],
                    use_case_alignment=item["use_case_alignment"],
                    design_suitability=item["design_suitability"],
                    content_compatibility=item["content_compatibility"]
                )
                matches.append(match)
            
            return matches[:2]  # Ensure we only return top 2
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            return []
        except KeyError as e:
            print(f"❌ Missing required field in AI response: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
            return []
    
    def get_template_details(self, template_id: str) -> Optional[Dict]:
        """Get full details of a specific template"""
        if not self.templates_data:
            return None
        
        for template in self.templates_data.get("templates", []):
            if template["id"] == template_id:
                return template
        
        return None
    
    def save_selections(self, matches: List[TemplateMatch], output_path: str):
        """Save the template selections to a JSON file"""
        try:
            selections_data = {
                "selection_metadata": {
                    "total_templates_analyzed": len(self.templates_data.get("templates", [])),
                    "top_selections": len(matches),
                    "selection_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "selections": []
            }
            
            for i, match in enumerate(matches, 1):
                selection = {
                    "rank": i,
                    "match_details": asdict(match),
                    "template_details": self.get_template_details(match.template_id)
                }
                selections_data["selections"].append(selection)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(selections_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved template selections to {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving selections: {e}")
    
    def display_results(self, matches: List[TemplateMatch]):
        """Display the selection results in a formatted way"""
        if not matches:
            print("❌ No template matches found")
            return
        
        print("\n" + "="*80)
        print("🎯 TEMPLATE SELECTION RESULTS")
        print("="*80)
        
        for i, match in enumerate(matches, 1):
            print(f"\n🏆 RANK {i} - {match.template_title}")
            print(f"   Template ID: {match.template_id}")
            print(f"   Confidence Score: {match.confidence_score:.2f}")
            print(f"   Content Compatibility: {match.content_compatibility:.2f}")
            print(f"   Use Case Alignment: {match.use_case_alignment:.2f}")
            print(f"   Design Suitability: {match.design_suitability:.2f}")
            print(f"   Reasoning: {match.reasoning}")
            
            # Get additional template details
            template_details = self.get_template_details(match.template_id)
            if template_details:
                print(f"   Category: {template_details['category']}")
                print(f"   Theme: {template_details['theme']}")
                print(f"   Use Cases: {', '.join(template_details['use_cases'])}")
                print(f"   Layout Types: {', '.join(template_details['layout_types'])}")
        
        print("\n" + "="*80)

def select_dual_templates(user_content: str, templates_db_path: str = None, user_requirements: str = "", 
                         api_key: str = None, model_name: str = "gemini-2.5-flash-preview-05-20", 
                         verbose: bool = True, save_results: bool = True) -> List[TemplateMatch]:
    """
    Main function to select the two best matching templates
    
    Args:
        user_content: Content for the presentation (required)
        templates_db_path: Path to Microsoft templates JSON file (optional, defaults to standard location)
        user_requirements: Additional requirements or preferences (optional)
        api_key: Google Gemini API key (optional, will use env var if not provided)
        model_name: Gemini model name (optional)
        verbose: Whether to display detailed output (default: True)
        save_results: Whether to save results to JSON file (default: True)
    
    Returns:
        List of top 2 TemplateMatch objects
    """
    
    # Validate user content
    if not user_content or not user_content.strip():
        print("❌ User content is required and cannot be empty.")
        return []
    
    # Set default templates database path if not provided
    if not templates_db_path:
        templates_db_path = "./scrapers/content/microsoft_templates.json"
    
    # Use provided API key or get from environment
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ Google API key not provided. Please set GOOGLE_API_KEY environment variable.")
        return []
    
    if verbose:
        print("🚀 Starting Intelligent Dual Template Selection...")
        print(f"📄 Analyzing user content ({len(user_content)} characters)")
    
    # Initialize selector
    selector = DualTemplateSelector(api_key, model_name)
    
    # Load templates database
    if not selector.load_templates_database(templates_db_path):
        return []
    
    # Select best two templates
    matches = selector.select_best_two_templates(user_content, user_requirements)
    
    if matches:
        if verbose:
            # Display results
            selector.display_results(matches)
        
        if save_results:
            # Save results
            output_path = os.path.join(os.path.dirname(templates_db_path), "dual_template_selections.json")
            selector.save_selections(matches, output_path)
        
        if verbose:
            print("✅ Dual template selection completed successfully!")
    else:
        if verbose:
            print("❌ Dual template selection failed!")
    
    return matches

def select_templates_for_content(content: str, requirements: str = "", **kwargs) -> List[TemplateMatch]:
    """
    Simplified function to select templates for given content
    
    Args:
        content: The presentation content to analyze
        requirements: Optional additional requirements
        **kwargs: Additional parameters passed to select_dual_templates
    
    Returns:
        List of top 2 TemplateMatch objects
    """
    return select_dual_templates(
        user_content=content,
        user_requirements=requirements,
        **kwargs
    )

def main():
    """Main function with command line argument support"""
    import sys
    
    # Check if user content is provided as command line argument
    if len(sys.argv) > 1:
        user_content = " ".join(sys.argv[1:])
        print(f"📝 Using provided user content: {user_content[:100]}...")
    else:
        print("😭 No user content provided")
        return []
    
    # Optional requirements (can be extended to accept as parameter too)
    user_requirements = ""
    
    # Path to the Microsoft templates database
    templates_db_path = "./scrapers/content/microsoft_templates.json"
    
    # Run dual template selection
    matches = select_dual_templates(
        user_content=user_content,
        templates_db_path=templates_db_path,
        user_requirements=user_requirements
    )
    
    if matches:
        print(f"\n🎉 Selected {len(matches)} templates for your presentation!")
        for i, match in enumerate(matches, 1):
            print(f"   {i}. {match.template_title} (ID: {match.template_id})")
        return matches
    else:
        print("\n😞 No suitable templates found. Please try different content or requirements.")
        return []

if __name__ == "__main__":
    main() 