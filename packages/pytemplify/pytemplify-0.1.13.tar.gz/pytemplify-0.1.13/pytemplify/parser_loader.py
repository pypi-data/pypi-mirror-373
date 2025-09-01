"""Module to load the specified parser."""

import logging
import sys
from importlib import metadata

from pytemplify.base_classes import BaseParserClass


def load_parser(parser_name: str) -> BaseParserClass:
    """Load the specified parser."""
    try:
        parser = metadata.entry_points(group="pytemplify.parsers")[parser_name].load()
        if issubclass(parser, BaseParserClass):
            return parser()
        logging.error("Parser '%s' is not a subclass of BaseParserClass.", parser_name)
        sys.exit(1)
    except KeyError:
        logging.error("Parser '%s' not found.", parser_name)
        sys.exit(1)
    except (ImportError, AttributeError) as e:
        logging.error("Failed to load parser '%s': %s", parser_name, e)
        sys.exit(1)
