from typing import Optional

import requests
import logging
import os
import threading
import urllib.parse
import json
import random
import time
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Путь к файлу токена (можно переопределить через ENV)
TOKEN_PROVIDER_AGW_URL = os.environ.get("TOKEN_PROVIDER_AGW_URL", "https://agent-gateway.apps.advosd.sberdevices.ru")
# Максимальное число попыток получения токена (по умолчанию 3, можно переопределить через ENV)
TOKEN_PROVIDER_AGW_DEFAULT_MAX_RETRIES = int(os.environ.get("TOKEN_PROVIDER_AGW_DEFAULT_MAX_RETRIES", 3))
# Таймаут ожидания ответа agw в секундах
TOKEN_PROVIDER_AGW_TIMEOUT_SEC = int(os.environ.get("TOKEN_PROVIDER_AGW_TIMEOUT_SEC", 5))
# Случайная задержка между повторными попытками: от 1 до 5 секунд
BACKOFF_MIN = 1
BACKOFF_MAX = 5
# Случайный порог обновления токена: от 0 до 300 секунд (5 минут)
REFRESH_WINDOW_MAX = 300

class AgwTokenManager:
    # Лок для синхронизации между потоками в одном процессе
    _thread_lock = threading.Lock()
    _tokens: dict[str, any] = {}

    @staticmethod
    def _get_new_token(provider: str, token_type: Optional[str] = None) -> dict[str, any]:
        req_url = urllib.parse.urljoin(TOKEN_PROVIDER_AGW_URL, "/tokens")
        params = {"provider": provider}
        if token_type:
            params["type"] = token_type
        
        max_retries = TOKEN_PROVIDER_AGW_DEFAULT_MAX_RETRIES
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Попытка получения токена из AGW ({attempt}/{max_retries})...")
                resp = requests.post(req_url, params=params, data={}, verify=False, timeout=TOKEN_PROVIDER_AGW_TIMEOUT_SEC)
                resp.raise_for_status()
                result = resp.json()

                token = result.get("token")
                expires_in = result.get("expiresIn")

                if not token or not expires_in:
                    raise ValueError(f"Неверный ответ API: {resp.text}")

                expiry_time = datetime.fromtimestamp(expires_in, tz=timezone.utc) - timedelta(seconds=60)
                logger.info("Успешно получили токен, действует до %s", expiry_time.isoformat())
                return {
                    "token": token,
                    "expiry_ts": expires_in
                }

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
    def get_token(cls, provider: str, token_type: Optional[str] = None) -> str:
        """
        Возвращает валидный токен, обновляя его при необходимости.
        """
        key = "{}_{}".format(provider, token_type if token_type is not None else "default")
        # Лок между потоками
        with cls._thread_lock:
            by_provider = cls._tokens.get(key)
            if by_provider:
                token = by_provider.get("token")
                expiry_ts = by_provider.get("expiry_ts")
                now = datetime.now(timezone.utc)

                if token and expiry_ts:
                    expiry_time = datetime.fromtimestamp(expiry_ts, tz=timezone.utc)
                    refresh_window = timedelta(seconds=random.uniform(0, REFRESH_WINDOW_MAX))
                    time_left = expiry_time - now
                    logger.debug("Осталось времени: %s, порог обновления: %s", time_left, refresh_window)
                    if time_left > refresh_window:
                        logger.debug("Используем кэшированный токен; истекает %s", expiry_time.isoformat())
                        return token


            # Иначе — запрашиваем новый токен
            new_token = cls._get_new_token(provider, token_type)
            cls._tokens[key] = new_token
            return new_token.get("token")
