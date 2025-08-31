Example:
```python
from logging_settings import LoggingSettings, setup_logging

LOKI_URL = "http://loki"
LOKI_TAGS = {"name": "my_app"}

def startup(loki: bool = True) -> None:
    log_settings = LoggingSettings(
        loglevel="DEBUG",
        rotating_file_handler=True,
        logs_dir="/var/log/my_app",
        filename="my-app.log",
    )

    if loki:
        log_settings.loki_handler = loki
        log_settings.loki_tags = LOKI_TAGS

    setup_logging(log_settings)
```
