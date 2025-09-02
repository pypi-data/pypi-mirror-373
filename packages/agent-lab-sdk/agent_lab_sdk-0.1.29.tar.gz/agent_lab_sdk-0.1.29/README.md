# Agent Lab SDK

Набор утилит и обёрток для упрощённой работы с LLM, Agent Gateway и метриками в проектах Giga Labs.

## Установка

```bash
pip install agent_lab_sdk
```

## Список изменений

Ознакомиться со списком изменений между версиями agent-lab-sdk можно по [ссылке](/CHANGELOG.md)

## Содержание

1. [Модуль `agent_lab_sdk.llm`](#1-модуль-agent_lab_sdkllm)
2. [Модуль `agent_lab_sdk.llm.throttled`](#2-модуль-agent_lab_sdkllmthrottled)
3. [Модуль `agent_lab_sdk.metrics`](#3-модуль-agent_lab_sdkmetrics)
4. [Хранилище](#4-хранилище)
5. [Схема](#5-схема)
6. [Сборка и публикация](#6-сборка-и-публикация)

---

## 1. Модуль `agent_lab_sdk.llm`

### 1.1. Получение модели

```python
from agent_lab_sdk.llm import get_model

# Использует токен из окружения по умолчанию
model = get_model()

# Получить модель GigaChat, использует токен из окружения по умолчанию
model = get_model("chat")

# Получить модель ThrottledGigaChat, использует токен из окружения по умолчанию
model = get_model("chat", throttled=True)

# Получить модель EmbeddingsGigaChat, использует токен из окружения по умолчанию
model = get_model("embeddings")

# Получить модель ThrottledEmbeddingsGigaChat, использует токен из окружения по умолчанию
model = get_model("embeddings", throttled=True)

# Передача явных параметров GigaChat, токен из окружения не использует
model = get_model(
    access_token="YOUR_TOKEN",
    timeout=60,
    scope="GIGACHAT_API_CORP"
)
```

> если не передавать access_token, токен будет выбран через GigaChatTokenManager

> указание флага throttled=True включает ограничения и метрики для GigaChat и GigaChatEmbeddings. Подробнее [здесь](#2-модуль-agent_lab_sdkllmthrottled)

### 1.2. Менеджеры токенов

| Класс                  | Описание                                                                                | Пример использования                            |
| ---------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `AgwTokenManager`      | Кеширование + получение токена через Agent Gateway                                      | `token = AgwTokenManager.get_token("provider")` |
| `GigaChatTokenManager` | Кеширование + получение через GigaChat OAuth с использованием пользовательских секретов | `token = GigaChatTokenManager.get_token()`      |

### 1.3. Переменные окружения

| Переменная                               | Описание                                                 | Значение по умолчанию / Пример                      |
| ---------------------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| `GIGACHAT_SCOPE`                         | Scope GigaChat API                               | `GIGACHAT_API_PERS`                                 |
| `GIGACHAT_TIMEOUT`                | Таймаут запросов к GigaChat (секунды)                    | `120`                                               |
| `USE_TOKEN_PROVIDER_AGW`                 | Использовать `AgwTokenManager` для получения токена GigaChat                          | `true`                                              |
| `GIGACHAT_CREDENTIALS`                   | Базовые креды для GigaChat (`b64(clientId:secretId)`)    | `Y2xpZW50SWQ6c2VjcmV0SWQ=`                          |
| `GIGACHAT_USER`                   | Имя пользователя GigaChat advanced    | `user`                          |
| `GIGACHAT_PASSWORD`                   | Пароль пользователя GigaChat advanced)    | `password`                          |
| `GIGACHAT_TOKEN_PATH`                    | Путь к файлу кеша токена GigaChat                        | `/tmp/gigachat_token.json`                          |
| `GIGACHAT_TOKEN_FETCH_RETRIES`           | Количество попыток получения токена (GigaChat)           | `3`                                                 |
| `USE_GIGACHAT_ADVANCED`                  | Включает запрос токена GigaChat API в продвинутом режиме | `true`                                              |
| `GIGACHAT_BASE_URL`                      | Базовый URL GigaChat (важно чтобы заканчивался на символ `/`)                                    | `https://gigachat.sberdevices.ru/v1/` |
| `TOKEN_PROVIDER_AGW_URL`                 | URL Agent Gateway для получения AGW-токена               | `https://agent-gateway.apps.advosd.sberdevices.ru`  |
| `TOKEN_PROVIDER_AGW_DEFAULT_MAX_RETRIES` | Макс. попыток запроса токена (AGW)                       | `3`                                                 |
| `TOKEN_PROVIDER_AGW_TIMEOUT_SEC`         | Таймаут запроса к AGW (секунды)                          | `5`                                                 |

---

## 2. Модуль `agent_lab_sdk.llm.throttled`

Позволяет ограничивать число одновременных вызовов к GigaChat и сервису эмбеддингов, автоматически собирая соответствующие метрики.

```python
from agent_lab_sdk.llm import GigaChatTokenManager
from agent_lab_sdk.llm.throttled import ThrottledGigaChat, ThrottledGigaChatEmbeddings

access_token = GigaChatTokenManager.get_token()

# Чат с учётом ограничений
chat = ThrottledGigaChat(access_token=access_token)
response = chat.invoke("Привет!")

# Эмбеддинги с учётом ограничений
emb = ThrottledGigaChatEmbeddings(access_token=access_token)
vectors = emb.embed_documents(["Text1", "Text2"])
```

### 2.1. Переменные окружения для ограничения

| Переменная                        | Описание                                    | Значение по умолчанию |
| --------------------------------- | ------------------------------------------- | --------------------- |
| `MAX_CHAT_CONCURRENCY`            | Максимум одновременных чат-запросов         | `100000`              |
| `MAX_EMBED_CONCURRENCY`           | Максимум одновременных запросов эмбеддингов | `100000`              |
| `EMBEDDINGS_MAX_BATCH_SIZE_PARTS` | Макс. размер батча частей для эмбеддингов   | `90`                  |

### 2.2. Метрики

Метрики доступны через `agent_lab_sdk.metrics.get_metric`:

| Метрика                   | Описание                                       | Тип       |
| ------------------------- | ---------------------------------------------- | --------- |
| `chat_slots_in_use`       | Число занятых слотов для чата                  | Gauge     |
| `chat_waiting_tasks`      | Число задач, ожидающих освобождения слота чата | Gauge     |
| `chat_wait_time_seconds`  | Время ожидания слота чата (секунды)            | Histogram |
| `embed_slots_in_use`      | Число занятых слотов для эмбеддингов           | Gauge     |
| `embed_waiting_tasks`     | Число задач, ожидающих слота эмбеддингов       | Gauge     |
| `embed_wait_time_seconds` | Время ожидания слота эмбеддингов (секунды)     | Histogram |

---

## 3. Модуль `agent_lab_sdk.metrics`

Предоставляет удобный интерфейс для создания и управления метриками через Prometheus-клиент.

### 3.1. Основные функции

```python
from agent_lab_sdk.metrics import get_metric

# Создать метрику
g = get_metric(
    metric_type="gauge",               # тип: "gauge", "counter" или "histogram"
    name="my_gauge",                   # имя метрики в Prometheus
    documentation="Моя метрика gauge"  # описание
)

# Увеличить счётчик
g.inc()

# Установить конкретное значение
g.set(42)
```

### 3.2. Пример использования в коде

```python
from agent_lab_sdk.metrics import get_metric
import time

# Счётчик HTTP-запросов с метками
reqs = get_metric(
    metric_type="counter",
    name="http_requests_total",
    documentation="Всего HTTP-запросов",
    labelnames=["method", "endpoint"]
)
reqs.labels("GET", "/api").inc()

# Гистограмма задержек
lat = get_metric(
    metric_type="histogram",
    name="http_request_latency_seconds",
    documentation="Длительность HTTP-запроса",
    buckets=[0.1, 0.5, 1.0, 5.0]
)
with lat.time():
    time.sleep(0.5)

print(reqs.collect())
print(lat.collect())
```

## 4. Хранилище

### 4.1 SD Ассетница

функция `store_file_in_sd_asset` сохраняет base64‑файл в хранилище S3 и отдаёт публичную ссылку на файл

```python
from agent_lab_sdk.storage import store_file_in_sd_asset

store_file_in_storage("my-agent-name-filename.png", file_b64, "giga-agents")
```

### 4.2 AGW Checkpointer

AGW поддерживает langgraph checkpoint API и в SDK представлен `AsyncAGWCheckpointSaver`, который позволяет сохранять состояние графа в AGW напрямую. 

## 5. Схема

### 5.1. Типы входных данных

Модуль `agent_lab_sdk.schema.input_types` предоставляет фабричные функции для создания аннотированных типов полей, которые могут использоваться в Pydantic моделях для описания интерфейса агентов.

#### Основные типы полей

```python
from typing import List, Annotated
from pydantic import BaseModel, Field
from agent_lab_sdk.schema import (
    MainInput, StringInput, StringArrayInput, NumberInput,
    SelectInput, CheckboxInput, FileInput, FilesInput, SelectOption
)

class AgentState(BaseModel):
    # Основное поле ввода
    query: Annotated[str, MainInput(placeholder="Введите ваш запрос")]
    
    # Строковое поле
    title: Annotated[str, StringInput(
        default="Без названия",
        title="Заголовок",
        description="Название для вашего запроса"
    )]
    
    # Массив строк
    keywords: Annotated[List[str], StringArrayInput(
        placeholder="Добавьте ключевые слова...",
        title="Ключевые слова",
        description="Список ключевых слов для поиска",
        group="Параметры"
    )]
    
    # Числовое поле
    temperature: Annotated[float, NumberInput(
        default=0.7,
        title="Температура",
        description="Параметр креативности модели (0.0 - 1.0)",
        hidden=True
    )]
    
    # Выпадающий список
    mode: Annotated[str, SelectInput(
        title="Режим работы",
        items=[
            SelectOption(label="Быстрый", value="fast").model_dump(),
            SelectOption(label="Точный", value="precise").model_dump()
        ],
        default="fast",
        group="Настройки"
    )]
    
    # Чекбокс
    save_history: Annotated[bool, CheckboxInput(
        title="Сохранять историю",
        description="Сохранять диалог для последующего анализа",
        default=True,
        group="Опции"
    )]
    
    # Загрузка одного файла
    document: Annotated[str, FileInput(
        title="Документ",
        file_extensions=".pdf,.docx,.txt"
    )]
    
    # Загрузка нескольких файлов
    attachments: Annotated[List[str], FilesInput(
        title="Прикрепленные файлы",
        file_extensions=".pdf,.csv,.xlsx",
        group="Файлы"
    )]
```

#### Доступные фабричные функции

| Тип                      | Описание                          | Основные параметры                                                  |
|--------------------------|-----------------------------------|---------------------------------------------------------------------|
| `MainInput`              | Основное поле ввода               | `placeholder`                                                       |
| `StringInput`            | Текстовое поле                    | `default`, `title`, `description`, `hidden`, `depends`              |
| `StringArrayInput`       | Массив строк                      | `placeholder`, `title`, `description`, `group`, `hidden`, `depends` |
| `StringArrayInputInline` | Массив строк в одной строке ввода | `placeholder`, `title`, `description`, `group`, `hidden`, `depends` |
| `NumberInput`            | Числовое поле                     | `default`, `title`, `description`, `hidden`, `depends`              |
| `SelectInput`            | Выпадающий список                 | `items`, `title`, `group`, `default`, `hidden`, `depends`           |
| `CheckboxInput`          | Чекбокс                           | `title`, `group`, `description`, `default`, `hidden`, `depends`     |
| `SwitchInput`            | Switch                            | `title`, `group`, `description`, `default`, `hidden`, `depends`     |
| `FileInput`              | Загрузка одного файла             | `title`, `file_extensions`, `group`, `hidden`, `depends`            |
| `FilesInput`             | Загрузка нескольких файлов        | `title`, `file_extensions`, `group`, `hidden`, `depends`, `limit`   |

#### Группировка полей

Используйте параметр `group` для логической группировки полей в интерфейсе:

```python
class TaskConfig(BaseModel):
    # Группа "Основные параметры"
    task_type: Annotated[str, SelectInput(
        title="Тип задачи",
        items=[...],
        group="Основные параметры"
    )]
    
    priority: Annotated[str, SelectInput(
        title="Приоритет",
        items=[...],
        group="Основные параметры"
    )]
    
    # Группа "Дополнительно"
    notifications: Annotated[bool, CheckboxInput(
        title="Уведомления",
        group="Дополнительно"
    )]
    
    tags: Annotated[List[str], StringArrayInput(
        placeholder="Теги...",
        group="Дополнительно"
    )]
```

### 5.2. LogMessage

TODO: описание LogMessage

## 6. Сборка и публикация

1. Установка twine

```bash
pip install --upgrade build twine
```

2. Собрать и загрузить в pypi

перед обновлением сборки нужно не забыть поменять версию в [pyproject.toml](/pyproject.toml)
```bash
python -m build && python -m twine upload dist/*
```

3. Ссылка на проект pypi

> https://pypi.org/project/agent-lab-sdk/

4. установка локально в editable mode. Предварительно может потребоваться выбрать необходимое окружение
```bash
pip install -e .
```
