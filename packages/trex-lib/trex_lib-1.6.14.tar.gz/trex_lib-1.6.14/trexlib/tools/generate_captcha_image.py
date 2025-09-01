'''
Created on 13 Mar 2025

@author: jacklok
'''

import random, re, string
from PIL import Image, ImageDraw
import glob
import os
from datetime import datetime

HUMAN_SAFE_ALPHANUMERIC_CHARS     = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'
ALPHANUMERIC_CHARS  = string.ascii_lowercase + string.ascii_uppercase + string.digits

def random_string(number_character, is_human_mistake_safe=False):
    random.seed(datetime.now().timestamp())
    if is_human_mistake_safe:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(HUMAN_SAFE_ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

    else:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

def generate_slider_captcha(width=400, height=200, puzzle_size=50):
    # Create a blank background image
    bg = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(bg)
    
    # Add random shapes/noise to the background
    for _ in range(20):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(x1, width)
        y2 = random.randint(y1, height)
        draw.rectangle([x1, y1, x2, y2], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Generate random Y-coordinate for the slider puzzle
    puzzle_y = random.randint(0, height - puzzle_size)
    
    # Create the puzzle piece (cut-out from the background)
    puzzle = bg.crop((0, puzzle_y, puzzle_size, puzzle_y + puzzle_size))
    
    # Add a border to the puzzle piece
    border = Image.new('RGB', (puzzle_size + 4, puzzle_size + 4), (0, 0, 0))
    border.paste(puzzle, (2, 2))
    
    # Add a hole in the background where the puzzle belongs
    draw.rectangle([0, puzzle_y, puzzle_size, puzzle_y + puzzle_size], fill=(0, 0, 0))
    
    # Save images
    bg.save("captcha_background.png")
    border.save("captcha_puzzle.png")
    
    return puzzle_y

def generate_realistic_slider_captcha(
        background_dir="backgrounds", 
        output_puzzle="captcha_puzzle.png",
        puzzle_width=80,
        puzzle_height=80
    ):
    # Get random real-life background image
    pick_image = os.path.join(background_dir, "*.jpg")
    print(f"pick_image: {pick_image}")
    bg_images = glob.glob(pick_image)
    if not bg_images:
        raise FileNotFoundError(f"No JPG images found in {background_dir}")
    
    # Select random background
    bg_path = random.choice(bg_images)
    bg = Image.open(bg_path).convert("RGB")
    bg_width, bg_height = bg.size
    
    # Resize background if too small
    if bg_width < 600 or bg_height < 400:
        bg = bg.resize((600, 400))
        bg_width, bg_height = 600, 400
    
    # Generate random Y-coordinate (ensure puzzle stays within bounds)
    max_y = bg_height - puzzle_height - 10
    puzzle_y = random.randint(10, max_y)
    puzzle_x = 50  # Fixed horizontal position for simplicity
    
    # Create puzzle piece with transparency
    puzzle = bg.crop((puzzle_x, puzzle_y, puzzle_x + puzzle_width, puzzle_y + puzzle_height))
    
    # Add red border to hole and puzzle piece
    draw = ImageDraw.Draw(bg)
    draw.rectangle(
        [(puzzle_x-2, puzzle_y-2), 
         (puzzle_x + puzzle_width + 2, puzzle_y + puzzle_height + 2)],
        outline=(255, 0, 0),  # Red border
        width=3
    )
    
    # Create transparent puzzle piece
    puzzle_with_border = Image.new("RGBA", (puzzle_width+6, puzzle_height+6))
    puzzle_with_border.paste(puzzle, (3, 3))
    
    # Add outline to puzzle piece
    draw_puzzle = ImageDraw.Draw(puzzle_with_border)
    draw_puzzle.rectangle(
        [(0, 0), (puzzle_width+6, puzzle_height+6)],
        outline=(255, 0, 0),  # Red border
        width=3
    )
    
    # Save outputs
    output_bg =  "captcha_bg_{random}.jpg".format(random=random_string(10))
    bg.save(output_bg)
    puzzle_with_border.save(output_puzzle)
    
    return puzzle_y


def main():
    """
    Generate a CAPTCHA image and display it.
    """
    y_coordinate = generate_realistic_slider_captcha()
    print(f"Y-coordinate for validation: {y_coordinate}")

if __name__ == '__main__':
    main()
