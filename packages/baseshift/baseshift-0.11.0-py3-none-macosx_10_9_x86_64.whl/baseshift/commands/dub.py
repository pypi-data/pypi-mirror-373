import json
import logging
import requests
from time import sleep

from .. import utils
from .base import BaseCommand

logger = logging.getLogger(__name__)


class DubCommand(BaseCommand):
    def add_arguments(self, parser):
        dub_subparsers = parser.add_subparsers(dest="action", required=True)

        parser_snapshot = dub_subparsers.add_parser("snapshot", help="Snapshot a dub")
        parser_snapshot.add_argument(
            "--dubUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Dub (CLI > BASESHIFT_DUB_UUID > config)",
        )
        parser_snapshot.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )
        parser_snapshot.add_argument(
            "--wait", action="store_true", help="Wait for snapshot to complete"
        )

        parser_subset = dub_subparsers.add_parser("subset", help="Subset a dub")
        parser_subset.add_argument(
            "--dubUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Dub (CLI > BASESHIFT_DUB_UUID > config)",
        )
        parser_subset.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )
        parser_subset.add_argument(
            "--config", required=True, help="Path to subset config file"
        )

    def run(self, args, server):
        if args.action == "snapshot":
            self.snapshot(args, server)
        elif args.action == "subset":
            self.subset(args, server)

    def snapshot(self, args, server):
        try:
            dub_uuid = utils.get_config_value(
                args.dubUuid, "BASESHIFT_DUB_UUID", "dubUuid", required=True
            )
            if not utils.is_valid_uuid(dub_uuid):
                logger.error(f"Invalid Dub UUID format: {dub_uuid}")
                print(
                    f"Error: Invalid Dub UUID format: {dub_uuid}. Please check CLI, BASESHIFT_DUB_UUID, or config file."
                )
                return

            org_token = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token):
                logger.error(f"Invalid Organization Token format: {org_token}")
                print(
                    f"Error: Invalid Organization Token format: {org_token}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in snapshot: {e}")
            print(f"Error: {e}")
            return

        try:
            response = requests.post(
                f"{server}/api/dubhub/snapshot",
                json={
                    "orgToken": org_token,
                    "dubUuid": dub_uuid,
                },
            )
            if response.status_code in [400, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.json())
                return
        except Exception as e:
            logger.exception("Error with sending post request:" + str(e))
            return
        try:
            snapshot_uuid = json.loads(json.dumps(json.loads(response.content)))
            print(f"Creating snapshot {snapshot_uuid}", flush=True)
            if args.wait is True:
                print("Waiting for creation to complete", end="", flush=True)
                snapshot_created = False
                while snapshot_created is False:
                    sleep(1)
                    print(".", end="", flush=True)
                    wait_response = requests.get(
                        f"{server}/api/dubhub/snapshot?snapshot_uuid={snapshot_uuid}&orgToken={org_token}",
                    )
                    snapshot_created = json.loads(
                        json.dumps(json.loads(wait_response.content))
                    )
                if snapshot_created is True:
                    print(f"\nSnapshot {snapshot_uuid} created successfully")
                else:
                    print(snapshot_created)
        except Exception as e:
            logger.exception("Error creating snapshot" + str(e))

    def subset(self, args, server):
        try:
            dub_uuid = utils.get_config_value(
                args.dubUuid, "BASESHIFT_DUB_UUID", "dubUuid", required=True
            )
            if not utils.is_valid_uuid(dub_uuid):
                logger.error(f"Invalid Dub UUID format: {dub_uuid}")
                print(
                    f"Error: Invalid Dub UUID format: {dub_uuid}. Please check CLI, BASESHIFT_DUB_UUID, or config file."
                )
                return

            org_token = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token):
                logger.error(f"Invalid Organization Token format: {org_token}")
                print(
                    f"Error: Invalid Organization Token format: {org_token}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in subset: {e}")
            print(f"Error: {e}")
            return

        try:
            with open(args.config, "r") as config_file:
                config_data = json.load(config_file)
            response = requests.post(
                f"{server}/api/dubhub/subset",
                json={
                    "dubUuid": dub_uuid,
                    "orgToken": org_token,
                    "config": config_data,
                },
            )
            if response.status_code in [400, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.json())
                return
            print(response.json())
        except Exception as e:
            logger.exception("Error with sending post request:" + str(e))
