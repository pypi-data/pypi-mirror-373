from cryptography.fernet import Fernet
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
import base64

load_dotenv()

FOLDER_STATUS_ENC_KEY = os.getenv("FOLDER_STATUS_ENC_KEY")


def generate_fernet_key():
    """
    Generates a valid Fernet key.
    """
    return Fernet.generate_key().decode()


def encrypt_timestamp(timestamp: datetime) -> str:
    """
    Encrypts a timestamp using Fernet encryption.

    :param timestamp: A datetime object to encrypt
    :return: An encrypted string
    """
    fernet = Fernet(FOLDER_STATUS_ENC_KEY.encode())
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
    enc_data = fernet.encrypt(f"timestamp:{timestamp_str}".encode()).decode()
    return enc_data


def decrypt_timestamp(enc_data: str) -> datetime:
    """
    Decrypts an encrypted timestamp string.

    :param enc_data: An encrypted string
    :return: A datetime object
    """
    fernet = Fernet(FOLDER_STATUS_ENC_KEY.encode())
    decrypted_data = fernet.decrypt(enc_data.encode()).decode()

    if not decrypted_data.startswith("timestamp:"):
        raise ValueError("Invalid encrypted data")

    timestamp_str = decrypted_data.split(":", 1)[1]
    taipei_tz = pytz.timezone("Asia/Taipei")
    return taipei_tz.localize(datetime.strptime(timestamp_str, "%Y%m%d%H%M%S"))


def get_current_timestamp() -> datetime:
    """
    Returns the current timestamp in Taipei timezone.

    :return: A datetime object representing the current time in Taipei timezone
    """
    return datetime.now(pytz.timezone("Asia/Taipei"))


def main():
    # 获取或生成 Fernet key
    key = generate_fernet_key()
    print(f"Fernet key: {key}")

    # 获取当前时间戳
    current_time = get_current_timestamp()
    print(f"Current timestamp: {current_time}")

    # 加密时间戳
    encrypted_time = encrypt_timestamp(current_time)
    print(f"Encrypted timestamp: {encrypted_time}")

    # 解密时间戳
    decrypted_time = decrypt_timestamp(encrypted_time)
    print(f"Decrypted timestamp: {decrypted_time}")

    # 验证解密后的时间戳是否与原始时间戳相同
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    decrypted_time_str = decrypted_time.strftime("%Y-%m-%d %H:%M:%S")
    assert (
        current_time_str == decrypted_time_str
    ), "Decrypted timestamp does not match the original"
    print("Encryption and decryption successful!")


if __name__ == "__main__":
    main()
