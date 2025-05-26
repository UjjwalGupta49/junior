# JuniorAI - AI-Powered Presentation Generator

An intelligent presentation automation tool that uses Google's Gemini AI to transform user content into professional PowerPoint presentations.

## 🚀 Features

- **AI-Powered Content Generation**: Uses Google Gemini AI to intelligently populate presentation slides
- **Template-Based**: Works with existing PowerPoint templates to maintain consistent design
- **Automated Workflow**: Complete end-to-end automation from content extraction to final presentation
- **JSON-Based Processing**: Intermediate JSON format for flexible content manipulation
- **Clean Architecture**: Modular design with separate extraction, processing, and update components

## 📋 Prerequisites

- Python 3.7 or higher
- Google Gemini AI API key
- PowerPoint template file

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/UjjwalGupta49junior.git
   cd junior
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your Google Gemini AI API key:
   ```
   GOOGLE_API_KEY=your_actual_google_gemini_api_key_here
   MODEL_NAME=gemini-2.5-flash-preview-05-20
   ```

## 🔑 Getting Your Google Gemini AI API Key

1. Visit the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key and add it to your `.env` file

## 📁 Project Structure

```
juniorAI/
├── scripts/
│   ├── main.py                    # Main workflow orchestrator
│   ├── extract_slide_details.py   # Slide content extraction
│   ├── update_presentation_from_json.py  # Presentation update logic
│   ├── template/                  # PowerPoint templates
│   ├── content/                   # Generated JSON files
│   ├── output/                    # Final presentations
│   └── user/                      # User content files
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🚀 Usage

1. **Prepare your content**
   - Create a `user_content.txt` file in the scripts directory
   - Add the content you want to transform into a presentation

2. **Add your PowerPoint template**
   - Place your template file as `scripts/template/template.pptx`

3. **Run the workflow**
   ```bash
   cd scripts
   python main.py
   ```

4. **Get your results**
   - The updated presentation will be saved as `scripts/output/template_updated.pptx`

## 🔄 Workflow Process

The tool follows a 4-step automated workflow:

1. **Extraction**: Extracts slide details from the template into JSON format
2. **AI Processing**: Uses Gemini AI to generate relevant content based on user input
3. **Update**: Applies the AI-generated content back to the presentation
4. **Cleanup**: Removes temporary files and cache

For detailed workflow information, see [scripts/README.md](scripts/README.md).

## ⚙️ Configuration

### Environment Variables

- `GOOGLE_API_KEY` (required): Your Google Gemini AI API key
- `MODEL_NAME` (optional): Gemini model to use (default: `gemini-2.5-flash-preview-05-20`)

### File Paths

All file paths in `main.py` are configurable:
- `ORIGINAL_TEMPLATE_PPTX`: Path to your PowerPoint template
- `SLIDE_DETAILS_JSON`: Intermediate JSON file location
- `USER_UPDATED_JSON_CONTENT`: AI-processed JSON file location
- `FINAL_UPDATED_PPTX`: Output presentation location

## 🔒 Security

- **API Keys**: Never commit API keys to version control. Always use environment variables.
- **Environment Files**: The `.env` file is automatically ignored by Git.
- **Sensitive Data**: Generated presentations and content files are excluded from version control.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your `GOOGLE_API_KEY` is correctly set in the `.env` file
2. **Template Not Found**: Verify that `template.pptx` exists in the `scripts/template/` directory
3. **Permission Errors**: Ensure the script has write permissions for the `output/` and `content/` directories

### Getting Help

- Check the [scripts/README.md](scripts/README.md) for detailed workflow information
- Review the error messages in the console output
- Ensure all dependencies are properly installed

## 🔮 Future Enhancements

- [ ] Intelligent slide removal based on content relevance
- [ ] Dynamic image updates to match presentation content
- [ ] Support for multiple presentation formats
- [ ] Batch processing capabilities
- [ ] Web interface for easier usage

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Made with ❤️ using Google Gemini AI** 