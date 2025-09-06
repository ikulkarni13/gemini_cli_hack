import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
from pathlib import Path

# Load environment variables from .env file manually
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    # Handle both "export KEY=VALUE" and "KEY=VALUE" formats
                    if line.startswith('export '):
                        line = line[7:]  # Remove 'export '
                    key, value = line.split('=', 1)
                    # Clean the value more thoroughly
                    value = value.strip().strip('"\'').strip()
                    # Remove any non-printable characters
                    value = ''.join(char for char in value if char.isprintable())
                    os.environ[key.strip()] = value

load_env_file()

def generate_vision_board_image(analysis: dict, output_path: str = "vision-board.png") -> str:
    """
    Generate a vision board image from the analysis data.
    Uses OpenAI DALL-E or falls back to text-based image generation.
    """
    vision_scenes = analysis.get("vision_board_scenes", [])
    
    if not vision_scenes:
        print("[warn] No vision board scenes found, creating text-based vision board")
        return create_text_based_vision_board(analysis, output_path)
    
    # Try to generate images for each scene
    try:
        return create_ai_generated_vision_board(vision_scenes, analysis, output_path)
    except Exception as e:
        print(f"[warn] AI image generation failed: {e}")
        print("[info] Falling back to text-based vision board")
        return create_text_based_vision_board(analysis, output_path)

def create_ai_generated_vision_board(vision_scenes: list, analysis: dict, output_path: str) -> str:
    """
    Generate vision board using AI image generation (requires OpenAI API key).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found. Set it to generate AI images.")
    
    # Create a collage-style vision board
    board_width, board_height = 1200, 1400
    board = Image.new('RGB', (board_width, board_height), color='#1a1a1a')
    
    # Generate individual scene images
    scene_images = []
    for i, scene in enumerate(vision_scenes[:4]):  # Limit to 4 scenes for layout
        try:
            print(f"[image] Generating scene {i+1}: {scene['theme']}")
            img = generate_single_scene_image(scene['image_description'], api_key)
            if img:
                scene_images.append((img, scene['theme']))
        except Exception as e:
            print(f"[warn] Failed to generate image for {scene['theme']}: {e}")
    
    if not scene_images:
        raise RuntimeError("No images were successfully generated")
    
    # Arrange images in a 2x2 grid with more vertical space
    img_width, img_height = 580, 450
    positions = [(10, 10), (610, 10), (10, 480), (610, 480)]
    
    for i, (img, theme) in enumerate(scene_images[:4]):
        if i < len(positions):
            # Resize and paste image
            img_resized = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            board.paste(img_resized, positions[i])
            
            # Add theme label
            draw = ImageDraw.Draw(board)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text_x, text_y = positions[i][0] + 10, positions[i][1] + img_height - 40
            draw.rectangle([text_x - 5, text_y - 5, text_x + 300, text_y + 35], fill='#000000aa')
            draw.text((text_x, text_y), theme, fill='white', font=font)
    
    # Add title
    draw = ImageDraw.Draw(board)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
    except:
        title_font = ImageFont.load_default()
    
    title = "MY VISION BOARD"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (board_width - title_width) // 2
    draw.text((title_x, board_height - 60), title, fill='white', font=title_font)
    
    board.save(output_path)
    return output_path

def generate_single_scene_image(description: str, api_key: str = None) -> Image.Image:
    """
    Generate an AI image for a vision board scene using OpenAI DALL-E
    
    Args:
        description: The scene description to visualize
        api_key: OpenAI API key (optional, will load from .env if not provided)
    
    Returns:
        PIL Image object
    """
    # Load environment variables
    load_env_file()
    
    # Get API key from parameter or environment
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
    
    # Prepare the API request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Enhanced prompt for better visual results
    enhanced_prompt = f"""Create a high-quality, inspirational vision board image that visualizes success and achievement. 
    The image should be photorealistic and motivational, showing: {description}
    
    Style: Professional, aspirational, bright lighting, successful atmosphere, high quality photography style.
    Avoid text overlays - focus on pure visual storytelling."""
    
    payload = {
        'model': 'dall-e-3',
        'prompt': enhanced_prompt,
        'n': 1,
        'size': '1024x1024',
        'quality': 'standard',
        'response_format': 'url'
    }
    
    try:
        # Make the API request
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"[ai-image] OpenAI API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenAI API request failed: {response.status_code}")
        
        result = response.json()
        image_url = result['data'][0]['url']
        
        # Download the generated image
        img_response = requests.get(image_url, timeout=30)
        if img_response.status_code != 200:
            raise Exception(f"Failed to download generated image: {img_response.status_code}")
        
        # Convert to PIL Image
        image = Image.open(BytesIO(img_response.content))
        return image
        
    except requests.exceptions.RequestException as e:
        print(f"[ai-image] Network error: {e}")
        raise Exception(f"Network error during image generation: {e}")
    except Exception as e:
        print(f"[ai-image] Error generating image: {e}")
        raise

def create_text_based_vision_board(analysis: dict, output_path: str) -> str:
    """
    Create a text-based vision board when AI image generation is not available.
    """
    board_width, board_height = 1200, 1400
    board = Image.new('RGB', (board_width, board_height), color='#0b0b10')
    draw = ImageDraw.Draw(board)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        text_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    y_pos = 40
    
    # Title
    title = "MY VISION BOARD"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (board_width - title_width) // 2
    draw.text((title_x, y_pos), title, fill='#ffffff', font=title_font)
    y_pos += 80
    
    # Themes
    themes = analysis.get("themes", [])[:3]
    if themes:
        draw.text((50, y_pos), "THEMES", fill='#9cc4ff', font=header_font)
        y_pos += 40
        for theme in themes:
            theme_text = f"• {theme['name']}"
            draw.text((70, y_pos), theme_text, fill='#ffffff', font=text_font)
            y_pos += 30
        y_pos += 20
    
    # Future Identities
    identities = analysis.get("future_identities", [])[:2]
    if identities:
        draw.text((50, y_pos), "FUTURE IDENTITIES", fill='#9cc4ff', font=header_font)
        y_pos += 40
        for identity in identities:
            id_text = f"» {identity['title']}"
            draw.text((70, y_pos), id_text, fill='#ffffff', font=text_font)
            y_pos += 25
            # Wrap the "why" text
            why_lines = textwrap.wrap(identity['why'], width=80)
            for line in why_lines:
                draw.text((90, y_pos), line, fill='#cccccc', font=text_font)
                y_pos += 25
            y_pos += 15
    
    # Affirmations
    affirmations = analysis.get("affirmations", [])[:4]
    if affirmations:
        draw.text((50, y_pos), "AFFIRMATIONS", fill='#9cc4ff', font=header_font)
        y_pos += 40
        for affirmation in affirmations:
            aff_text = f"✓ {affirmation}"
            draw.text((70, y_pos), aff_text, fill='#ffffff', font=text_font)
            y_pos += 30
    
    board.save(output_path)
    return output_path
