import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt_file(file_path, key):
    backend = default_backend()
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    key = kdf.derive(key)

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    padder = padding.PKCS7(128).padder()
    plaintext_padded = padder.update(plaintext) + padder.finalize()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()

    return (salt + iv + ciphertext, key)

def copy_encrypt_all_files(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    key = secrets.token_bytes(32)
    encrypted_files = []
    for root, dirs, files in os.walk(src_folder):
        for filename in files:
            src_path = os.path.join(root, filename)
            encrypted_file, key = encrypt_file(src_path, key)
            encrypted_files.append((filename, encrypted_file))

            relative_dest_path = os.path.relpath(src_path, src_folder)
            dest_path = os.path.join(dest_folder, relative_dest_path)
            dest_dir = os.path.dirname(dest_path)

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            with open(dest_path, 'wb') as f:
                f.write(encrypted_file)
    with open(os.path.join(dest_folder, 'key.txt'), 'wb') as f:
        f.write(key)

if __name__ == '__main__':
    use_default_folders = input("Would you like to use the default folders (C:/ and flash drive user folder)? (yes/no)")
    if use_default_folders.lower() == 'yes':
        src_folder = "C:/"
        dest_folder = os.path.join(os.path.expanduser('~'), "flash_drive_user_folder")
    else:
        src_folder = input("Enter the path of the source folder: ")
        dest_folder = input("Enter the path of the destination folder:")
    copy_encrypt_all_files(src_folder, dest_folder)
