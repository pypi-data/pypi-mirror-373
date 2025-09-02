#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
from abc import ABC,                                    \
                abstractmethod
from copy import copy
from datetime import datetime,                          \
                     tzinfo
from logging import getLogger,                          \
                    Formatter,                          \
                    Logger,                             \
                    LogRecord,                          \
                    root,                               \
                    config,                             \
                    addLevelName,                       \
                    getLevelName,                       \
                    LoggerAdapter,                      \
                    StreamHandler,                      \
                    Handler,                            \
                    DEBUG,                              \
                    INFO,                               \
                    WARN,                               \
                    ERROR,                              \
                    CRITICAL,                           \
                    NOTSET
from logging.handlers import RotatingFileHandler
from os import path,                                    \
               remove,                                  \
               mkdir
from typing import Any,                                 \
                   Callable

from galaxy.service import constant
from galaxy.service.service import Manager,             \
                                   AsyncManager,        \
                                   LogService,          \
                                   LogAsyncService
from galaxy.utils.base import Component,                \
                              Configurable


class HandlerFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(HandlerFactory, self)._load()

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class ZmqNotificationLoggingHandler(Handler):
    """
    classdocs
    """

    def __init__(self, root_topic: str | None = None) -> None:
        """
        Constructor
        """
        super(ZmqNotificationLoggingHandler, self).__init__()
        self.formatters = {
                           DEBUG: Formatter("%(levelname)s %(filename)s:%(lineno)d - %(message)s\n"),
                           INFO: Formatter("%(message)s\n"),
                           WARN: Formatter("%(levelname)s %(filename)s:%(lineno)d - %(message)s\n"),
                           ERROR: Formatter("%(levelname)s %(filename)s:%(lineno)d - %(message)s - %(exc_info)s\n"),
                           CRITICAL: Formatter("%(levelname)s %(filename)s:%(lineno)d - %(message)s\n")
                          }
        self._root_topic = root_topic
        self.notif_pub: Any = None

    def setRootTopic(self, root_topic: str):
        if isinstance(root_topic, bytes):
            root_topic = root_topic.decode("utf8")
        self._root_topic = root_topic

    def setFormatter(self, fmt, level=NOTSET):
        if level == NOTSET:
            for fmt_level in self.formatters.keys():
                self.formatters[fmt_level] = fmt
        else:
            self.formatters[level] = fmt

    def format(self, record):
        return self.formatters[record.levelno].format(record)

    def emit(self, record):
        try:
            topic, msg = str(record.msg).split(constant.TOPIC_DELIM, 1)
        except ValueError:
            topic = ""
        else:
            # copy to avoid mutating LogRecord in-place
            record = copy(record)
            record.msg = msg

        try:
            bmsg = self.format(record).encode("utf8")
        except Exception:
            self.handleError(record)
            return

        topic_list = []
        if self._root_topic:
            topic_list.append(self._root_topic)
        topic_list.append(record.levelname)
        if topic:
            topic_list.append(topic)
        btopic = ".".join(topic_list).encode("utf8", "replace")

        #self.notif_pub
        #self.socket.send_multipart([btopic, bmsg])


class ZmqNotificationLoggingHandlerFactory(HandlerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqNotificationLoggingHandlerFactory, self).__init__()
        self.formatter: Formatter | None = None
        self.notif_pub: Any | None = None

    def create(self) -> ZmqNotificationLoggingHandler:
        handler = ZmqNotificationLoggingHandler(self.conf["root_topic"])
        handler.set_name(self.conf["name"])
        handler.setLevel(self.conf["level"])
        handler.notif_pub = self.notif_pub
        return handler


class RotatingFileLoggingHandlerFactory(HandlerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RotatingFileLoggingHandlerFactory, self).__init__()

    def create(self) -> RotatingFileHandler:
        if path.exists(self.conf["dir"]) and not path.isdir(self.conf["dir"]):
            remove(self.conf["dir"])
        if not path.exists(self.conf["dir"]):
            mkdir(self.conf["dir"])
        handler = RotatingFileHandler(path.join(self.conf["dir"], self.conf["filename"]),
                                      self.conf["mode"],
                                      self.conf["max_bytes"],
                                      self.conf["backup_count"],
                                      self.conf["encoding"])
        handler.set_name(self.conf["name"])
        handler.setLevel(self.conf["level"])
        return handler


class StreamLoggingHandlerFactory(HandlerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(StreamLoggingHandlerFactory, self).__init__()

    def create(self) -> StreamHandler:
        handler = None
        if self.conf["stream"] == "stdout":
            handler = StreamHandler(sys.stdout)
        elif self.conf["stream"] == "stderr":
            handler = StreamHandler(sys.stderr)
        handler.set_name(self.conf["name"])
        handler.setLevel(self.conf["level"])
        return handler


class FormatterFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(FormatterFactory, self)._load()

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class MSecLoggingFormatter(Formatter):
    """
    classdocs
    """

    def __init__(self, fmt: str, datefmt: str, style: str = "%") -> None:
        """
        Constructor
        """
        super(MSecLoggingFormatter, self).__init__(fmt, datefmt, style)
        self.converter: Callable[[float, tzinfo | None], datetime] = datetime.fromtimestamp

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = datetime.strftime(self.default_time_format, ct)
            s = self.default_msec_format.format(t, record.msecs)
        return s


class MSecLoggingFormatterFactory(FormatterFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(MSecLoggingFormatterFactory, self).__init__()

    def create(self) -> MSecLoggingFormatter:
        formatter = MSecLoggingFormatter(self.conf["format"],
                                         self.conf["datefmt"])
        return formatter


class LoggerFactory(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)

    def _load(self) -> None:
        super(LoggerFactory, self)._load()

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class LoggingLoggerFactory(LoggerFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LoggingLoggerFactory, self).__init__()
        self.handler_factories: dict[str, HandlerFactory] | None = None
        self.fmt_factories: dict[str, FormatterFactory] | None = None

    def _load(self) -> None:
        super(LoggerFactory, self)._load()
        [handler_fact._load() for handler_fact in self.handler_factories.values()]
        [fmt_fact._load() for fmt_fact in self.fmt_factories.values()]

    def create(self) -> Logger:
        logger = Logger(self.conf["name"], self.conf["level"])
        logger.propagate = self.conf["propagate"]
        formatters = {name:fact.create() for name, fact in self.fmt_factories.items()}
        for name, fact in self.handler_factories.items():
            handler = fact.create()
            handler.formatter = formatters[fact.conf["formatter"]]
            logger.addHandler(handler)
        return logger


class LoggingService(LogService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LoggingService, self).__init__()
        #self.extra_info: dict[str, Any] | None = None
        self.logger_factories: dict[str, LoggerFactory] | None = None
        self.logger: Logger | None = getLogger()

    def _load(self) -> None:
        super(LoggingService, self)._load()
        self.loggers = {}
        for name, fact in self.logger_factories.items():
            fact._load()
            self.loggers[name] = fact.create()
        self.logger = list(self.loggers.values())[0]
        #self.add_logger("transitions")
        #     if self.extra_info is not None:
        #         self.logger = LoggerAdapter(logger, self.extra_info)
        #     else:
        #         self.logger = logger

    def add_logger(self, name):
        logger = getLogger(name)
        logger.disabled = False
        [logger.removeHandler(handler) for handler in logger.handlers[:]]
        logger.setLevel(self.logger.level)
        #self.add_logger("transitions")

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<LoggingService(id='{}')>".format(self.id)


class LoggingAsyncService(LogAsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LoggingAsyncService, self).__init__()
        self.extra_info: dict[str, Any] | None = None
        self.logger_factories: dict[str, LoggerFactory] | None = None
        self.loggers: dict[str, Logger] | None = None
        self.logger: Logger = getLogger()

    async def _load(self) -> None:
        await super(LoggingAsyncService, self)._load()
        self.loggers = {}
        for name, fact in self.logger_factories.items():
            fact._load()
            self.loggers[name] = fact.create()
        self.logger = list(self.loggers.values())[0]
        #self.add_logger("transitions")
        #     if self.extra_info is not None:
        #         self.logger = LoggerAdapter(logger, self.extra_info)
        #     else:
        #         self.logger = logger

    def add_logger(self, name):
        logger = getLogger(name)
        logger.disabled = False
        [logger.removeHandler(handler) for handler in logger.handlers[:]]
        logger.setLevel(self.logger.level)
        [logger.addHandler(handler) for handler in self.logger.handlers]

    async def _start(self) -> None:
        pass

    async def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<LoggingAsyncService(id='{}')>".format(self.id)


class SyslogService(LogService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SyslogService, self).__init__()

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<SyslogService(id='{}')>".format(self.id)


class SyslogNGService(LogService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SyslogNGService, self).__init__()

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<SyslogNGService(id='{}')>".format(self.id)


class LogManager(Manager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LogManager, self).__init__()

    def __repr__(self) -> str:
        return "<LogManager(id='{}')>".format(self.id)


class LogAsyncManager(AsyncManager):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(LogAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<LogAsyncManager(id='{}')>".format(self.id)
