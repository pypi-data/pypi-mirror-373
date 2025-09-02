import argparse
import json
import logging
import requests

import os
import shutil
import sys

from .. import utils
from ..utils import parse_connection_string, save_last_clone_uuid, get_last_clone_uuid
from ..version import VERSION
from .. import client as api_client
from .base import BaseCommand
from ..build_config import is_tailscale_enabled

# Conditional Tailscale imports
if is_tailscale_enabled():
    from ..tailscale import create_tailscale_forwarder, stop_forwarder_by_clone_uuid
else:
    # Provide stub functions when Tailscale is disabled
    def create_tailscale_forwarder():
        return None
    
    def stop_forwarder_by_clone_uuid(clone_uuid):
        return {"success": False, "message": "Tailscale not enabled in this build"}

logger = logging.getLogger(__name__)


class CloneCommand(BaseCommand):
    def add_arguments(self, parser):
        # Create parent parsers for common arguments
        org_token_parser = argparse.ArgumentParser(add_help=False)
        org_token_parser.add_argument(
            "--orgToken",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Org Token (CLI > BASESHIFT_ORG_TOKEN > config)",
        )
        
        host_parser = argparse.ArgumentParser(add_help=False)
        host_parser.add_argument(
            "--host",
            type=str,
            help="Host URL for the API server (CLI > BASESHIFT_HOST > config, defaults to https://app.dubhub.io)",
        )
        
        clone_uuid_parser = argparse.ArgumentParser(add_help=False)
        clone_uuid_parser.add_argument(
            "--cloneUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Clone (defaults to last started clone if not specified)",
        )
        
        verbose_parser = argparse.ArgumentParser(add_help=False)
        verbose_parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output for debugging (logs REST responses)",
        )
        
        clone_subparsers = parser.add_subparsers(dest="action", required=True)

        parser_start = clone_subparsers.add_parser("start", parents=[org_token_parser, host_parser, verbose_parser], help="Start a clone")
        parser_start.add_argument(
            "--dubUuid",
            required=False,
            default=None,
            type=utils.regex_type_uuid,
            help="Uuid of Dub (CLI > BASESHIFT_DUB_UUID > config)",
        )
        parser_start.add_argument(
            "--output", type=str, help="Output result of start clone"
        )
        parser_start.add_argument(
            "--grace",
            type=int,
            help="Number of seconds from startup that inactivity is not checked",
        )
        parser_start.add_argument(
            "--timeout",
            type=int,
            help="Number of seconds of inactivity before clone is shut down",
        )

        parser_start.add_argument(
            "--cloneConfig",
            type=str,
            help="Optional JSON string containing key-value pairs for clone configuration",
        )
        if sys.version_info >= (3, 9):
            parser_start.add_argument(
                "-i",
                "--cli",
                action=argparse.BooleanOptionalAction,
                help="Run a native CLI (eg psql) for the clone on start",
            )
        else:
            parser_start.add_argument(
                "-i",
                "--cli",
                action="store_true",
                help="Run a native CLI (eg psql) for the clone on start",
            )
            parser_start.add_argument(
                "--no-cli",
                dest="cli",
                action="store_false",
                help="Run a native CLI (eg psql) for the clone on start",
            )

        clone_subparsers.add_parser("stop", parents=[clone_uuid_parser, org_token_parser, host_parser, verbose_parser], help="Stop a clone")

        parser_analyse = clone_subparsers.add_parser("analyse", parents=[org_token_parser, host_parser], help="Analyse a clone")
        parser_analyse.add_argument(
            "--cloneUuid",
            required=True,
            type=utils.regex_type_uuid,
            help="Uuid of Clone",
        )
        parser_analyse.add_argument(
            "--cloneUuid2",
            required=True,
            type=utils.regex_type_uuid,
            help="Uuid of Clone2",
        )
        parser_analyse.add_argument(
            "--accessToken",
            required=False,
            default=None,
            help="Gitlab/Github Access Token (CLI > BASESHIFT_ACCESS_TOKEN > config)",
        )

        clone_subparsers.add_parser("schema_diff", parents=[clone_uuid_parser, org_token_parser, host_parser], help="Get schema diff for a clone")

        parser_query_diff = clone_subparsers.add_parser("query_diff", parents=[clone_uuid_parser, org_token_parser, host_parser], help="Get query diff for a clone")
        parser_query_diff.add_argument(
            "--baseClone",
            required=False,
            default="",
            type=str,
            help="Base clone UUID for comparison (optional, defaults to empty string)",
        )

    def run(self, args, server):
        if args.action == "start":
            self.start(args, server)
        elif args.action == "stop":
            self.stop(args, server)
        elif args.action == "analyse":
            self.analyse(args, server)
        elif args.action == "schema_diff":
            self.schema_diff(args, server)
        elif args.action == "query_diff":
            self.query_diff(args, server)

    def start(self, args, server):
        # When output mode is JSON, keep stdout clean for JSON only; route status to stderr
        info_stream = sys.stderr if getattr(args, "output", None) == "json" else sys.stdout
        try:
            dub_uuid = utils.get_config_value(
                args.dubUuid, "BASESHIFT_DUB_UUID", "dubUuid", required=True
            )
            if not utils.is_valid_uuid(dub_uuid):
                logger.error(f"Invalid Dub UUID format: {dub_uuid}")
                print(
                    f"Error: Invalid Dub UUID format: {dub_uuid}. Please check CLI, BASESHIFT_DUB_UUID, or config file.",
                    file=info_stream,
                )
                return

            org_token = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token):
                logger.error(f"Invalid Organization Token format: {org_token}")
                print(
                    f"Error: Invalid Organization Token format: {org_token}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file.",
                    file=info_stream,
                )
                return

        except ValueError as e:
            logger.error(f"Configuration error in start: {e}")
            print(f"Error: {e}", file=info_stream)
            return

        # Get host from config with proper priority (CLI > ENV > config)
        try:
            api_host = utils.get_config_value(
                args.host, "BASESHIFT_HOST", "host", default="https://app.dubhub.io"
            )
        except ValueError as e:
            logger.error(f"Configuration error for host: {e}")
            print(f"Error: {e}", file=info_stream)
            return

        # Initialize Tailscale forwarder (will be used if auth key is provided by server)
        tailscale_forwarder = None
        
        # Check if Tailscale is enabled in this build
        if not is_tailscale_enabled():
            pass  # Silently skip Tailscale integration

        # Parse clone_config if provided
        parsed_clone_config = None
        if args.cloneConfig:
            try:
                parsed_clone_config = json.loads(args.cloneConfig)
                logger.info(f"Parsed clone_config: {parsed_clone_config}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in cloneConfig: {e}")
                print(f"Error: Invalid JSON in cloneConfig parameter: {e}", file=info_stream)
                return

        # Control httpx logging based on verbose mode
        httpx_logger = logging.getLogger("httpx")
        if not args.verbose:
            httpx_logger.setLevel(logging.WARNING)  # Suppress INFO logs like HTTP requests
        else:
            httpx_logger.setLevel(logging.INFO)  # Show all logs in verbose mode

        try:
            response = api_client.start_clone_api_sync(
                dub_uuid, org_token, api_host, args.grace, args.timeout, parsed_clone_config
            )

            # Verbose logging for REST responses
            if args.verbose:
                print(f"REST API Response Status: {response.status_code}", file=info_stream)
                print(f"REST API Response Headers: {dict(response.headers)}", file=info_stream)
                try:
                    response_data = response.json()
                    print(f"REST API Response Body: {json.dumps(response_data, indent=2)}", file=info_stream)
                except json.JSONDecodeError:
                    print(f"REST API Response Body (raw): {response.text}", file=info_stream)

            if response.status_code >= 400:
                logger.error(
                    f"API call failed with status code: {response.status_code}"
                )
                try:
                    logger.error(response.json())
                except json.JSONDecodeError:
                    logger.error(response.text)
                return
        except Exception as e:
            logger.exception("Error with sending post request:" + str(e))
            return

        try:
            response_json = response.json()
            connection_string = response_json["conn_string"]
            db_type = response_json.get("db_type", "postgres")

            # Check if Tailscale auth key is provided by server
            tailscale_auth_key = response_json.get("ts_auth_key")
            if tailscale_auth_key and is_tailscale_enabled():
                try:
                    tailscale_forwarder = create_tailscale_forwarder()
                    logger.info("Tailscale forwarder initialized successfully with server-provided auth key")
                except Exception as e:
                    logger.error(f"Failed to initialize Tailscale forwarder: {e}")
                    print(f"Error: Failed to initialize Tailscale forwarder: {e}", file=info_stream)
                    return

            host = ""
            port = ""
            password = ""
            user = "postgres"

            if db_type == "postgres":
                host = utils.parse_connection_string(
                    connection_string, r"host=([^\s]+)"
                )
                port = utils.parse_connection_string(
                    connection_string, r"port=([^\s]+)"
                )
                password = utils.parse_connection_string(
                    connection_string, r"password=([^\s]+)"
                )
            else:
                host = utils.parse_connection_string(connection_string, r"\(([^:]+)")
                port = utils.parse_connection_string(
                    connection_string, r":(\d+)(?![^@]*@)"
                )
                password = utils.parse_connection_string(
                    connection_string, r":(.*?)(?=@)"
                )
                user = utils.parse_connection_string(connection_string, r"^([^@:]+)")

            # Start Tailscale forwarder if enabled
            if tailscale_forwarder:
                try:
                    # Generate remote hostname and client device name
                    dub_name = response_json.get("dub_name", "unknown")
                    clone_uuid_short = response_json["cloneUuid"][:6]
                    tailscale_hostname = f"dubhub-{dub_name}"  # Remote host to connect to
                    client_hostname = f"{dub_name}-clone-client-{clone_uuid_short}"  # Local client device name

                    logger.info(
                        f"Starting Tailscale forwarder for {host}:{port} as {tailscale_hostname}"
                    )
                    forwarder_response = tailscale_forwarder.start(
                        auth_key=tailscale_auth_key,
                        remote_host=tailscale_hostname,  # Use Tailscale hostname, not AWS internal hostname
                        remote_port=int(port),
                        clone_uuid=response_json["cloneUuid"],
                        dub_name=dub_name,
                        dub_uuid=dub_uuid,
                        hostname=client_hostname,  # Client device name in tailnet
                        ephemeral=True,
                    )

                    if forwarder_response.get("success"):
                        local_port = forwarder_response.get("local_port")
                        logger.info(
                            f"Tailscale forwarder started, local port: {local_port}"
                        )
                        print(
                            f"✓ Tailscale forwarder started on local port {local_port}",
                            file=info_stream,
                        )

                        # Update host and port to use local forwarder
                        original_host = host
                        original_port = port
                        host = "localhost"
                        port = str(local_port)

                        print(
                            f"✓ Database accessible via Tailscale: {original_host}:{original_port} → localhost:{local_port}",
                            file=info_stream,
                        )
                    else:
                        error_msg = forwarder_response.get("error", "Unknown error")
                        logger.error(
                            f"Failed to start Tailscale forwarder: {error_msg}"
                        )
                        print(
                            f"Error: Failed to start Tailscale forwarder: {error_msg}",
                            file=info_stream,
                        )
                        return

                except Exception as e:
                    logger.error(f"Exception starting Tailscale forwarder: {e}")
                    print(f"Error: Exception starting Tailscale forwarder: {e}", file=info_stream)
                    return

            # Save the last started clone UUID for convenience
            save_last_clone_uuid(response_json["cloneUuid"])

            json_output = {
                "host": host,
                "port": port,
                "username": user,
                "password": password,
                "database": response_json.get("database", "postgres"),
                "clone_uuid": response_json["cloneUuid"],
                "dub_uuid": dub_uuid,
            }

            # Add Tailscale info if enabled
            if tailscale_forwarder:
                json_output["tailscale_enabled"] = True
                json_output["original_host"] = original_host
                json_output["original_port"] = original_port

            if args.cli:
                # Show user-friendly output before launching psql
                print("Clone started!", file=info_stream)
                print(f"Clone UUID: {json_output['clone_uuid']}", file=info_stream)
                if tailscale_forwarder and json_output.get("tailscale_enabled"):
                    print(f"Tailscale forwarding: localhost:{json_output['port']} → {json_output['original_host']}:{json_output['original_port']}", file=info_stream)
                print("Launching psql...", file=info_stream)

                import subprocess

                cli_env = os.environ.copy()
                cli_env["PGPASSWORD"] = json_output["password"]
                psql_path = shutil.which("psql")
                if not psql_path:
                    print(
                        "Error: psql command not found. Please ensure it's installed and in your PATH.",
                        file=info_stream,
                    )
                    return
                subprocess.run(
                    [
                        psql_path,
                        "-h",
                        json_output["host"],
                        "-p",
                        str(json_output["port"]),
                        "-U",
                        json_output["username"],
                        "-d",
                        json_output["database"],
                    ],
                    env=cli_env,
                )
            elif args.output == "json":
                print(json.dumps(json_output, indent=4))
            elif args.output == "file":
                with open("start_clone_output.json", "w") as outfile:
                    json.dump(json_output, outfile, indent=4)
            else:
                # User-friendly output format
                print("Clone started!")
                print(f"Clone UUID: {json_output['clone_uuid']}")
                # Generate connection string
                if db_type == "postgres":
                    conn_str = f"postgresql://{json_output['username']}:{json_output['password']}@{json_output['host']}:{json_output['port']}/{json_output['database']}"
                else:
                    conn_str = connection_string
                # Show connection information
                print("Connect with psql:")
                print(f"PGPASSWORD={json_output['password']} psql -h {json_output['host']} -p {json_output['port']} -U {json_output['username']} {json_output['database']}")
                print("Connection string:")
                print(conn_str)
                # Show Tailscale info if enabled
                if tailscale_forwarder and json_output.get("tailscale_enabled"):
                    print(f"Tailscale forwarding: localhost:{json_output['port']} → {json_output['original_host']}:{json_output['original_port']}")

        except Exception as e:
            logger.exception("Error processing API response: " + str(e))

    def stop(self, args, server):
        # Determine which clone UUID to use
        clone_uuid = args.cloneUuid
        if not clone_uuid:
            clone_uuid = get_last_clone_uuid()
            if not clone_uuid:
                print("Error: No clone UUID specified and no last started clone found.")
                print("Please specify --cloneUuid or start a clone first.")
                return
            else:
                print(f"Using last started clone: {clone_uuid}")

        try:
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
            logger.error(f"Configuration error in stop: {e}")
            print(f"Error: {e}")
            return

        # Get host from config with proper priority (CLI > ENV > config)
        try:
            api_host = utils.get_config_value(
                args.host, "BASESHIFT_HOST", "host", default="https://app.dubhub.io"
            )
        except ValueError as e:
            logger.error(f"Configuration error for host: {e}")
            print(f"Error: {e}")
            return

        # Control HTTP library logging based on verbose mode
        httpx_logger = logging.getLogger("httpx")
        requests_logger = logging.getLogger("urllib3.connectionpool")
        if not args.verbose:
            httpx_logger.setLevel(logging.WARNING)  # Suppress INFO logs like HTTP requests
            requests_logger.setLevel(logging.WARNING)  # Suppress requests HTTP logs
        else:
            httpx_logger.setLevel(logging.INFO)  # Show all logs in verbose mode
            requests_logger.setLevel(logging.INFO)

        try:
            response = requests.post(
                f"{api_host}/api/clone/stop",
                json={
                    "cloneUuid": clone_uuid,
                    "orgToken": org_token,
                    "VERSION": VERSION,
                },
            )
            if response.status_code in [400, 500]:
                logger.error(
                    "Failed API call with status code: %s", response.status_code
                )
                logger.error(response.json())
                return

            # Stop any associated Tailscale forwarder
            try:
                forwarder_result = stop_forwarder_by_clone_uuid(clone_uuid)
                if forwarder_result.get("success"):
                    logger.info(forwarder_result["message"])
                    print(f"✓ {forwarder_result['message']}")
                else:
                    if args.verbose:
                        logger.info(f"No Tailscale forwarder found for clone {clone_uuid}")
            except Exception as forwarder_error:
                logger.warning(f"Error stopping Tailscale forwarder: {forwarder_error}")
                # Don't fail the entire stop operation if forwarder cleanup fails

            print(response.json())
        except Exception as e:
            logger.exception("Error with sending post request:" + str(e))

    def analyse(self, args, server):
        try:
            org_token = utils.get_config_value(
                args.orgToken, "BASESHIFT_ORG_TOKEN", "orgToken", required=True
            )
            if not utils.is_valid_uuid(org_token):
                logger.error(f"Invalid Organization Token format: {org_token}")
                print(
                    f"Error: Invalid Organization Token format: {org_token}. Please check CLI, BASESHIFT_ORG_TOKEN, or config file."
                )
                return

            access_token = utils.get_config_value(
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
            CI_COMMIT_REF_NAME = os.environ.get("CI_COMMIT_REF_NAME", None)
            if CI_COMMIT_REF_NAME is None:
                CI_COMMIT_REF_NAME = os.environ.get("GITHUB_HEAD_REF", None)
            GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", None)
            GITHUB_SHA = os.environ.get("GITHUB_SHA", None)
            GITHUB_REF = os.environ.get("GITHUB_REF", None)
            GITHUB_PR_REF = os.environ.get("PR_REF", None)
            if CI_PROJECT_ID is None:
                GITHUB_OR_GITLAB = "github"
            else:
                GITHUB_OR_GITLAB = "gitlab"
        except Exception as e:
            logger.exception("Error converting JSON file to JSON object:" + str(e))
            return
        # Get host from config with proper priority (CLI > ENV > config)
        try:
            api_host = utils.get_config_value(
                args.host, "BASESHIFT_HOST", "host", default="https://app.dubhub.io"
            )
        except ValueError as e:
            logger.error(f"Configuration error for host: {e}")
            print(f"Error: {e}")
            return

        try:
            response = requests.post(
                f"{api_host}/api/clone/analyse",
                json={
                    "cloneUuid": args.cloneUuid,
                    "cloneUuid2": args.cloneUuid2,
                    "orgToken": org_token,
                    "ACCESS_TOKEN": access_token,
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
                    "CI_COMMIT_REF_NAME": CI_COMMIT_REF_NAME,
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

    def schema_diff(self, args, server):
        # Determine which clone UUID to use
        clone_uuid = args.cloneUuid
        if not clone_uuid:
            clone_uuid = get_last_clone_uuid()
            if not clone_uuid:
                print("Error: No clone UUID specified and no last started clone found.")
                print("Please specify --cloneUuid or start a clone first.")
                return
            else:
                print(f"Using last started clone: {clone_uuid}")

        try:
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
            logger.error(f"Configuration error in schema_diff: {e}")
            print(f"Error: {e}")
            return

        # Get host from config with proper priority (CLI > ENV > config)
        try:
            api_host = utils.get_config_value(
                args.host, "BASESHIFT_HOST", "host", default="https://app.dubhub.io"
            )
        except ValueError as e:
            logger.error(f"Configuration error for host: {e}")
            print(f"Error: {e}")
            return

        # First, check if the clone is stopped by getting its status
        try:
            status_response = requests.get(
                f"{api_host}/api/clone/status",
                params={
                    "orgToken": org_token,
                    "cloneUuid": clone_uuid,
                },
            )
            if status_response.status_code == 200:
                status_data = status_response.json()
                clone_status = status_data.get("status", "unknown")
                if clone_status != "stopped":
                    print(f"Error: Schema diff can only be run on stopped clones. Current clone status: {clone_status}")
                    print("Please stop the clone first using 'baseshift clone stop' command.")
                    return
            else:
                logger.warning(f"Could not verify clone status: {status_response.status_code}")
                print("Warning: Could not verify clone status. Proceeding with schema diff...")
        except Exception as e:
            logger.warning(f"Error checking clone status: {e}")
            print("Warning: Could not verify clone status. Proceeding with schema diff...")

        try:
            response = requests.get(
                f"{api_host}/api/dubhub/clone/schema_diff",
                params={
                    "orgToken": org_token,
                    "cloneUuid": clone_uuid,
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
            logger.exception("Error with sending get request:" + str(e))

    def query_diff(self, args, server):
        # Determine which clone UUID to use
        clone_uuid = args.cloneUuid
        if not clone_uuid:
            clone_uuid = get_last_clone_uuid()
            if not clone_uuid:
                print("Error: No clone UUID specified and no last started clone found.")
                print("Please specify --cloneUuid or start a clone first.")
                return
            else:
                print(f"Using last started clone: {clone_uuid}")

        try:
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
            logger.error(f"Configuration error in query_diff: {e}")
            print(f"Error: {e}")
            return

        # Get host from config with proper priority (CLI > ENV > config)
        try:
            api_host = utils.get_config_value(
                args.host, "BASESHIFT_HOST", "host", default="https://app.dubhub.io"
            )
        except ValueError as e:
            logger.error(f"Configuration error for host: {e}")
            print(f"Error: {e}")
            return

        try:
            response = requests.get(
                f"{api_host}/api/dubhub/clone/query_diff",
                params={
                    "orgToken": org_token,
                    "cloneUuid": clone_uuid,
                    "baseCloneUuid": args.baseClone,
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
            logger.exception("Error with sending get request:" + str(e))
