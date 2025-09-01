"""Main module for the pytemplify package."""

import argparse
import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pytemplify.parser_loader import load_parser
from pytemplify.renderer import TemplateRenderer


def setup_logging(log_filepath: Path, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Configure logging."""
    log_filepath.parent.mkdir(parents=True, exist_ok=True)
    rotating_handler = RotatingFileHandler(log_filepath, maxBytes=max_bytes, backupCount=backup_count, delay=False)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), rotating_handler],
    )


def cli_entry(parser_name: str) -> None:
    """Command line interface entry point."""
    argparser = argparse.ArgumentParser(description="A simple templating engine.")
    argparser.add_argument("template", help="The template file or directory to render.")
    argparser.add_argument("output-dir", help="The output directory to write the rendered templates to.")
    argparser.add_argument("--input-data", help="The input data file to parse.")
    argparser.add_argument("--input-dict", help="The JSON file containing dictionary data.")
    argparser.add_argument(
        "--print-schema",
        action="store_true",
        help="Print the data dictionary schema in JSON format.",
    )
    args = argparser.parse_args()

    setup_logging(Path("pytemplify.log"))

    logging.info("Using parser: %s", parser_name)
    parser = load_parser(parser_name)
    data_class = parser.get_data_class()

    if args.print_schema:
        schema = data_class.json_schema()
        print(json.dumps(schema, indent=2))
        return

    if args.input_data:
        data = parser.parse(Path(args.input_data))
        # Save the parsed dictionary data
        data.save(Path(args.input_data).with_suffix(".parsed.json"))
    elif args.input_dict:
        with open(args.input_dict, "r", encoding="utf-8") as dict_file:
            data_dict = json.load(dict_file)
            data = data_class(**data_dict)
    else:
        logging.error("Either --input_data or --dict_data must be provided.")
        sys.exit(1)

    renderer = TemplateRenderer(data, "dict_data")
    renderer.generate(Path(args.template), Path(args.output_dir))
