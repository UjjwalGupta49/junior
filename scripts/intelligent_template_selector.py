import json
import os
import sys
import logging
import time
from pathlib import Path
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TemplateRecommendation:
    """Represents a template recommendation with reasoning"""
    template_id: str
    template_title: str
    confidence_score: float
    reasoning: str
    matching_criteria: List[str]
    suitability_factors: Dict[str, float]

class IntelligentTemplateSelector:
    """Server-optimized AI-powered template selector using Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-preview-05-20", log_level: str = "INFO"):
        self.api_key = api_key
        self.model_name = model_name
        self.templates_data = None
        self.logger = self._setup_logging(log_level)
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.logger.info(f"Initialized Gemini AI model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI: {e}")
            raise
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging for server environment"""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
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
    
    def load_templates_database(self, templates_json_path: str) -> bool:
        """Load the scraped templates database with server-side validation"""
        try:
            # Validate file exists and is readable
            if not os.path.exists(templates_json_path):
                self.logger.error(f"Templates database file not found: {templates_json_path}")
                return False
            
            file_size = os.path.getsize(templates_json_path)
            if file_size == 0:
                self.logger.error(f"Templates database file is empty: {templates_json_path}")
                return False
            
            self.logger.info(f"Loading templates database ({file_size} bytes): {templates_json_path}")
            
            with open(templates_json_path, 'r', encoding='utf-8') as f:
                self.templates_data = json.load(f)
            
            # Validate database structure
            if not self._validate_database_structure():
                return False
            
            total_templates = self.templates_data['metadata']['total_templates']
            self.logger.info(f"Successfully loaded {total_templates} templates from database")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in templates database: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading templates database: {e}")
            return False
    
    def _validate_database_structure(self) -> bool:
        """Validate the structure of the loaded templates database"""
        try:
            if not isinstance(self.templates_data, dict):
                self.logger.error("Templates data is not a dictionary")
                return False
            
            required_keys = ['metadata', 'templates']
            for key in required_keys:
                if key not in self.templates_data:
                    self.logger.error(f"Missing required key in database: {key}")
                    return False
            
            if not isinstance(self.templates_data['templates'], list):
                self.logger.error("Templates data is not a list")
                return False
            
            # Validate at least one template has required fields
            if self.templates_data['templates']:
                first_template = self.templates_data['templates'][0]
                required_template_keys = ['id', 'title', 'category', 'theme', 'use_cases']
                
                for key in required_template_keys:
                    if key not in first_template:
                        self.logger.warning(f"Template missing recommended key: {key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating database structure: {e}")
            return False
    
    def select_best_template(self, user_content: str, user_requirements: Optional[str] = None) -> Optional[TemplateRecommendation]:
        """
        Select the best template based on user content and requirements using AI analysis
        
        Args:
            user_content: The content that will be used in the presentation
            user_requirements: Additional requirements or preferences (optional)
        
        Returns:
            TemplateRecommendation object with the best template choice
        """
        if not self.templates_data:
            self.logger.error("Templates database not loaded. Call load_templates_database() first.")
            return None
        
        try:
            # Prepare templates summary for AI analysis
            templates_summary = self._prepare_templates_summary()
            
            # Create AI prompt for template selection
            prompt = self._create_selection_prompt(user_content, user_requirements, templates_summary)
            
            self.logger.info("Analyzing user content and selecting best template...")
            
            # Make API call with retry logic
            response = self._make_ai_request_with_retry(prompt, max_retries=3)
            if not response:
                return None
            
            # Parse AI response
            recommendation = self._parse_ai_response(response.text)
            
            if recommendation:
                self.logger.info(f"Selected template: {recommendation.template_title}")
                self.logger.info(f"Confidence: {recommendation.confidence_score:.2f}")
                self.logger.debug(f"Reasoning: {recommendation.reasoning}")
                return recommendation
            else:
                self.logger.error("Failed to parse AI recommendation")
                return None
                
        except Exception as e:
            self.logger.error(f"Error during template selection: {e}")
            return None
    
    def _make_ai_request_with_retry(self, prompt: str, max_retries: int = 3):
        """Make AI request with retry logic for server stability"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                self.logger.warning(f"AI request attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"AI request failed after {max_retries} attempts")
                    return None
                
                # Exponential backoff
                wait_time = 2 ** attempt
                self.logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return None
    
    def get_top_recommendations(self, user_content: str, user_requirements: Optional[str] = None, top_n: int = 3) -> List[TemplateRecommendation]:
        """Get top N template recommendations"""
        if not self.templates_data:
            return []
        
        try:
            templates_summary = self._prepare_templates_summary()
            prompt = self._create_multi_selection_prompt(user_content, user_requirements, templates_summary, top_n)
            
            print(f"🤖 Getting top {top_n} template recommendations...")
            response = self.model.generate_content(prompt)
            
            recommendations = self._parse_multi_ai_response(response.text)
            
            if recommendations:
                print(f"✅ Generated {len(recommendations)} recommendations")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec.template_title} (confidence: {rec.confidence_score:.2f})")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            return []
    
    def _prepare_templates_summary(self) -> str:
        """Prepare a concise summary of all templates for AI analysis"""
        templates = self.templates_data.get("templates", [])
        
        summary_parts = []
        for template in templates:
            template_summary = {
                "id": template["id"],
                "title": template["title"],
                "category": template["category"],
                "theme": template["theme"],
                "estimated_slides": template["estimated_slides"],
                "features": template["features"][:5],  # Limit features for brevity
                "use_cases": template["use_cases"][:3],  # Limit use cases
                "difficulty_level": template["difficulty_level"],
                "description": template["description"][:200] + "..." if len(template["description"]) > 200 else template["description"]
            }
            summary_parts.append(json.dumps(template_summary, indent=2))
        
        return "\n".join(summary_parts)
    
    def _create_selection_prompt(self, user_content: str, user_requirements: Optional[str], templates_summary: str) -> str:
        """Create AI prompt for single template selection"""
        requirements_text = f"\nAdditional Requirements: {user_requirements}" if user_requirements else ""
        
        return f"""
You are an expert presentation consultant. Analyze the user's content and requirements to select the BEST PowerPoint template from the available options.

USER CONTENT:
{user_content}
{requirements_text}

AVAILABLE TEMPLATES:
{templates_summary}

Your task is to:
1. Analyze the user's content theme, purpose, and target audience
2. Match content requirements with template features and capabilities
3. Consider presentation complexity and slide count needs
4. Select the single BEST template that maximizes content-template alignment

Respond with a JSON object in this exact format:
{{
    "selected_template_id": "ms_template_XXX",
    "template_title": "Template Name",
    "confidence_score": 0.95,
    "reasoning": "Detailed explanation of why this template is the best choice",
    "matching_criteria": ["criterion1", "criterion2", "criterion3"],
    "suitability_factors": {{
        "content_alignment": 0.9,
        "design_appropriateness": 0.85,
        "feature_match": 0.8,
        "complexity_fit": 0.9,
        "use_case_match": 0.95
    }}
}}

Consider these factors:
- Content theme and professional level
- Required slide types and layouts
- Visual design preferences
- Presentation complexity
- Target audience appropriateness
- Feature requirements (charts, timelines, etc.)

Return ONLY the JSON response, no additional text.
"""
    
    def _create_multi_selection_prompt(self, user_content: str, user_requirements: Optional[str], templates_summary: str, top_n: int) -> str:
        """Create AI prompt for multiple template recommendations"""
        requirements_text = f"\nAdditional Requirements: {user_requirements}" if user_requirements else ""
        
        return f"""
You are an expert presentation consultant. Analyze the user's content and provide the top {top_n} PowerPoint template recommendations.

USER CONTENT:
{user_content}
{requirements_text}

AVAILABLE TEMPLATES:
{templates_summary}

Provide the top {top_n} template recommendations ranked by suitability. Consider:
- Content theme and purpose alignment
- Design appropriateness for the content
- Required features and layouts
- Presentation complexity needs
- Target audience fit

Respond with a JSON array of recommendations:
[
    {{
        "selected_template_id": "ms_template_XXX",
        "template_title": "Template Name",
        "confidence_score": 0.95,
        "reasoning": "Why this template is recommended",
        "matching_criteria": ["criterion1", "criterion2"],
        "suitability_factors": {{
            "content_alignment": 0.9,
            "design_appropriateness": 0.85,
            "feature_match": 0.8,
            "complexity_fit": 0.9,
            "use_case_match": 0.95
        }}
    }}
]

Return ONLY the JSON array, no additional text.
"""
    
    def _parse_ai_response(self, response_text: str) -> Optional[TemplateRecommendation]:
        """Parse AI response for single template selection"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Find JSON object
            start_idx = response_text.find('{')
            if start_idx == -1:
                return None
            
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
            data = json.loads(json_text)
            
            return TemplateRecommendation(
                template_id=data["selected_template_id"],
                template_title=data["template_title"],
                confidence_score=data["confidence_score"],
                reasoning=data["reasoning"],
                matching_criteria=data["matching_criteria"],
                suitability_factors=data["suitability_factors"]
            )
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return None
    
    def _parse_multi_ai_response(self, response_text: str) -> List[TemplateRecommendation]:
        """Parse AI response for multiple template recommendations"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Find JSON array
            start_idx = response_text.find('[')
            if start_idx == -1:
                return []
            
            bracket_count = 0
            end_idx = start_idx
            for i, char in enumerate(response_text[start_idx:], start_idx):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            
            json_text = response_text[start_idx:end_idx]
            data = json.loads(json_text)
            
            recommendations = []
            for item in data:
                rec = TemplateRecommendation(
                    template_id=item["selected_template_id"],
                    template_title=item["template_title"],
                    confidence_score=item["confidence_score"],
                    reasoning=item["reasoning"],
                    matching_criteria=item["matching_criteria"],
                    suitability_factors=item["suitability_factors"]
                )
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            print(f"Error parsing multi AI response: {e}")
            return []
    
    def get_template_details(self, template_id: str) -> Optional[Dict]:
        """Get full details of a specific template"""
        if not self.templates_data:
            return None
        
        for template in self.templates_data.get("templates", []):
            if template["id"] == template_id:
                return template
        
        return None
    
    def save_recommendation(self, recommendation: TemplateRecommendation, output_path: str):
        """Save template recommendation to file"""
        try:
            recommendation_data = {
                "recommendation": {
                    "template_id": recommendation.template_id,
                    "template_title": recommendation.template_title,
                    "confidence_score": recommendation.confidence_score,
                    "reasoning": recommendation.reasoning,
                    "matching_criteria": recommendation.matching_criteria,
                    "suitability_factors": recommendation.suitability_factors
                },
                "template_details": self.get_template_details(recommendation.template_id),
                "timestamp": json.dumps({"selected_at": "now"})
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(recommendation_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved recommendation to {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving recommendation: {e}")

def template_selection_workflow(user_content: str, templates_db_path: str, api_key: str, model_name: str, user_requirements: Optional[str] = None) -> Optional[TemplateRecommendation]:
    """
    Complete workflow for intelligent template selection
    
    Args:
        user_content: User's presentation content
        templates_db_path: Path to templates JSON database
        api_key: Google Gemini API key
        model_name: Gemini model name
        user_requirements: Additional user requirements (optional)
    
    Returns:
        TemplateRecommendation object or None if failed
    """
    print("🎯 Starting intelligent template selection workflow...")
    
    # Initialize selector
    selector = IntelligentTemplateSelector(api_key, model_name)
    
    # Load templates database
    if not selector.load_templates_database(templates_db_path):
        return None
    
    # Get best template recommendation
    recommendation = selector.select_best_template(user_content, user_requirements)
    
    if recommendation:
        # Save recommendation for reference
        selector.save_recommendation(recommendation, "./content/selected_template.json")
        print("✅ Template selection workflow completed successfully!")
    else:
        print("❌ Template selection workflow failed!")
    
    return recommendation

if __name__ == "__main__":
    # Example usage
    sample_content = """
    I need to create a business presentation about our company's quarterly financial results.
    The presentation should include revenue charts, expense breakdowns, profit margins,
    and future projections. Target audience is executive leadership and board members.
    """
    
    # Run template selection
    recommendation = template_selection_workflow(
        user_content=sample_content,
        templates_db_path="./content/microsoft_templates.json",
        api_key=os.getenv("GOOGLE_API_KEY"),
        model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-05-20")
    )
    
    if recommendation:
        print(f"\n🎉 Recommended template: {recommendation.template_title}")
        print(f"Confidence: {recommendation.confidence_score:.2f}")
        print(f"Reasoning: {recommendation.reasoning}") 