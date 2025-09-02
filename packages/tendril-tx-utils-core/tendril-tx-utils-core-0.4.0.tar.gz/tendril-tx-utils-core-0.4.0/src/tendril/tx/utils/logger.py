

import io
import sys
from datetime import datetime
from twisted import logger

from twisted.logger import globalLogPublisher
from twisted.logger import LogLevelFilterPredicate
from twisted.logger import FilteringLogObserver
from twisted.logger import textFileLogObserver
from twisted.logger import FileLogObserver
from twisted.logger import LogEvent
from twisted.logger import formatEvent

from tendril.config import LOG_COMPACT_TS
from tendril.config import LOG_COMPACT_TS_READABLE
from tendril.config import LOG_COMPACT_LEVEL
from tendril.config import LOG_COMPACT_LEVEL_ICON


def _time_fmt():
    if LOG_COMPACT_TS:
        if LOG_COMPACT_TS_READABLE:
            return '%m-%d %H%M.%S'
        return '%s'
    return 'YYYY-MM-DD HH:mm:ss.SSS'

time_fmt = _time_fmt()


def format_level(level):
    if LOG_COMPACT_LEVEL or LOG_COMPACT_LEVEL_ICON:
        return f'{level.name[0].upper()}'
    return f'{level.name:<8}'


def format_event(event: LogEvent):
    time_str = datetime.fromtimestamp(event['log_time']).strftime(time_fmt)
    level_str = format_level(event['log_level'])
    if 'log_source' in event.keys():
        logger_str = f"{event['log_source']}"
    else:
        logger_str = f"{event['log_namespace']}"
    if 'system' in event.keys():
        logger_str += f"#{event['system']}"
    if 'log_failure' in event.keys():
        msg = event['log_failure']
    else:
        msg = formatEvent(event)
    log_msg = f"{time_str} | {level_str} | {logger_str} - {msg}\n"
    return log_msg


class TwistedLogObserverManager(object):
    def __init__(self):
        self._observers = {}

    @property
    def observers(self):
        return self._observers

    def init(self):
        for observer in globalLogPublisher._observers:
            print("Removing pre-installed log observer: ", observer)
            globalLogPublisher.removeObserver(observer)

    def add_observer(self, name, observer):
        if name not in self._observers.keys():
            self._observers[name] = observer
            print("Installing log observer: ", observer)
            globalLogPublisher.addObserver(observer)


manager = TwistedLogObserverManager()
manager.init()


class TwistedLoggerMixin(object):
    log_source_instance = False

    def __init__(self, *args, **kwargs):
        super(TwistedLoggerMixin, self).__init__(*args, **kwargs)
        self._log_file = None
        if self.log_source_instance:
            self._log = logger.Logger(namespace=self.__class__.__name__,
                                      source=self)
        else:
            self._log = logger.Logger(namespace=self.__class__.__name__,
                                      source=self.__class__.__name__)
        self._log_level = logger.LogLevel.info

    @property
    def log_file(self):
        return self._log_file

    @property
    def level(self):
        return self._log_level

    @level.setter
    def level(self, value):
        self._log_level = value

    def observers(self):
        rv = []
        stdout_level = self.level
        if self.log_file:
            print(f"Logging to {self.log_file}")
            rv.append(
                ('file', FilteringLogObserver(
                    textFileLogObserver(io.open(self.log_file, 'a')),
                    predicates=[LogLevelFilterPredicate(logger.LogLevel.info)]
                ))
            )
            stdout_level = logger.LogLevel.warn
        rv.append(
            ('stdout', FilteringLogObserver(
                FileLogObserver(sys.stdout, formatEvent=format_event),
                predicates=[LogLevelFilterPredicate(stdout_level)]
            ))
        )
        return rv

    def log_init(self):
        # TODO Fix what this does when you have multiple objects
        #      calling log_init()
        for observer in self.observers():
            manager.add_observer(*observer)

    @property
    def log(self):
        return self._log
