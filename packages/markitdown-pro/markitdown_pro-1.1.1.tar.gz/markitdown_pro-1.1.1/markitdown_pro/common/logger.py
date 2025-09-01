import logging
import os

log_level = int(os.getenv("LOG_LEVEL", "20"))
logger = logging.getLogger(__name__)
logging.basicConfig(level=log_level, format="[%(asctime)s] [%(levelname)s] %(message)s")

NOISY_LIST = [
    "azure.core.pipeline.policies.http_logging_policy",
    "azure.core.pipeline.policies._universal",
    "Transmission succeeded...",
    "azure.monitor.opentelemetry.exporter",
    "azure.monitor.opentelemetry.exporter._transmission",
    "azure",
    "opentelemetry",
    "urllib3",
    "urllib3.connectionpool",
    "httpx",
    "httpcore",
    "openai",
]

for name in NOISY_LIST:
    logging.getLogger(name).setLevel(logging.WARNING)
