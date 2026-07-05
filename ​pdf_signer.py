import fitz
import os

def apply_signature_to_pdf(pdf_path: str, sig_path: str, out_path: str, coords: tuple, page_num: int = 0) -> bool:
    """Overlays transparent signature images onto specific coordinate spaces of a PDF layout via PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        if page_num >= len(doc):
            return False
            
        page = doc[page_num]
        # Map raw bounding boxes values tuples: (x1, y1, x2, y2)
        rect = fitz.Rect(coords[0], coords[1], coords[0] + 150, coords[1] + 75)
        
        page.insert_image(rect, filename=sig_path)
        doc.save(out_path)
        doc.close()
        return True
    except Exception:
        return False

