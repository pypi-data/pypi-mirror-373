import os
import json
import logging
import logging
import uuid
import requests
import fcntl
import random
import time
import base64
import threading
from datetime import datetime, timedelta, timezone
from .agw_token_manager import AgwTokenManager
import urllib3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Путь к файлу токена (можно переопределить через ENV)
TOKEN_FILE_PATH = os.environ.get("GIGACHAT_TOKEN_PATH", "/tmp/gigachat_token.json")
USE_TOKEN_PROVIDER_AGW = os.environ.get("USE_TOKEN_PROVIDER_AGW", 'False').lower() in ('true', '1', 't')

# Максимальное число попыток получения токена (по умолчанию 3, можно переопределить через ENV)
DEFAULT_MAX_RETRIES = int(os.environ.get("GIGACHAT_TOKEN_FETCH_RETRIES", 3))
# Случайная задержка между повторными попытками: от 1 до 5 секунд
BACKOFF_MIN = 1
BACKOFF_MAX = 5
# Случайный порог обновления токена: от 0 до 300 секунд (5 минут)
REFRESH_WINDOW_MAX = 300

class GigaChatTokenManager:
    # Лок для синхронизации между потоками в одном процессе
    _thread_lock = threading.Lock()

    @staticmethod
    def _get_new_token():
        """Запрашивает новый токен у GigaChat API с retry и случайной задержкой."""
        if os.getenv("USE_GIGACHAT_ADVANCED", 'False').lower() in ('true', '1', 't'):
            url = os.environ.get("GIGACHAT_BASE_URL") + "token"
            data = None
        else:
            gigachat_scope = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
            url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
            data = {"scope": gigachat_scope}

        gigachat_credentials = os.environ.get("GIGACHAT_CREDENTIALS")
        if not gigachat_credentials:
            user = os.getenv("GIGACHAT_USER")
            password = os.getenv("GIGACHAT_PASSWORD")
            if user and password:
                gigachat_credentials = base64.b64encode(f"{user}:{password}".encode()).decode()
        if not gigachat_credentials:
            raise ValueError("Переменная окружения GIGACHAT_CREDENTIALS (или GIGACHAT_USER в комбинации с GIGACHAT_PASSWORD) не установлена.")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "agent-toolkit",
            "RqUID": str(uuid.uuid4()),  # Уникальный идентификатор запроса
            "Authorization": f"Basic {gigachat_credentials}"
        }

        max_retries = DEFAULT_MAX_RETRIES
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Попытка получения токена GigaChat ({attempt}/{max_retries})...")
                resp = requests.post(url, headers=headers, data=data, verify=False)
                resp.raise_for_status()
                result = resp.json()

                token = result.get("access_token")
                if not token:
                    token = result.get("tok")
                expires_at = result.get("expires_at")
                if not expires_at:
                    expires_at = result.get("exp") * 1000
                if not token or not expires_at:
                    raise ValueError(f"Неверный ответ API: {resp.text}")

                # expires_at в миллисекундах
                expiry_time = datetime.fromtimestamp(expires_at / 1000, tz=timezone.utc) - timedelta(seconds=60)
                logger.info("Успешно получили токен, действует до %s", expiry_time.isoformat())
                return token, expiry_time

            except (Exception, requests.RequestException, ValueError, json.JSONDecodeError) as e:
                logger.error("Ошибка при попытке %d: %s", attempt, e)
                if attempt < max_retries:
                    delay = random.uniform(BACKOFF_MIN, BACKOFF_MAX)
                    logger.info("Повтор через %.2f сек...", delay)
                    time.sleep(delay)
                else:
                    logger.error("Все %d попыток получения токена провалены.", max_retries)
                    raise

    @classmethod
    def get_token(cls) -> str:
        """
        Возвращает валидный токен, обновляя его при необходимости.
        Использует межпроцессную блокировку (fcntl.flock) и лок для потоков,
        чтобы избежать дублирующих запросов.
        """
        if USE_TOKEN_PROVIDER_AGW:
            provider = "GIGACHAT-ADVANCED" if os.getenv("USE_GIGACHAT_ADVANCED", 'False').lower() in ('true', '1', 't') else "GIGACHAT"
            return AgwTokenManager.get_token(provider=provider)
        
        # Лок между потоками
        with cls._thread_lock:
            # Гарантируем существование директории под файл токена
            dirpath = os.path.dirname(TOKEN_FILE_PATH)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)

            # Открываем (или создаем) файл токена
            with open(TOKEN_FILE_PATH, "a+", encoding="utf-8") as f:
                # Межпроцессная блокировка файла
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    # Читаем существующие данные
                    f.seek(0)
                    try:
                        data = json.load(f)
                    except (json.JSONDecodeError, IOError):
                        data = {}

                    token = data.get("token")
                    expiry_ts = data.get("expiry_timestamp")
                    now = datetime.now(timezone.utc)

                    # Если токен есть и не истекает раньше случайного порога — возвращаем его
                    if token and expiry_ts:
                        expiry_time = datetime.fromtimestamp(expiry_ts, tz=timezone.utc)
                        # генерируем случайный порог в секундах до истечения (0–300)
                        refresh_window = timedelta(seconds=random.uniform(0, REFRESH_WINDOW_MAX))
                        time_left = expiry_time - now
                        logger.debug("Осталось времени: %s, порог обновления: %s", time_left, refresh_window)
                        if time_left > refresh_window:
                            logger.debug("Используем кэшированный токен; истекает %s", expiry_time.isoformat())
                            return token

                    # Иначе — запрашиваем новый токен
                    new_token, new_expiry = cls._get_new_token()

                    # Сохраняем новый токен
                    f.seek(0)
                    f.truncate()
                    json.dump({
                        "token": new_token,
                        "expiry_timestamp": new_expiry.timestamp()
                    }, f)
                    f.flush()
                    logger.debug("Новый токен сохранен в %s", TOKEN_FILE_PATH)
                    return new_token

                finally:
                    # Снимаем межпроцессную блокировку
                    fcntl.flock(f, fcntl.LOCK_UN)

# Примечание: fcntl.flock обеспечивает межпроцессную блокировку,
# а threading.Lock — синхронизацию между потоками в одном процессе.
