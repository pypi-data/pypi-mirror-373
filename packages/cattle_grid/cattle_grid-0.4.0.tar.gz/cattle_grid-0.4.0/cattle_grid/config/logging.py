import logging


def configure_logging(settings):
    """Sets the log level according to the settings"""
    log_config = settings.get("logging", {})

    for name, level in log_config.items():
        logging.getLogger(name).setLevel(level.upper())
