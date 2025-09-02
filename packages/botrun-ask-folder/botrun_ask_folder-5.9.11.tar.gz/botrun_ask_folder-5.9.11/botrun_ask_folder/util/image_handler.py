import base64
import os
from PIL import Image
import io


class ExceedImageLimitException(Exception):
    def __init__(self):
        self.message = ""
        super().__init__(self.message)


class ProcessImageException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def handle_image_encode(file_path: str, file_mime: str) -> str | None:
    # Check file size
    file_size = os.path.getsize(file_path)
    max_size = 5 * 1024 * 1024  # 5MB in bytes

    if file_size > max_size:
        try:
            with Image.open(file_path) as img:
                # Convert to JPG if not already
                if img.format != "JPEG":
                    img = img.convert("RGB")

                # Resize if width is greater than 1920
                if img.width > 1920:
                    ratio = 1920 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1920, new_height), Image.LANCZOS)

                # Save to a BytesIO object
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                buffer.seek(0)

                # Check new file size
                new_file_size = buffer.getbuffer().nbytes
                if new_file_size > max_size:
                    raise ExceedImageLimitException()

                return "image/jpeg", base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            raise ProcessImageException(str(e))

    # If file size is already under 5MB, process as before
    return file_mime, encode_image(file_path)
