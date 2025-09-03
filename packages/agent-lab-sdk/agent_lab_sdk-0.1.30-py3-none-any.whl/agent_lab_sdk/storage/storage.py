import base64
import os
import mimetypes
from typing import Optional
from io import BytesIO
import requests

def store_file_in_sd_asset(filename: str, file_base64: str, folder: str = "giga-agents") -> Optional[str]:
    """
    Загружает файл в формате base64 в SD Asset API и возвращает URL загруженного файла.
    
    Args:
        file_base64: файл в формате base64
        folder: Название папки для загрузки
        
    Returns:
        URL загруженного файла или None в случае ошибки
    """
    # Декодируем base64 в бинарные данные
    try:
        file_data = base64.b64decode(file_base64.split(",")[-1])
    except Exception as e:
        print(f"Ошибка декодирования base64: {e}")
        return None
    
    # URL API
    url = "https://asset.tools.sberdevices.ru/api/file/upload"
    
    api_key = os.getenv("SD_ASSET_API_KEY")
    if not api_key:
        raise ValueError("SD_ASSET_API_KEY is missing")
    
    # Заголовки запроса
    headers = {
        "X-Api-Key": api_key
    }

    mimetype, _ = mimetypes.guess_type(filename)

    # Параметры формы
    files = {
        "files": (f"{filename}", BytesIO(file_data), mimetype)
    }
    
    # Дополнительные параметры
    data = {
        "folder": folder,
        "uniqueNames": "false",
        "removable": "true"
    }
    
    try:
        # Отправляем POST-запрос
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        
        # Получаем URL загруженного файла
        if response.status_code == 200 and response.json():
            return response.json()[0].replace('cdn-app.sberdevices.ru', 'cdn-app.giga.chat')
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")
    
    return None