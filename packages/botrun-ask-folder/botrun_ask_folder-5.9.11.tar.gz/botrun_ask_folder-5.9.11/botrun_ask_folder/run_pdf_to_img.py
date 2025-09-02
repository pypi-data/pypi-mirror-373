import os
import fitz
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from dataclasses import dataclass

from botrun_ask_folder.drive_download import append_export_extension_to_path, truncate_filename
from botrun_ask_folder.fast_api.util.pdf_util import process_pdf_page
from .emoji_progress_bar import EmojiProgressBar


@dataclass
class PDFInfo:
    path: str
    google_file_id: str
    total_pages: int

    def __hash__(self):
        return hash((self.path, self.google_file_id))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.path == other.path and self.google_file_id == other.google_file_id
    @property
    def filename(self):
        return os.path.basename(self.path)

def load_pdf_to_img_metadata(metadata_file: str) -> Dict[str, str]:
    import json
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    return {truncate_filename(append_export_extension_to_path(item['name'], item['mimeType'])): item['id'] for item in metadata.get('items', [])}


def get_pdf_files(data_folder: str, metadata: Dict[str, str]) -> List[PDFInfo]:
    pdf_files = []
    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                google_file_id = metadata.get(file)
                if google_file_id:
                    with fitz.open(pdf_path) as pdf_document:
                        total_pages = len(pdf_document)
                    pdf_files.append(PDFInfo(pdf_path, google_file_id, total_pages))
    return pdf_files


def process_page(args: Tuple[PDFInfo, int, str, bool, int, float, bool]) -> Tuple[PDFInfo, int]:
    pdf_info, page_number, output_folder, force, dpi, scale, color = args
    img_path = os.path.join(output_folder, f"{pdf_info.google_file_id}_{page_number}.png")

    if not force and os.path.exists(img_path):
        return pdf_info, page_number

    with fitz.open(pdf_info.path) as pdf_document:
        img_byte_arr = process_pdf_page(pdf_document, page_number, dpi=dpi, scale=scale, color=color)

    with open(img_path, "wb") as img_file:
        img_file.write(img_byte_arr)

    return pdf_info, page_number


def run_pdf_to_img(google_drive_folder_id: str, force: bool = False):
    data_folder = f"./data/{google_drive_folder_id}"
    metadata_file = os.path.join(data_folder, f"{google_drive_folder_id}-metadata.json")
    output_folder = f"{data_folder}/img"
    os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(data_folder):
        raise FileNotFoundError(f"Data folder for Google Drive folder ID {google_drive_folder_id} does not exist.")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file for Google Drive folder ID {google_drive_folder_id} does not exist.")

    metadata = load_pdf_to_img_metadata(metadata_file)
    pdf_files = get_pdf_files(data_folder, metadata)

    # Set up progress bars for each PDF
    progress_bars = {}
    for pdf_info in pdf_files:
        progress_bar = EmojiProgressBar(pdf_info.total_pages)
        progress_bar.set_description(f"Processing {pdf_info.filename}")
        progress_bars[pdf_info] = progress_bar

    # Create a list of all pages to process
    all_pages = [(pdf_info, page_number, output_folder, force, 300, 1.0, True)
                 for pdf_info in pdf_files
                 for page_number in range(1, pdf_info.total_pages + 1)]

    total_pages = sum(pdf_info.total_pages for pdf_info in pdf_files)
    print(f"Processing {len(pdf_files)} PDFs with a total of {total_pages} pages")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_page, args) for args in all_pages]

        for future in as_completed(futures):
            pdf_info, page_number = future.result()
            progress_bars[pdf_info].update(page_number)

    print("All PDFs processed successfully")

if __name__ == "__main__":
    run_pdf_to_img("your_google_drive_folder_id_here")
