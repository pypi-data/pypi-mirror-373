import json
import logging
import os
import requests

import psycopg

from .. import utils
from ..version import VERSION
from .base import BaseCommand
from .schema import PGDatabase, PGDatabaseEncoder

logger = logging.getLogger(__name__)


class BaseguardCommand(BaseCommand):
    def add_arguments(self, parser):
        baseguard_subparsers = parser.add_subparsers(dest="action", required=True)

        parser_create_run = baseguard_subparsers.add_parser(
            "create_run", help="Create a baseguard run"
        )
        parser_create_run.add_argument(
            "--projectUuid",
            required=True,
            type=utils.regex_type_uuid,
            help="Uuid of Project",
        )
        parser_create_run.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )

        parser_analyse = baseguard_subparsers.add_parser(
            "analyse", help="Analyse a baseguard run"
        )
        parser_analyse.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )
        parser_analyse.add_argument(
            "--accessToken",
            required=False,
            default=None,
            help="Gitlab/Github Access Token (CLI > BASESHIFT_ACCESS_TOKEN > config)",
        )

        parser_upload_schema = baseguard_subparsers.add_parser(
            "upload_schema", help="Upload a schema to baseguard"
        )
        parser_upload_schema.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )

    def run(self, args, server):
        if args.action == "create_run":
            self.create_run(args, server)
        elif args.action == "analyse":
            self.analyse(args, server)
        elif args.action == "upload_schema":
            self.upload_schema(args, server)

    def create_run(self, args, server):
        try:
            org_token_val = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token_val):
                logger.error(f"Invalid Organization Token format: {org_token_val}")
                print(
                    f"Error: Invalid Organization Token format: {org_token_val}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return
        except ValueError as e:
            logger.error(f"Configuration error in create_run: {e}")
            print(f"Error: {e}")
            return

        try:
            CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", None)
            GITHUB_SHA = os.environ.get("GITHUB_SHA", None)
            GITHUB_REF = os.environ.get("GITHUB_REF", None)
            GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID", None)
            GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", None)
            GITHUB_HEAD_REF = os.environ.get("GITHUB_HEAD_REF", None)
            response = requests.post(
                f"{server}/api/baseguard/create_run",
                json={
                    "GITHUB_REF": GITHUB_REF,
                    "org_token": org_token_val,  # Note: API expects 'org_token' with underscore
                    "project_uuid": args.projectUuid,
                    "GITHUB_SHA": GITHUB_SHA,
                    "CI_COMMIT_SHA": CI_COMMIT_SHA,
                    "GITHUB_RUN_ID": GITHUB_RUN_ID,
                    "GITHUB_REPOSITORY": GITHUB_REPOSITORY,
                    "GITHUB_HEAD_REF": GITHUB_HEAD_REF,
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
            print(response.json())
        except Exception as e:
            logger.exception("Error converting response object to JSON file:" + str(e))

    def analyse(self, args, server):
        try:
            org_token_val = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token_val):
                logger.error(f"Invalid Organization Token format: {org_token_val}")
                print(
                    f"Error: Invalid Organization Token format: {org_token_val}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return

            access_token_val = utils.get_config_value(
                args.accessToken, "BASESHIFT_ACCESS_TOKEN", "accessToken", required=True
            )
            # No specific format validation for access_token, presence is key

        except ValueError as e:
            logger.error(f"Configuration error in analyse: {e}")
            print(f"Error: {e}")
            return

        try:
            CI_API_V4_URL = os.environ.get("CI_API_V4_URL", None)
            CI_PROJECT_ID = os.environ.get("CI_PROJECT_ID", None)
            CI_MERGE_REQUEST_IID = os.environ.get("CI_MERGE_REQUEST_IID", None)
            CI_DEFAULT_BRANCH = os.environ.get("CI_DEFAULT_BRANCH", None)
            CI_COMMIT_SHA = os.environ.get("CI_COMMIT_SHA", None)
            if CI_DEFAULT_BRANCH is None:
                CI_DEFAULT_BRANCH = os.environ.get("GITHUB_BASE_REF", None)
            GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", None)
            GITHUB_SHA = os.environ.get("GITHUB_SHA", None)
            GITHUB_REF = os.environ.get("GITHUB_REF", None)
            GITHUB_PR_REF = os.environ.get("PR_REF", None)
            GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID", None)
            if CI_PROJECT_ID is None:
                GITHUB_OR_GITLAB = "github"
            else:
                GITHUB_OR_GITLAB = "gitlab"
        except Exception as e:
            logger.exception("Error converting JSON file to JSON object:" + str(e))
            return
        try:
            response = requests.post(
                f"{server}/api/baseguard/analyse",
                json={
                    "orgToken": org_token_val,
                    "ACCESS_TOKEN": access_token_val,
                    "CI_API_V4_URL": CI_API_V4_URL,
                    "CI_PROJECT_ID": CI_PROJECT_ID,
                    "CI_COMMIT_SHA": CI_COMMIT_SHA,
                    "CI_MERGE_REQUEST_IID": CI_MERGE_REQUEST_IID,
                    "CI_DEFAULT_BRANCH": CI_DEFAULT_BRANCH,
                    "GITHUB_OR_GITLAB": GITHUB_OR_GITLAB,
                    "GITHUB_REPOSITORY": GITHUB_REPOSITORY,
                    "GITHUB_SHA": GITHUB_SHA,
                    "GITHUB_REF": GITHUB_REF,
                    "VERSION": VERSION,
                    "GITHUB_PR_REF": GITHUB_PR_REF,
                    "GITHUB_RUN_ID": GITHUB_RUN_ID,
                },
            )
            if response.status_code in [400, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.json())
                return
            # print(f"See your results here: {response}")
        except Exception as e:
            logger.exception("Error with sending post request:" + str(e))

    def upload_schema(self, args, server):
        try:
            org_token_val = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token_val):
                logger.error(f"Invalid Organization Token format: {org_token_val}")
                print(
                    f"Error: Invalid Organization Token format: {org_token_val}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return
        except ValueError as e:
            logger.error(f"Configuration error in upload_schema: {e}")
            print(f"Error: {e}")
            return

        try:
            GITHUB_SHA = os.environ.get("GITHUB_SHA", None)
            GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID", None)
            # redundant for now because the driver would looks for these anyway
            conn_params = {
                "dbname": os.getenv("PGDATABASE", default="postgres"),
                "user": os.getenv("PGUSER", default="postgres"),
                "password": os.getenv("PGPASSWORD", default=""),
                "host": os.getenv("PGHOST", default="postgres"),
                "port": os.getenv("PGPORT", default="5432"),
            }
            conn = psycopg.connect(**conn_params)
            db = PGDatabase(conn)
            db.load()
            json_str = json.dumps(db, cls=PGDatabaseEncoder)
            response = requests.post(
                f"{server}/api/baseguard/upload_schema",
                json={
                    "orgToken": org_token_val,
                    "pg_schema_dump": json.loads(json_str),
                    "GITHUB_SHA": GITHUB_SHA,
                    "GITHUB_RUN_ID": GITHUB_RUN_ID,
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
