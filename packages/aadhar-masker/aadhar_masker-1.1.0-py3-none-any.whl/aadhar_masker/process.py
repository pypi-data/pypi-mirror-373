import os
import logging
import time
from .azure_client import analyze_read
from .utils import convert_document_lines_to_dicts, extract_valid_aadhaars, mask_partial_text, combine_images_to_pdf

logger = logging.getLogger(__name__)

def process_images(image_paths, azure_url: str, azure_key: str, original_file_name: str, output_folder: str):
    """
    Processes a list of image paths (pages for a single document), performs OCR,
    masks Aadhaar numbers, and writes a single masked PDF into output_folder/masked_aadhars.

    Args:
        image_paths (list): list of local image file paths (pages)
        azure_url (str): azure endpoint
        azure_key (str): azure key
        original_file_name (str): original filename (used to name masked pdf)
        output_folder (str): base folder where masked_aadhars will be created

    Returns:
        dict: { "noOfPages": int, "maskedPdfPath": str } or {"error": "..."}
    """
    masked_images_paths = []
    no_of_pages = len(image_paths)
    logger.info(f"Starting processing of {no_of_pages} pages for {original_file_name}")

    for img_path in image_paths:
        try:
            start = time.time()
            lines, angle = analyze_read(img_path, azure_key, azure_url)
            post_lines = convert_document_lines_to_dicts(lines)
            valid_aad, _ = extract_valid_aadhaars(post_lines)
            if valid_aad:
                masked_img = mask_partial_text(img_path, valid_aad)
                masked_images_paths.append(masked_img)
            else:
                # no aadhaar found: keep original image
                masked_images_paths.append(img_path)
            dur = time.time() - start
            logger.info(f"Processed {img_path} in {dur:.2f}s")
        except Exception as e:
            logger.exception(f"Error processing image {img_path}: {e}")
            # on error, fallback to original image (so combining still works)
            masked_images_paths.append(img_path)

    if not masked_images_paths:
        return {"error": "No images processed"}

    masked_folder = os.path.join(output_folder, "masked_aadhars")
    os.makedirs(masked_folder, exist_ok=True)

    final_pdf_name = os.path.splitext(original_file_name)[0] + "_masked.pdf"
    final_pdf_path = os.path.join(masked_folder, final_pdf_name)

    try:
        combine_images_to_pdf(masked_images_paths, final_pdf_path)
    except Exception as e:
        logger.exception(f"Failed to combine masked images into PDF: {e}")
        return {"error": f"Failed to create masked PDF: {e}"}

    logger.info(f"Final masked PDF created at: {final_pdf_path}")
    return {"noOfPages": no_of_pages, "maskedPdfPath": final_pdf_path}
