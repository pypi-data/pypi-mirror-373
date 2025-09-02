import os
import re
import logging
import cv2
import numpy as np
from PIL import Image
from PyPDF2 import PdfMerger

logger = logging.getLogger(__name__)

# Verhoeff Algorithm Tables
multiplication_table = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

permutation_table = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

inverse_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(aadhaar_number: str) -> bool:
    """Verhoeff checksum validation for Aadhaar-like numbers."""
    try:
        digits = [int(d) for d in str(aadhaar_number)][::-1]
        checksum = 0
        for i, digit in enumerate(digits):
            checksum = multiplication_table[checksum][permutation_table[i % 8][digit]]
        return checksum == 0
    except Exception:
        return False


def convert_document_lines_to_dicts(document_lines):
    """
    Convert Azure SDK DocumentLine objects to simple dicts:
    [{'content': str, 'polygon':[{'x':..,'y':..}, ...], 'spans':[{'offset':..,'length':..}, ...]}, ...]
    """
    result = []
    for line in document_lines:
        try:
            line_dict = {
                "content": str(line.content),
                "polygon": [{"x": int(p.x), "y": int(p.y)} for p in line.polygon],
                "spans": [{"offset": s.offset, "length": s.length} for s in line.spans]
            }
            result.append(line_dict)
        except Exception:
            # if SDK object shape differs, skip the line
            continue
    return result


def detect_goi_uidai_keywords(ocr_text):
    """
    Detect keyword presence ('Government of India' and 'UIDAI') inside OCR text list of dicts.
    """
    from .constants import AADHAR_KEYWORDS
    is_goi_present = False
    is_uidai_present = False
    for item in ocr_text:
        content = item.get("content", "").lower()
        if AADHAR_KEYWORDS.GOI in content:
            is_goi_present = True
        if AADHAR_KEYWORDS.UIDAI in content:
            is_uidai_present = True
        if is_goi_present and is_uidai_present:
            break
    return is_goi_present, is_uidai_present


def extract_valid_aadhaars(ocr_text):
    """
    Extract valid Aadhaar objects (dict entries) from OCR text list using regex and Verhoeff.
    Returns (valid_aadhaars_list, forged_present_bool)
    """
    aadhaar_pattern = re.compile(r"\d{12}")
    aadhaar_pattern_2 = re.compile(r"[2-9]\d{11}")

    valid = []
    forged_present = False

    for item in ocr_text:
        text = item.get("content", "")
        digits = re.sub(r"\D", "", text)
        if not digits:
            continue
        if aadhaar_pattern.fullmatch(digits):
            if aadhaar_pattern_2.fullmatch(digits) and validate_verhoeff(digits):
                valid.append(item)
            else:
                # looks like aadhaar-like but invalid
                forged_present = True

    logger.info(f"Valid Aadhaar entries found: {len(valid)}")
    return valid, forged_present


def mask_partial_text(image_path: str, ocr_response, mask_length_ratio: float = 0.67) -> str:
    """
    Mask left portion (~8/12) of Aadhaar number polygon areas on image.
    Returns path to masked image (or original path if saving fails).
    """
    logger.info(f"Masking image {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not open image: {image_path}")

    if not ocr_response:
        return image_path

    for item in ocr_response:
        try:
            poly = item.get("polygon")
            if not poly or len(poly) < 4:
                continue
            pts = np.array([(p["x"], p["y"]) for p in poly], np.int32)
            x_min = int(pts[:, 0].min())
            x_max = int(pts[:, 0].max())
            y_min = int(pts[:, 1].min())
            y_max = int(pts[:, 1].max())
            text_width = x_max - x_min
            mask_width = int(text_width * mask_length_ratio)
            if mask_width <= 0:
                continue
            partial_pts = np.array([
                [x_min, y_min],
                [x_min + mask_width, y_min],
                [x_min + mask_width, y_max],
                [x_min, y_max]
            ], np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(image, [partial_pts], (0, 0, 0))
        except Exception:
            logger.exception("Error masking one polygon; continuing")
            continue

    base, ext = os.path.splitext(image_path)
    out_path = f"{base}_Masked{ext}"
    try:
        cv2.imwrite(out_path, image)
        return out_path
    except Exception:
        logger.exception("Failed to save masked image; returning original")
        return image_path


def convert_image_to_pdf(image_path: str) -> str:
    """Convert single image to a temporary single-page PDF and return its path."""
    image = Image.open(image_path).convert("RGB")
    temp_pdf_path = os.path.splitext(image_path)[0] + ".pdf"
    image.save(temp_pdf_path, "PDF")
    return temp_pdf_path


def combine_images_to_pdf(image_paths, output_pdf_path):
    """
    Combine image files into single PDF file at output_pdf_path.
    This creates temporary PDFs per image then merges them.
    """
    temp_pdf_paths = []
    for p in image_paths:
        temp_pdf_paths.append(convert_image_to_pdf(p))

    merger = PdfMerger()
    try:
        for t in temp_pdf_paths:
            merger.append(t)
        merger.write(output_pdf_path)
    finally:
        try:
            merger.close()
        except Exception:
            pass
        # cleanup temp pdfs
        for t in temp_pdf_paths:
            try:
                os.remove(t)
            except Exception:
                pass
    return output_pdf_path
