import pytesseract.pytesseract
import json
import os


paths = ['C:\\', 'D:\\', 'E:\\']


def setup_tesseract(search_paths=['C:\\'], config_file='tesseract_config.json'):
    def load_tesseract_path():
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = json.load(file)
                tesseract_path = config.get('tesseract_path')
                if tesseract_path and os.path.exists(tesseract_path):
                    return tesseract_path
        return None

    def save_tesseract_path(tesseract_path):
        with open(config_file, 'w') as file:
            json.dump({'tesseract_path': tesseract_path}, file, indent=2)

    tesseract_path = load_tesseract_path()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        return tesseract_path

    for path in search_paths:
        try:
            for root, dirs, files in os.walk(path):
                if 'tesseract.exe' in files:
                    tesseract_path = os.path.join(root, 'tesseract.exe')
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                    save_tesseract_path(tesseract_path)
                    return tesseract_path
        except (FileNotFoundError, PermissionError):
            continue

    raise TesseractFileNotFoundError

class TesseractFileNotFoundError(FileNotFoundError):
    pass