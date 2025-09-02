from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import fitz  # PyMuPDF
from PIL import Image
from googleapiclient.http import MediaIoBaseDownload

DEFAULT_DPI = 150


def pdf_page_to_image(file_id: str,
                      page: int,
                      dpi: int = DEFAULT_DPI,
                      scale: float = 1.0,
                      color: bool = True
                      ):
    current_dir = Path(__file__).parent.absolute()
    service_account_file = current_dir.parent / "keys" / "google_service_account_key.json"
    credentials = service_account.Credentials.from_service_account_file(
        str(service_account_file),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    try:
        # Get file metadata
        file = drive_service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_mime_type = file.get('mimeType')

        # Check if the file is a PDF
        if file_mime_type != 'application/pdf':
            raise ValueError("The requested file is not a PDF.")

        # Download the file content
        request = drive_service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        img_byte_arr = process_pdf_page(pdf_document, page, dpi, scale, color)
        return img_byte_arr
    except Exception as e:
        raise e


def process_pdf_page(pdf_document, page, dpi: int = DEFAULT_DPI,
                     scale: float = 1.0,
                     color: bool = True):
    # Check if the requested page exists
    if page < 1 or page > len(pdf_document):
        raise ValueError(f"Page {page} does not exist in this PDF. Total pages: {len(pdf_document)}")

    # Get the requested page
    pdf_page = pdf_document[page - 1]  # PyMuPDF uses 0-based indexing

    # Calculate the scaling matrix
    zoom = dpi / 72 * scale  # 72 is the default DPI
    matrix = fitz.Matrix(zoom, zoom)

    # Render page to an image with improved quality
    pix = pdf_page.get_pixmap(matrix=matrix, alpha=False)

    if color:
        mode = "RGB"
    else:
        mode = "L"
        pix = fitz.Pixmap(pix, 0) if pix.alpha else pix

    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

    # Apply antialiasing
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG', optimize=True)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
