# logging_hub.py
from __future__ import annotations
import logging
import contextvars
import os
from contextlib import contextmanager
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Dict, Optional

# Context key: which "channel" (log) is current?
_current_channel: contextvars.ContextVar[str] = contextvars.ContextVar("current_log_channel", default="default")

def get_current_channel() -> str:
    return _current_channel.get()

def set_current_channel(name: str) -> None:
    _current_channel.set(name)

class ChannelFilter(logging.Filter):
    """Injects the current channel into every LogRecord."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.log_channel = get_current_channel()
        return True

class DispatchingHandler(logging.Handler):
    """
    Routes records to a per-channel handler (file/stream), based on LogRecord.log_channel
    which is set by ChannelFilter.
    """
    def __init__(self):
        super().__init__()
        self._channel_handlers: Dict[str, logging.Handler] = {}
        self._enabled: Dict[str, bool] = {}
        self._default_channel = "default"

    def set_default_channel(self, name: str) -> None:
        self._default_channel = name

    def add_channel(self, name: str, handler: logging.Handler, enabled: bool = True) -> None:
        self._channel_handlers[name] = handler
        self._enabled[name] = enabled

    def enable(self, name: str) -> None:
        self._enabled[name] = True

    def disable(self, name: str) -> None:
        self._enabled[name] = False

    def remove_channel(self, name: str) -> None:
        h = self._channel_handlers.pop(name, None)
        self._enabled.pop(name, None)
        if h:
            try:
                h.flush()
                h.close()
            except Exception:
                pass

    def has_channel(self, name: str) -> bool:
        return name in self._channel_handlers

    def emit(self, record: logging.LogRecord) -> None:
        channel = getattr(record, "log_channel", None) or self._default_channel
        handler = self._channel_handlers.get(channel) or self._channel_handlers.get(self._default_channel)
        if not handler:
            return  # nothing to write to
        if not self._enabled.get(channel, True):
            return  # channel muted
        handler.emit(record)

@dataclass
class ChannelConfig:
    name: str
    path: Optional[str] = None
    level: int = logging.INFO
    fmt: str = "[%(asctime)s] %(levelname)s %(log_channel)s %(name)s: %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
    rotation: Optional[str] = None
    # rotation options:
    #   None                     -> plain FileHandler
    #   "size:10MB:3"            -> RotatingFileHandler(maxBytes=10MB, backupCount=3)
    #   "time:midnight:7"        -> TimedRotatingFileHandler(when="midnight", backupCount=7)

class LoggingHub:
    """
    A centralized, context-aware logging hub.
    Usage:
        hub = LoggingHub()
        hub.init_root()  # do once at startup
        hub.start_channel(ChannelConfig(name="default", path="logs/default.log"))
        hub.set_current("default")

        # In any module:
        log = logging.getLogger("gedcomx")
        log.info("hello")  # goes to current channel

        with hub.use("import-job-42"):
            log.info("within job 42")
    """
    def __init__(self, root_logger_name: str = "gedcomx"):
        self.root_name = root_logger_name
        self._root = logging.getLogger(self.root_name)
        self._dispatch = DispatchingHandler()
        self._root.setLevel(logging.DEBUG)  # Let handlers control final level

        self._filter = ChannelFilter()
        self._initialized = False

    # -------- Initialization --------
    def init_root(self) -> None:
        if self._initialized:
            return
        # Clean existing handlers on the root logger (optional safety)
        for h in list(self._root.handlers):
            self._root.removeHandler(h)
        self._root.addFilter(self._filter)
        self._root.addHandler(self._dispatch)
        self._initialized = True

    # -------- Channel Management --------
    def start_channel(self, cfg: ChannelConfig, make_current: bool = False, enabled: bool = True) -> None:
        """Create/replace a channel with a file/rotating handler."""
        handler: logging.Handler
        formatter = logging.Formatter(cfg.fmt, datefmt=cfg.datefmt)

        if cfg.path is None:
            # StreamHandler to stdout if no path provided
            handler = logging.StreamHandler()
        else:
            # Rotation options
            if cfg.rotation and cfg.rotation.startswith("size:"):
                # "size:10MB:3"
                _, size_str, backups_str = cfg.rotation.split(":")
                size_str = size_str.upper().replace("MB", "*1024*1024").replace("KB", "*1024")
                max_bytes = int(eval(size_str))  # safe for the limited substitutions we made
                backup_count = int(backups_str)
                handler = RotatingFileHandler(cfg.path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
            elif cfg.rotation and cfg.rotation.startswith("time:"):
                # "time:midnight:7" or "time:H:24"
                parts = cfg.rotation.split(":")
                when = parts[1]
                backup_count = int(parts[2]) if len(parts) > 2 else 7
                handler = TimedRotatingFileHandler(cfg.path, when=when, backupCount=backup_count, encoding="utf-8", utc=False)
            else:
                handler = logging.FileHandler(cfg.path, encoding="utf-8")

        handler.setLevel(cfg.level)
        handler.setFormatter(formatter)

        # Replace if exists
        if self._dispatch.has_channel(cfg.name):
            self._dispatch.remove_channel(cfg.name)
        self._dispatch.add_channel(cfg.name, handler, enabled=enabled)

        if make_current:
            self.set_current(cfg.name)

    def stop_channel(self, name: str) -> None:
        self._dispatch.remove_channel(name)

    def enable(self, name: str) -> None:
        self._dispatch.enable(name)

    def disable(self, name: str) -> None:
        self._dispatch.disable(name)

    def list_channels(self) -> Dict[str, bool]:
        """Return dict of channel -> enabled?"""
        return {name: enabled for name, enabled in self._dispatch._enabled.items()}

    # -------- Current Channel --------
    def set_current(self, name: str) -> None:
        set_current_channel(name)

    @contextmanager
    def use(self, name: str):
        """Temporarily switch to a channel within a with-block."""
        token = _current_channel.set(name)
        try:
            yield
        finally:
            _current_channel.reset(token)

    # -------- Utilities --------
    def set_default_channel(self, name: str) -> None:
        self._dispatch.set_default_channel(name)

hub = LoggingHub("gedcomx")     # this becomes your app logger root
hub.init_root()                 # do this ONCE at startup

os.makedirs("logs", exist_ok=True)

# 1) Start a default channel (file w/ daily rotation)
hub.start_channel(
    ChannelConfig(
        name="default",
        path="logs/app.log",
        level=logging.INFO,
        fmt="[%(asctime)s] %(levelname)s %(log_channel)s %(name)s: %(message)s",
        rotation="time:midnight:7",
    ),
    make_current=True
)

# (optional) Also a console channel you can switch to
hub.start_channel(ChannelConfig(name="console", path=None, level=logging.DEBUG))