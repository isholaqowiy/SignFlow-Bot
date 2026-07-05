import os
from PIL import Image

def apply_signature_to_image(img_path: str, sig_path: str, out_path: str, position: tuple) -> bool:
    """Pastes transparent signature alpha masks cleanly over an image canvas."""
    try:
        with Image.open(img_path) as base_img:
            with Image.open(sig_path) as sig_img:
                base_img = base_img.convert("RGBA")
                sig_img = sig_img.convert("RGBA")
                
                # Dynamic adaptive scaling resizing down layer
                sig_img.thumbnail((200, 100))
                
                base_img.paste(sig_img, position, sig_img)
                base_img.save(out_path, "PNG")
                return True
    except Exception:
        return False

