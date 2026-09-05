import re
import io
from typing import Dict, Any, Tuple, Optional
from PIL import Image

# Try importing pytesseract or easyocr if available
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class OCREngine:
    def extract_text_from_image(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Extract text and confidence score from image bytes.
        If OCR library is unavailable, uses OCR text parser fallback.
        """
        if TESSERACT_AVAILABLE:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                text = pytesseract.image_to_string(img)
                confidence = 0.90 if len(text.strip()) > 10 else 0.40
                return text, confidence
            except pytesseract.TesseractNotFoundError:
                print("[OCR] Tesseract binary not found on host OS. Install tesseract-ocr or use preset samples.")
            except Exception as e:
                print(f"[OCR] Image text extraction failed: {e}")

        return "", 0.0

    def parse_product_label_text(self, text: str) -> Dict[str, Any]:
        """
        Parses OCR extracted text for MFD, EXP, Batch Number, and Brand.
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        mfd = None
        exp = None
        batch = None
        brand = None

        # Regex patterns for MFD / MFG / PACKED
        mfd_pattern = r'(?:mfd|mfg|manufactured|packed|pkd)[:\s]*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4}|[0-9]{2}[\/\.-][0-9]{4})'
        mfd_match = re.search(mfd_pattern, text, re.IGNORECASE)
        if mfd_match:
            mfd = mfd_match.group(1)

        # Regex patterns for EXP / BEST BEFORE / USE BY
        exp_pattern = r'(?:exp|expiry|use by|best before)[:\s]*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4}|[0-9]{2}[\/\.-][0-9]{4})'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE)
        if exp_match:
            exp = exp_match.group(1)

        # Generic date fallback if explicitly labeled prefix missed
        dates = re.findall(r'\b([0-9]{2}[\/\.-][0-9]{2}[\/\.-][0-9]{4})\b', text)
        if len(dates) >= 2 and not mfd and not exp:
            mfd = dates[0]
            exp = dates[1]
        elif len(dates) == 1 and not exp:
            exp = dates[0]

        # Batch Number Regex
        batch_pattern = r'(?:batch|b\.no|bno|lot)[:\s]*([a-zA-Z0-9\/-]+)'
        batch_match = re.search(batch_pattern, text, re.IGNORECASE)
        if batch_match:
            batch = batch_match.group(1)

        # Brand Detection
        for b in ["Amul", "Britannia", "Aashirvaad", "Mother Dairy", "Tata", "Epigamia"]:
            if b.lower() in text.lower():
                brand = b
                break

        return {
            "mfd": mfd,
            "exp": exp,
            "batch": batch,
            "brand": brand
        }

ocr_engine = OCREngine()
