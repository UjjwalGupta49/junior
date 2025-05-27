#!/usr/bin/env python3
"""
Dual Template Selector Usage Script
===================================

This script demonstrates how to use the intelligent dual template selector
to find the two best matching PowerPoint templates for your content.

Usage:
    python run_dual_template_selector.py

Requirements:
    - Google Gemini API key in .env file
    - Microsoft templates database (microsoft_templates.json)
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from .intelligent_template_selector_dual import select_dual_templates

def main():
    """Main function to run dual template selection"""
    
    print("🎯 Intelligent Dual Template Selector")
    print("=" * 50)
    
    # Configuration
    templates_db_path = "./scrapers/content/microsoft_templates.json"
    
    # Check if templates database exists
    if not os.path.exists(templates_db_path):
        print(f"❌ Templates database not found: {templates_db_path}")
        print("Please ensure the Microsoft templates database exists.")
        return
    
    # Load user content from file or use sample content
    user_content_path = "./user/user_content.txt"
    
    if os.path.exists(user_content_path):
        print(f"📖 Loading user content from: {user_content_path}")
        with open(user_content_path, 'r', encoding='utf-8') as f:
            user_content = f.read().strip()
    else:
        print("📝 Using sample blockchain content")
        user_content = """
        I want to create a presentation about blockchain and cryptocurrency fundamentals for beginners 
        with a maximum of 5 slides. The presentation should cover: 1. Introduction to Blockchain - what 
        it is and why it's revolutionary 2. How Blockchain Works - basic concepts like blocks, chains, 
        and decentralization 3. Cryptocurrency Basics - Bitcoin, digital wallets, and how crypto 
        transactions work 4. Real-world applications beyond crypto - supply chain, healthcare, voting 
        systems 5. Getting started with blockchain - popular platforms, wallets, and learning resources. 
        The presentation should be educational, engaging, and suitable for people with no prior blockchain 
        or cryptocurrency experience. Focus on practical understanding and clear explanations rather than 
        complex technical details.
        """
    
    # User requirements (optional)
    # user_requirements = """
    # I need a modern, professional template that works well for educational content. 
    # The audience will be business professionals who are new to blockchain technology. 
    # I prefer clean designs with good readability and space for diagrams or charts.
    # """
    user_requirements = ""
    
    print(f"📄 Content length: {len(user_content)} characters")
    print(f"📋 Requirements: {'Yes' if user_requirements.strip() else 'None'}")
    
    # Run dual template selection
    matches = select_dual_templates(
        user_content=user_content,
        templates_db_path=templates_db_path,
        user_requirements=user_requirements
    )
    
    # Display final summary
    if matches:
        print("\n🎉 SELECTION COMPLETE!")
        print("=" * 50)
        print(f"Found {len(matches)} optimal template matches:")
        
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match.template_title}")
            print(f"   🆔 ID: {match.template_id}")
            print(f"   🎯 Confidence: {match.confidence_score:.1%}")
            print(f"   📊 Content Fit: {match.content_compatibility:.1%}")
            print(f"   🎨 Design Fit: {match.design_suitability:.1%}")
            print(f"   ✅ Use Case Match: {match.use_case_alignment:.1%}")
        
        print(f"\n💾 Results saved to: ./scrapers/content/dual_template_selections.json")
        print("\n📋 Next Steps:")
        print("   1. Review the selected templates")
        print("   2. Choose one for your presentation")
        print("   3. Use the template ID in your main workflow")
        
    else:
        print("\n😞 No suitable templates found.")
        print("💡 Try:")
        print("   - Adjusting your content description")
        print("   - Being more specific about requirements")
        print("   - Checking your API key configuration")

def interactive_mode():
    """Interactive mode for custom content input"""
    print("\n🔄 INTERACTIVE MODE")
    print("=" * 30)
    
    print("Enter your presentation content (press Enter twice when done):")
    content_lines = []
    while True:
        line = input()
        if line == "" and content_lines and content_lines[-1] == "":
            break
        content_lines.append(line)
    
    user_content = "\n".join(content_lines[:-1])  # Remove last empty line
    
    print("\nEnter any specific requirements (optional, press Enter to skip):")
    user_requirements = input().strip()
    
    templates_db_path = "./scrapers/content/microsoft_templates.json"
    
    matches = select_dual_templates(
        user_content=user_content,
        templates_db_path=templates_db_path,
        user_requirements=user_requirements
    )
    
    return matches

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
    
    print("\n✨ Thank you for using the Intelligent Dual Template Selector!") 