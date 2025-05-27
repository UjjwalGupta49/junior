#!/usr/bin/env python3
"""
Example Usage Script for Dual Template Selector
==============================================

This script demonstrates different ways to use the intelligent dual template selector
with user content as parameters.
"""

import os
from .intelligent_template_selector_dual import select_dual_templates, select_templates_for_content

def example_1_basic_usage():
    """Example 1: Basic usage with user content as parameter"""
    print("="*60)
    print("📝 EXAMPLE 1: Basic Usage")
    print("="*60)
    
    user_content = """
    I need to create a business presentation about our company's quarterly financial performance. 
    The presentation should include revenue growth charts, expense breakdowns, profit margins, 
    and future financial projections. The audience will be our board of directors and senior 
    executives, so it needs to be professional and data-driven.
    """
    
    matches = select_dual_templates(
        user_content=user_content
    )
    
    return matches

def example_2_with_requirements():
    """Example 2: Usage with additional requirements"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 2: With Additional Requirements")
    print("="*60)
    
    user_content = """
    I want to create an educational presentation about renewable energy sources for high school 
    students. The presentation should cover solar power, wind energy, hydroelectric power, and 
    their environmental benefits. It should be engaging and visually appealing to keep students 
    interested.
    """
    
    requirements = """
    I need a template with bright colors and modern design that works well for educational 
    content. The template should have good space for images and charts, and should be 
    suitable for a younger audience while maintaining professionalism.
    """
    
    matches = select_dual_templates(
        user_content=user_content,
        user_requirements=requirements
    )
    
    return matches

def example_3_silent_mode():
    """Example 3: Silent mode with custom parameters"""
    print("\n" + "="*60)
    print("🔇 EXAMPLE 3: Silent Mode (No Verbose Output)")
    print("="*60)
    
    user_content = """
    I need to create a pitch deck for our startup. We're developing an AI-powered customer 
    service chatbot. The presentation should cover the problem we're solving, our solution, 
    market opportunity, business model, team background, and funding requirements. This is 
    for potential investors.
    """
    
    # Run in silent mode with no verbose output
    matches = select_dual_templates(
        user_content=user_content,
        verbose=False,
        save_results=False
    )
    
    # Display results manually
    if matches:
        print("🎯 Selected Templates (Silent Mode):")
        for i, match in enumerate(matches, 1):
            print(f"   {i}. {match.template_title}")
            print(f"      Confidence: {match.confidence_score:.2f}")
            print(f"      Template ID: {match.template_id}")
    else:
        print("❌ No templates found in silent mode")
    
    return matches

def example_4_simplified_function():
    """Example 4: Using the simplified function"""
    print("\n" + "="*60)
    print("⚡ EXAMPLE 4: Using Simplified Function")
    print("="*60)
    
    content = """
    I'm preparing a presentation about digital marketing strategies for small businesses. 
    Topics include social media marketing, email campaigns, content marketing, SEO basics, 
    and measuring ROI. The audience will be small business owners with limited marketing 
    experience.
    """
    
    requirements = "Modern, professional template suitable for business training"
    
    matches = select_templates_for_content(
        content=content,
        requirements=requirements
    )
    
    return matches

def example_5_programmatic_usage():
    """Example 5: Programmatic usage with custom content"""
    print("\n" + "="*60)
    print("🤖 EXAMPLE 5: Programmatic Usage")
    print("="*60)
    
    # Simulate getting content from user input or another system
    presentation_topics = [
        "Introduction to Machine Learning",
        "Data preprocessing and cleaning",
        "Supervised vs Unsupervised learning",
        "Popular ML algorithms overview",
        "Real-world ML applications"
    ]
    
    target_audience = "Software developers new to machine learning"
    presentation_goal = "Educational workshop"
    
    # Construct content programmatically
    content = f"""
    I need to create a {presentation_goal} presentation about machine learning fundamentals. 
    The presentation should cover: {', '.join(presentation_topics)}.
    
    Target audience: {target_audience}
    
    The presentation should be technical but accessible, with practical examples and 
    hands-on coding demonstrations. It should bridge the gap between theory and practice.
    """
    
    print(f"📄 Generated content: {content[:100]}...")
    
    matches = select_dual_templates(
        user_content=content,
        user_requirements="Technical presentation template with good code display capabilities"
    )
    
    return matches

def main():
    """Run all examples"""
    print("🚀 Dual Template Selector - Usage Examples")
    print("This script demonstrates various ways to use the template selector\n")
    
    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google Gemini API key in the .env file")
        return
    
    all_results = []
    
    try:
        # Run examples
        results1 = example_1_basic_usage()
        all_results.extend(results1 if results1 else [])
        
        results2 = example_2_with_requirements()
        all_results.extend(results2 if results2 else [])
        
        results3 = example_3_silent_mode()
        all_results.extend(results3 if results3 else [])
        
        results4 = example_4_simplified_function()
        all_results.extend(results4 if results4 else [])
        
        results5 = example_5_programmatic_usage()
        all_results.extend(results5 if results5 else [])
        
        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY OF ALL EXAMPLES")
        print("="*60)
        print(f"Total template matches found: {len(all_results)}")
        
        if all_results:
            unique_templates = set(match.template_id for match in all_results)
            print(f"Unique templates recommended: {len(unique_templates)}")
            
            print("\nMost frequently recommended templates:")
            from collections import Counter
            template_counts = Counter(match.template_title for match in all_results)
            for template, count in template_counts.most_common(3):
                print(f"   • {template} ({count} times)")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
    
    print("\n✨ Examples completed!")

if __name__ == "__main__":
    main() 