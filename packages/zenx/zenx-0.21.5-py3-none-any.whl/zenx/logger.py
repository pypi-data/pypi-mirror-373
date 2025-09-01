from pathlib import Path
import structlog
import logging

from zenx.settings import settings

logging_level = logging.INFO if settings.LOG_LEVEL == "INFO" else logging.DEBUG



def limit_body_length(logger, method_name, event_dict):
    if 'item' in event_dict and isinstance(event_dict['item'], dict):
        item = event_dict['item']
        if 'body' in item and isinstance(item['body'], str):
            max_length = 50
            if len(item['body']) > max_length:
                item['body'] = item['body'][:max_length] + '...'
    return event_dict


def configure_logger(name: str) -> structlog.BoundLogger:
    if settings.APP_ENV == "prod":
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging_level),
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.add_log_level,
                limit_body_length,
                # format_exc_info suits with JSONRenderer
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            logger_factory=structlog.WriteLoggerFactory(
                file=Path(name).with_suffix(".log").open("wt")
            ),
        )
    else:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging_level),
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.add_log_level,
                limit_body_length,
                structlog.dev.ConsoleRenderer(sort_keys=False),
            ],
        )
    log: structlog.BoundLogger = structlog.get_logger()
    return log
