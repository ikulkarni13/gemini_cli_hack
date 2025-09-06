# AI Vision Board Generator

**What it does**  
Scans your local files and photos, analyzes them with Google Gemini AI, and creates a personalized vision board showing your future successful self. Features:

- **Theme Analysis**: Identifies your strongest themes from file content and photos
- **AI Image Generation**: Creates photorealistic DALL-E images showing you as successful in each theme
- **Personalized Content**: Theme-specific affirmations, future identities, and action prompts
- **Multiple Outputs**: 
  - Terminal display with formatted results
  - `vision-board.html` with embedded images and clean layout
  - `vision-board.png` collage image

## Prerequisites

1. **Gemini CLI**: `npm install -g @google/generative-ai-cli`
2. **Authenticate Gemini**: `gemini auth login`
3. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/account/api-keys)
4. **Python packages**: `pip install -r requirements.txt`

## Setup

1. Clone and install:
```bash
git clone <this-repo>
cd gemini_cli_hack
pip install -r requirements.txt
```

2. Create `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env and add your keys:
OPENAI_API_KEY=sk-proj-your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

## Usage

### Basic Vision Board
```bash
python3 app_direct.py "/path/to/your/folder"
```

### With AI Image Generation
```bash
python3 app_direct.py "/path/to/your/folder" --generate-image
```

### Options
- `--max-files 50`: Limit number of files to scan
- `--generate-image`: Generate AI images using DALL-E
- `--debug`: Show detailed processing information

## Example Output

The generator creates:
- **Themes**: Specific areas like "Photography", "Data Science", "Creative Writing"
- **Future Identities**: "Master Photographer", "AI Research Scientist" 
- **Theme-Specific Affirmations**: "I capture compelling visual stories" (not generic)
- **AI Images**: Photorealistic scenes showing you successful in each theme
- **Action Prompts**: Concrete steps you can take today

## Files Created
- `vision-board.html`: Interactive web page with all content
- `vision-board.png`: Collage image with AI-generated scenes (1200x1400px)
- `vision_board_images/`: Folder with individual AI images

## Troubleshooting

### API Key Issues
If you get authentication errors:

**For Google Gemini:**
```bash
# Set environment variable (temporary)
export GOOGLE_API_KEY='your_google_api_key'

# Or authenticate via CLI
gemini auth login
```

**For OpenAI:**
Make sure your `.env` file contains:
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

### Common Issues
- **"No themes found"**: Make sure your folder contains readable files (text, images, documents)
- **"Image generation failed"**: Check your OpenAI API key and account credits
- **"Vision board cut off"**: The latest version uses 1200x1400px dimensions to show full content

## Features

### Theme-Specific Content
Unlike generic vision boards, this tool creates content specifically tied to what it finds in your files:
- Analyzes your actual photos and documents
- Generates domain-specific affirmations (e.g., "I excel at data visualization" not "I am successful")
- Creates AI images showing you in realistic success scenarios for each theme

### AI Image Generation
Uses OpenAI DALL-E 3 to create high-quality, photorealistic images showing:
- You as successful in each identified theme
- Professional, aspirational settings
- Specific visual elements related to your themes
- Bright, motivational atmosphere