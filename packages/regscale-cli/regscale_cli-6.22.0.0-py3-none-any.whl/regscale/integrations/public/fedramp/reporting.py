"""Provide modules for logging and reporting."""

from datetime import datetime

from regscale.core.app.logz import create_logger

logger = create_logger()


def log_event(
    record_type: str,
    event_msg: str,
    model_layer: str = "Undefined",
    level: str = "Info",
) -> dict:
    """
    Function to log events

    :param str record_type: record type (SSP, Control Implementation, etc)
    :param str event_msg: Message to log for the event
    :param str model_layer: relevant NIST SSP model layer missing from, such as 'metadata' or 'system-characteristics'
    :param str level: Level of logging, defaults to info
    :return: dict to save to logs
    :rtype: dict
    """

    logger.info(f"Layer: {model_layer} |  {record_type} | {event_msg}")

    event_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "level": level,
        "model_layer": model_layer,
        "record_type": record_type,
        "event": event_msg,
    }
    return event_entry


def log_error(
    record_type: str,
    missing_element: str = "Undefined",
    model_layer: str = "Undefined",
    level: str = "Error",
    event_msg: str = None,
) -> dict:
    """
    Log errors

    :param str record_type: record type (SSP, Control Implementation, etc)
    :param str missing_element: the name data element expected but not found, defaults to 'Undefined'
    :param str model_layer: relevant NIST SSP model layer missing from, such as 'metadata' or 'system-characteristics'
    :param str level: Level of the logging, defaults to error
    :param str event_msg: Event such as data element recorded
    :return: dict to save to logs
    :rtype: dict
    """

    if event_msg is None:
        event_msg = f"Failed to locate required element: {missing_element}"
    msg = f"Layer: {model_layer} |  {record_type} | " + event_msg
    logger.error(msg)

    event_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "level": level,
        "model_layer": model_layer,
        "record_type": record_type,
        "event": event_msg,
    }
    return event_entry


def write_events(events_list: list, filepath: str = "artifacts/import-results.csv") -> None:
    """
    Write events to CSV file

    :param list events_list: list of events to be written to CSV
    :param str filepath:  default if not specified otherwise use provided file path
    :rtype: None
    """
    import pandas as pd  # Optimize import performance

    events_df = pd.DataFrame(events_list)
    events_df.to_csv(filepath)
