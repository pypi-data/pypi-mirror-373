__all__ = ["get_logger", "BasicLogger"]
import sys
import logging


from datetime import datetime
from typing import Optional, Literal, Union


from lt_utils.file_ops import (
    save_text,
    load_text,
    load_yaml,
    save_yaml,
    load_json,
    save_json,
    is_pathlike,
)
from lt_utils.type_utils import is_str
from lt_utils.misc_utils import get_current_time
from pathlib import Path


# ANSI escape sequences for terminal colors
COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class BasicLogger(logging.Formatter):
    def __init__(
        self,
        dir_to_save: Optional[str] = None,
        save_logs: bool = False,
        encoding: Optional[str] = "utf-8",
        errors: Union[str, Literal["strict", "ignore"]] = "strict",
    ):
        super().__init__()
        self.dir_save = None
        self.saving_fn = lambda message, title, level, time: ...
        self.encoding = encoding
        self.errors = errors
        self._key_save_type: Optional[Literal["json", "yaml"]] = None
        if save_logs:
            self.dir_save = Path(
                dir_to_save
                if is_pathlike(dir_to_save, True, False)
                else f"./logs/{get_current_time()}.log"
            )
            if not self.dir_save.name.endswith((".log", ".txt", ".json", ".yaml")):
                self.dir_save = Path(self.dir_save, get_current_time() + ".log")
                self.saving_fn = self._save_text
            else:
                if self.dir_save.name.endswith((".json", ".yaml")):
                    self._key_save_type = self.dir_save.name[-4:]
                    self.saving_fn = self._save_by_keys
                else:
                    self.saving_fn = self._save_text
            self.dir_save.parent.mkdir(exist_ok=True, parents=True)

    def _save_by_keys(self, message: str, title: str, level: str, time: str):
        contents = []
        if self._key_save_type == "json":
            contents = load_json(
                self.dir_save, [], encoding=self.encoding, errors=self.errors
            )
        else:
            contents = load_yaml(self.dir_save, [], False)
        contents.append(
            {
                "title": title.replace(" ", "_"),
                "time": time,
                "level": level,
                "message": message,
            }
        )
        if self._key_save_type == "json":
            save_json(
                path=self.dir_save,
                content=contents,
                encoding=self.encoding,
                errors=self.errors,
            )
        else:
            save_yaml(
                path=self.dir_save,
                content=contents,
                encoding=self.encoding,
                errors=self.errors,
            )

    def _save_text(self, message: str, title: str, level: str, time: str):
        contents = load_text(
            self.dir_save,
            encoding=self.encoding,
            errors=self.errors,
            default_value="\n",
        ).rstrip()

        content = (
            f"[{title} | {time}]: {message.strip()}"
            if title == level
            else f"[{title} - {level} | {time}]: {message.strip()}"
        )
        if contents:
            contents += f"\n"
        contents += f"{content}"
        save_text(
            path=self.dir_save,
            content=contents,
            encoding=self.encoding,
            errors=self.errors,
        )

    def format(self, record):
        log_time = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        level = record.levelname
        reset = COLORS["RESET"]
        color = getattr(record, "color", COLORS.get(level, reset))

        # Title from record or default to level name
        title = getattr(record, "title", level)
        msg = record.getMessage()
        message = f"[{log_time}] ({title.capitalize()}): {msg}"
        self.saving_fn(message=msg, title=title, level=level, time=log_time)
        return f"{color}{message}{reset}"


def get_logger(
    name: str = "Base",
    logs_location: Optional[str] = None,
    level=logging.DEBUG,
    save_logs: bool = False,
    *,
    encoding: Optional[str] = "utf-8",
    errors: Union[str, Literal["strict", "ignore"]] = "strict",
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            BasicLogger(
                logs_location, save_logs=save_logs, encoding=encoding, errors=errors
            )
        )
        logger.addHandler(handler)

    return logger
