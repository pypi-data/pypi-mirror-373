import os
import uuid
import shutil
import fitz
import logging
import tempfile
from typing import Dict, Any, List
from .process import process_images

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def aadhar_masking_from_folder(folder_path: str, azure_url: str, azure_key: str) -> Dict[str, Any]:
    """
    Public entry point. Processes all files in `folder_path`. For each file:
      - if image: send single image (as list) to process_images
      - if pdf: convert pages to images, then send images to process_images
    Each final masked PDF will be saved in: <folder_path>/masked_aadhars/
    The function processes files sequentially (one file at a time).

    Returns:
        {
          "masked_folder": "<folder_path>/masked_aadhars",
          "results": [{"file": "orig.pdf", "maskedPdfPath": "..."}, ...],
          "errors": [{"file":"bad.pdf", "error":"..."}]
        }
    """
    if not os.path.isdir(folder_path):
        return {"error": f"Provided folder_path does not exist or is not a directory: {folder_path}"}

    request_uuid = uuid.uuid4().hex

    # Use system-independent temp directory
    base_tmp_dir = tempfile.gettempdir()
    temp_dir = os.path.join(base_tmp_dir, request_uuid)

    # Create the directory
    os.makedirs(temp_dir, exist_ok=True)

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    try:
        entries = os.listdir(folder_path)
        if not entries:
            return {"error": "Provided folder is empty"}

        for file_name in entries:
            file_path = os.path.join(folder_path, file_name)

            # skip masked_aadhars folder if already present
            if os.path.isdir(file_path) and os.path.basename(file_path) == "masked_aadhars":
                continue
            if not os.path.isfile(file_path):
                continue

            ext = os.path.splitext(file_name)[1].lower()
            image_paths = []

            try:
                if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
                    # copy to temp and process single image
                    dest = os.path.join(temp_dir, file_name)
                    shutil.copy(file_path, dest)
                    image_paths.append(dest)

                elif ext == ".pdf":
                    # convert each pdf page to image and store in temp_dir
                    pdf = fitz.open(file_path)
                    for p in range(len(pdf)):
                        page = pdf[p]
                        pix = page.get_pixmap()
                        img_name = f"{os.path.splitext(file_name)[0]}_page_{p+1}.png"
                        img_path = os.path.join(temp_dir, img_name)
                        pix.save(img_path)
                        image_paths.append(img_path)
                    pdf.close()
                else:
                    logger.warning(f"Skipping unsupported file {file_name}")
                    continue

                if not image_paths:
                    logger.warning(f"No images extracted for {file_name}, skipping")
                    continue

                # process this document (list of image paths -> masked pdf)
                resp = process_images(
                    image_paths=image_paths,
                    azure_url=azure_url,
                    azure_key=azure_key,
                    original_file_name=file_name,
                    output_folder=folder_path
                )

                if resp.get("error"):
                    errors.append({"file": file_name, "error": resp.get("error")})
                else:
                    results.append({"file": file_name, "maskedPdfPath": resp.get("maskedPdfPath")})

            except Exception as e:
                logger.exception(f"Error processing {file_name}: {e}")
                errors.append({"file": file_name, "error": str(e)})

            finally:
                # cleanup temp images for this file (but do not remove temp_dir entirely until end)
                for p in image_paths:
                    try:
                        if os.path.exists(p):
                            os.remove(p)
                    except Exception:
                        pass

        masked_folder = os.path.join(folder_path, "masked_aadhars")
        return {"masked_folder": masked_folder, "results": results, "errors": errors}

    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
