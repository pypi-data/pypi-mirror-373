import logging

from regscale.core.app.logz import create_logger
from regscale.integrations.public.fedramp.reporting import log_error, log_event, write_events


class CaptureEventsHandler(logging.Handler):
    def __init__(self, events, errors, infos):
        self.events = events
        self.errors = errors
        self.infos = infos
        super().__init__()

    def emit(self, record):
        try:
            log_entry = self.format(record)
            if record.levelname == "INFO":
                self.events.append(log_entry)
            elif record.levelname == "ERROR":
                self.errors.append(log_entry)
        except Exception:
            self.handleError(record)


class SSPLogger:
    def __init__(self):
        self.events = []
        self.errors = []
        self.infos = []
        self.capture_handler = CaptureEventsHandler(self.events, self.errors, self.infos)
        logger = create_logger(custom_handler=self.capture_handler)
        self.logger = logger

    def create_logger(self):
        return self.logger

    def info(self, event_msg: str, record_type: str = "", model_layer: str = ""):
        info = {
            "event_msg": event_msg,
            "record_type": record_type,
            "model_layer": model_layer,
        }
        self.infos.append(log_event(**info, level="Info"))

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def error(
        self,
        event_msg: str,
        record_type: str = "",
        model_layer: str = "",
        missing_element: str = "",
    ):
        error = {
            "event_msg": event_msg,
            "missing_element": missing_element,
            "record_type": record_type,
            "model_layer": model_layer,
        }
        self.errors.append(log_error(**error, level="Error"))

    def warning(self, event_msg: str, record_type: str = "", model_layer: str = ""):
        warning = {
            "event_msg": event_msg,
            "record_type": record_type,
            "model_layer": model_layer,
        }
        self.infos.append(log_event(**warning, level="Warning"))

    def get_events(self):
        return self.events

    def get_errors(self):
        return self.errors

    def write_events(self):
        # Write the events.
        final_list = [*self.events, *self.errors, *self.infos]
        write_events(final_list)
