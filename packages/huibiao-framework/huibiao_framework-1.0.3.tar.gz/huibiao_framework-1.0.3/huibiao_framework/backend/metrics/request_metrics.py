from typing import Dict
from loguru import logger
from prometheus_client import Counter, Gauge


class RequestOperationMetrics:
    """
    算法接口中算法操作的耗时统计
    """

    __METRICS_MAX: Dict[str, float] = dict()
    __METRICS_SUM: Dict[str, float] = dict()
    __METRICS_NUM: Dict[str, int] = dict()
    __AVG_METRICS: Dict[str, float] = dict()
    __ERROR_METRICS: Dict[str, int] = dict()

    _max_metrics = Gauge(
        "operation_max_duration_seconds",
        "The maximum duration of an operation.",
        ["operation"],
    )
    _num_metrics = Counter(
        "operation_count", "The total number of operations.", ["operation"]
    )
    _avg_metrics = Gauge(
        "operation_avg_duration_seconds",
        "The average duration of an operation.",
        ["operation"],
    )
    _error_metrics = Counter(
        "operation_errors_total",
        "The total number of errors in operations.",
        ["operation"],
    )

    @classmethod
    def add(cls, key, cost):
        _max = cls.__METRICS_MAX.get(key, 0)
        _sum = cls.__METRICS_SUM.get(key, 0)
        _num = cls.__METRICS_NUM.get(key, 0)

        new_max = max(_max, cost)
        new_sum = _sum + cost
        new_num = _num + 1
        cls.__METRICS_MAX[key] = new_max
        cls.__METRICS_SUM[key] = new_sum
        cls.__METRICS_NUM[key] = new_num
        cls.__AVG_METRICS[key] = new_sum / new_num
        logger.info(
            f"OpTimeCost：{key}: max={new_max}, sum={new_sum}, num={new_num}, avg={new_sum / new_num}s"
        )
        # 更新 Prometheus 指标
        cls._max_metrics.labels(operation=key).set(new_max)
        cls._num_metrics.labels(operation=key).inc(1)
        cls._avg_metrics.labels(operation=key).set(new_sum / new_num)

    @classmethod
    def add_error(cls, key):
        cls.__ERROR_METRICS[key] = cls.__ERROR_METRICS.get(key, 0) + 1
        logger.info(f"OpErrorNum：{key}: {cls.__ERROR_METRICS[key]}")
        cls._error_metrics.labels(operation=key).inc(1)
