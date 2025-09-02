import json
import logging
import os
from pathlib import Path

from .base import BaseCommand
from ..build_config import is_custom_host_enabled

logger = logging.getLogger(__name__)

CONFIG_DIR_NAME = ".baseshift"
CONFIG_FILE_NAME = "config"


class InitCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose output for debugging",
        )

    def run(self, args, server):
        home_dir = Path.home()
        config_dir = home_dir / CONFIG_DIR_NAME
        config_file_path = config_dir / CONFIG_FILE_NAME

        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                logger.info(f"Ensured config directory exists: {config_dir}")

            org_token = input(
                "Enter default Organization Token (leave blank if none): "
            ).strip()
            dub_uuid = input("Enter default Dub UUID (leave blank if none): ").strip()

            # Only prompt for custom host if this build supports it
            host = ""
            if is_custom_host_enabled():
                host = input(
                    "Enter default Host URL (leave blank for https://app.dubhub.io): "
                ).strip()

            config_data = {}
            if org_token:
                config_data["orgToken"] = org_token
            if dub_uuid:
                config_data["dubUuid"] = dub_uuid
            if host:
                config_data["host"] = host

            with open(config_file_path, "w") as f:
                json.dump(config_data, f, indent=4)
                f.write("\n")  # Add newline to prevent trailing % in terminal

            print(f"Configuration saved to {config_file_path}")
            if not config_data:
                print("No default values were set.")
            else:
                print("Default values set:")
                if "orgToken" in config_data:
                    print(f"  orgToken: {config_data['orgToken']}")
                if "dubUuid" in config_data:
                    print(f"  dubUuid: {config_data['dubUuid']}")
                if "host" in config_data:
                    print(f"  host: {config_data['host']}")

        except Exception as e:
            logger.error(f"Error during baseshift init: {e}")
            print(f"An error occurred: {e}")
