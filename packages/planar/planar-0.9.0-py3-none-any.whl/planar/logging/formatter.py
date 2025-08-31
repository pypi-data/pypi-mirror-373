import json
import logging
from typing import Any, Dict

from pydantic import BaseModel
from pygments import formatters, highlight, lexers

# A set of standard LogRecord attributes that should not be included in the extra fields.
# Copied from logging/__init__.py and added a few more that are sometimes present.
STANDARD_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "color_message",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "pid",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


COLORS: Dict[int, str] = {
    logging.DEBUG: "\033[94m",  # Blue
    logging.INFO: "\033[92m",  # Green
    logging.WARNING: "\033[93m",  # Yellow
    logging.ERROR: "\033[91m",  # Red
    logging.CRITICAL: "\033[91m\033[1m",  # Bold Red
}
RESET = "\033[0m"
DARK_GRAY = "\033[90m"


def serialize_value(val: Any) -> Any:
    if isinstance(val, BaseModel):
        return val.model_dump(mode="json")
    elif isinstance(val, list):
        return [serialize_value(item) for item in val]
    elif isinstance(val, dict):
        return {k: serialize_value(v) for k, v in val.items()}
    elif not isinstance(val, (dict, list, int, bool, float, str, type(None))):
        return str(val)
    else:
        return val


def json_print(value: Any, use_colors: bool = False) -> str:
    serialized = serialize_value(value)
    stringified = json.dumps(serialized)

    if use_colors:
        lexer = lexers.JsonLexer()
        formatter = formatters.TerminalFormatter()
        return highlight(stringified, lexer, formatter)
    else:
        return stringified


def dictionary_print(value: Dict[str, Any], use_colors: bool = False) -> str:
    result = []
    for key, val in value.items():
        val_str = json_print(val, use_colors).strip()
        result.append(f"{key}={val_str}")
    return ",".join(result)


class StructuredFormatter(logging.Formatter):
    """
    A logging formatter that formats logs in a structured way with key-value pairs,
    and adds color to log levels when connected to a TTY.
    """

    def __init__(self, use_colors: bool = False):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        levelname = record.levelname

        padding_len = 10 - len(levelname)
        padding_len = max(1, padding_len)
        padded_colon = f"{':':<{padding_len}}"

        if self.use_colors:
            color = COLORS.get(record.levelno, "")
            levelname = f"{color}{levelname}{RESET}"
            record_name = f"{DARK_GRAY}{record.name}{RESET}"
        else:
            record_name = record.name

        extra_attrs = self._format_extra_attrs(record)

        log_message = f"{levelname}{padded_colon}{message} [{record_name}]"
        if extra_attrs:
            log_message += f" [{extra_attrs}]"

        if record.exc_info:
            log_message += "\n" + self.formatException(record.exc_info)

        return log_message

    def _format_extra_attrs(self, record: logging.LogRecord) -> str:
        extra = {
            (key[1:] if key.startswith("$") else key): value
            for key, value in record.__dict__.items()
            if key not in STANDARD_LOG_RECORD_ATTRS
        }
        if not extra:
            return ""
        return dictionary_print(extra, self.use_colors)
