import logging
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from prometheus_client import Counter, Gauge, Summary, Histogram, Info, Enum

logger = logging.getLogger(__name__)

_metrics: Dict[str, Any] = {}

MetricType = Union[
    Type[Counter],
    Type[Gauge],
    Type[Summary],
    Type[Histogram],
    Type[Info],
    Type[Enum],
]

_CONSTRUCTORS: Dict[str, MetricType] = {
    "counter": Counter,
    "gauge": Gauge,
    "summary": Summary,
    "histogram": Histogram,
    "info": Info,
    "enum": Enum,
}

def get_metric(
    metric_type: str,
    name: str,
    documentation: str,
    *,
    labelnames: Optional[List[str]] = None,
    buckets: Optional[List[float]] = None,
    states: Optional[List[str]] = None,
    **kwargs
) -> MetricType:
    """
    Возвращает метрику по name, создаёт её при первом запросе.
    
    metric_type  — один из ключей _CONSTRUCTORS ('counter', 'gauge', 'summary', 'histogram', 'info', 'enum').
    labelnames   — список имён лейблов (для Counter, Gauge, Summary, Histogram).
    buckets      — для histogram.
    states       — для enum.
    kwargs       — остальные параметры конструктору.
    """
    if name in _metrics:
        return _metrics[name]

    ctor = _CONSTRUCTORS.get(metric_type)
    if ctor is None:
        raise ValueError(f"Unknown metric type: {metric_type!r}")

    try:
        # Собираем позиционные и именованные аргументы в зависимости от типа
        args: Tuple = ()
        if metric_type == "histogram" and buckets is not None:
            # Histogram(name, doc, labelnames?, buckets=buckets, **kwargs)
            args = (name, documentation)
            if labelnames:
                args += (labelnames,)
            _metrics[name] = ctor(*args, buckets=buckets, **kwargs)
        elif metric_type == "enum" and states is not None:
            # Enum(name, doc, labelnames?, states=states, **kwargs)
            args = (name, documentation)
            if labelnames:
                args += (labelnames,)
            _metrics[name] = ctor(*args, states=states, **kwargs)
        else:
            # Counter, Gauge, Summary, Info
            args = (name, documentation)
            if labelnames:
                args += (labelnames,)
            _metrics[name] = ctor(*args, **kwargs)

    except Exception as e:
        logger.error("Failed to create %s metric '%s': %s", metric_type, name, e)
        return None

    return _metrics[name]


if __name__ == "__main__":

    # получение счётчика
    reqs = get_metric("http_reqs", "counter", "http_requests_total",
                    "Всего HTTP-запросов", labelnames=["method", "endpoint"])

    # увеличение
    if reqs:
        reqs.labels("GET", "/api").inc()

    # получение гистограммы
    lat = get_metric("http_latency", "histogram", "http_request_latency_seconds",
                    "Длительность HTTP-запроса", buckets=[0.1, 0.5, 1.0, 5.0])

    # замер времени через контекст
    if lat:
        with lat.time():
            import time
            time.sleep(0.5) # имитируем длительный запрос
            
    print(reqs.collect())
    print(lat.collect())
