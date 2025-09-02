import logging

import click


class ColourFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        colours = {
            logging.INFO: {"bold": True},
            logging.WARNING: {"fg": "yellow"},
            logging.ERROR: {"fg": "bright_red"},
            logging.CRITICAL: {"fg": "bright_white", "bg": "red"},
        }
        try:
            message = click.style(message, **colours[record.levelno])
        except KeyError:
            pass
        return message
