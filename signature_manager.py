import os
from PIL import Image

def process_transparent_signature(input_path: str, output_path: str) -> bool:
    """Isolates dark ink structures and converts off-white backgrounds into alpha channels."""
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            datas = img.getdata()
            
            new_data = []
            for item in datas:
                # If pixel is near-white threshold, drop alpha channel color boundary maps
                if item[0] > 200 and item[1] > 200 and item[2] > 200:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
                    
            img.putdata(new_data)
            img.save(output_path, "PNG")
            return True
    except Exception:
        return False

