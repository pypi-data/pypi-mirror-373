"""
Tailscale integration module for baseshift CLI.
Manages the Go binary that provides local Tailscale connectivity.
"""

import json
import logging
import os
import platform
import subprocess
import time
import signal
import requests
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


def get_forwarder_metadata_path() -> Path:
    """Get the path to store forwarder metadata."""
    home_dir = Path.home()
    dubhub_dir = home_dir / ".baseshift"
    dubhub_dir.mkdir(exist_ok=True)
    return dubhub_dir / "tailscale_forwarders.json"


def save_forwarder_metadata(clone_uuid: str, pid: int, local_port: int, hostname: str):
    """Save forwarder metadata for later cleanup."""
    metadata_path = get_forwarder_metadata_path()

    # Load existing metadata
    metadata = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, IOError):
            metadata = {}

    # Add new forwarder info
    metadata[clone_uuid] = {
        "pid": pid,
        "local_port": local_port,
        "hostname": hostname,
        "created_at": time.time(),
    }

    # Save updated metadata
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved forwarder metadata for clone {clone_uuid}")
    except IOError as e:
        logger.error(f"Failed to save forwarder metadata: {e}")


def get_forwarder_metadata(clone_uuid: str) -> Optional[Dict[str, Any]]:
    """Get forwarder metadata for a clone UUID."""
    metadata_path = get_forwarder_metadata_path()

    if not metadata_path.exists():
        return None

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return metadata.get(clone_uuid)
    except (json.JSONDecodeError, IOError):
        return None


def remove_forwarder_metadata(clone_uuid: str):
    """Remove forwarder metadata for a clone UUID."""
    metadata_path = get_forwarder_metadata_path()

    if not metadata_path.exists():
        return

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if clone_uuid in metadata:
            del metadata[clone_uuid]

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Removed forwarder metadata for clone {clone_uuid}")
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to remove forwarder metadata: {e}")


def stop_forwarder_by_clone_uuid(clone_uuid: str) -> Dict[str, Any]:
    """Stop a forwarder process by clone UUID."""
    metadata = get_forwarder_metadata(clone_uuid)

    if not metadata:
        return {"success": False, "error": f"No forwarder found for clone {clone_uuid}"}

    pid = metadata["pid"]

    try:
        # Check if process is still running
        os.kill(pid, 0)  # Signal 0 checks if process exists

        # Try graceful termination first
        os.kill(pid, signal.SIGTERM)

        # Wait a bit for graceful shutdown
        time.sleep(2)

        try:
            # Check if it's still running
            os.kill(pid, 0)
            # Still running, force kill
            os.kill(pid, signal.SIGKILL)
            logger.warning(f"Force-killed forwarder process {pid}")
        except ProcessLookupError:
            # Process has exited
            pass

        # Remove metadata
        remove_forwarder_metadata(clone_uuid)

        return {
            "success": True,
            "message": f"Stopped forwarder for clone {clone_uuid} (PID {pid})",
        }

    except ProcessLookupError:
        # Process doesn't exist anymore
        remove_forwarder_metadata(clone_uuid)
        return {
            "success": True,
            "message": f"Forwarder for clone {clone_uuid} was already stopped",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to stop forwarder: {e}"}


class TailscaleForwarder:
    """Manages the Tailscale forwarder Go binary."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.local_port: Optional[int] = None
        self.binary_path = self._get_binary_path()

    def _get_binary_path(self) -> str:
        """Get the path to the platform-specific binary."""
        # Get the package directory
        package_dir = Path(__file__).parent

        # Determine platform-specific binary name
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map platform.machine() output to our binary naming
        if machine in ("x86_64", "amd64"):
            arch = "amd64"
        elif machine in ("arm64", "aarch64"):
            arch = "arm64"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        if system == "darwin":
            binary_name = f"baseshift-dubhub-ts-forwarder-darwin-{arch}"
        elif system == "linux":
            binary_name = f"baseshift-dubhub-ts-forwarder-linux-{arch}"
        elif system == "windows":
            binary_name = f"baseshift-dubhub-ts-forwarder-windows-{arch}.exe"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        # 1) Prefer packaged binary
        binary_path = package_dir / "binaries" / binary_name
        if binary_path.exists():
            return str(binary_path)

        # 2) Look for cached binary under ~/.baseshift/binaries
        cached_path = _get_cached_binary_path(binary_name)
        if cached_path.exists():
            return str(cached_path)

        # 3) Attempt to download if configured
        download_url = _resolve_download_url(binary_name)
        if download_url:
            try:
                _download_binary(download_url, cached_path)
                return str(cached_path)
            except Exception as e:
                raise FileNotFoundError(
                    f"Failed to download forwarder from {download_url}: {e}"
                )

        # 4) Give a descriptive error with remediation hints
        raise FileNotFoundError(
            "Tailscale forwarder binary not found.\n"
            f"Searched: {binary_path} and {cached_path}.\n"
            "To resolve: either\n"
            "  - place the binary at one of the above locations, or\n"
            "  - set BASESHIFT_TS_FORWARDER_URL to a full download URL, or\n"
            "  - set BASESHIFT_TS_FORWARDER_BASE_URL to a base URL hosting the named binary.\n"
            f"Expected filename: {binary_name}"
        )

    def start(
        self,
        auth_key: str,
        remote_host: str,
        remote_port: int,
        clone_uuid: str,
        dub_name: Optional[str] = None,
        dub_uuid: Optional[str] = None,
        local_port: int = 0,
        hostname: Optional[str] = None,
        control_url: Optional[str] = None,
        ephemeral: bool = True,
    ) -> Dict[str, Any]:
        """
        Start the Tailscale forwarder.

        Args:
            auth_key: Tailscale auth key
            remote_host: Target host in Tailscale network
            remote_port: Target port on remote host
            local_port: Desired local port (0 for auto-assign)
            hostname: Local hostname for the tsnet node
            control_url: Optional custom control URL
            ephemeral: Whether to use ephemeral node

        Returns:
            Dict with success status, local_port, and message

        Raises:
            RuntimeError: If the forwarder fails to start
        """
        if self.process and self.process.poll() is None:
            raise RuntimeError("Tailscale forwarder is already running")

        # Generate hostname if not provided
        if hostname is None:
            hostname = f"dubhub-{os.getpid()}"

        request = {
            "action": "start",
            "auth_key": auth_key,
            "hostname": hostname,
            "remote_host": remote_host,
            "remote_port": remote_port,
            "local_port": local_port,
            "ephemeral": ephemeral,
            "clone_uuid": clone_uuid,
            "dub_name": dub_name or "",
            "dub_uuid": dub_uuid or "",
        }

        if control_url:
            request["control_url"] = control_url

        logger.info(f"Starting Tailscale forwarder for {remote_host}:{remote_port}")

        # Create a clean symlink for better process name visibility
        clean_binary_path = self._create_clean_binary_symlink()

        try:
            # Start the Go binary as a detached process (cross-platform)
            self.process = subprocess.Popen(
                [clean_binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # Redirect stderr to avoid blocking
                text=True,
                bufsize=1,  # Line buffered
                start_new_session=True,  # Detach from parent process group
            )

            # Send request
            request_json = json.dumps(request)
            logger.debug(f"Sending request to forwarder: {request_json}")

            # Send the request to stdin
            self.process.stdin.write(request_json + "\n")
            self.process.stdin.flush()

            # Read the response from stdout (one line)
            stdout_line = self.process.stdout.readline()

            # Check if process is still running (it should be for the forwarder)
            if self.process.poll() is not None:
                # Process has exited unexpectedly
                raise RuntimeError(
                    f"Forwarder process exited unexpectedly before sending response"
                )

            # Parse response from the single line we read
            try:
                response = json.loads(stdout_line.strip())
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse forwarder response: {e}\nOutput: {stdout_line}"
                )

            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                raise RuntimeError(f"Forwarder failed to start: {error_msg}")

            self.local_port = response.get("local_port")
            logger.info(f"Tailscale forwarder started on local port {self.local_port}")

            # Save metadata for later cleanup
            save_forwarder_metadata(
                clone_uuid=clone_uuid,
                pid=self.process.pid,
                local_port=self.local_port,
                hostname=hostname or f"dubhub-{clone_uuid[:8]}",
            )

            # Now that we have the response, properly close file handles to detach
            try:
                self.process.stdin.close()
                self.process.stdout.close()
            except:
                pass  # Ignore any errors during cleanup

            # The process is now completely detached and will continue running
            logger.info(f"Forwarder process {self.process.pid} detached successfully")

            # Clear our reference to the process to avoid interference
            self.process = None

            return response

        except subprocess.TimeoutExpired:
            if self.process:
                self.process.kill()
                self.process = None
            raise RuntimeError("Tailscale forwarder startup timed out")

        except Exception as e:
            if self.process:
                self.process.kill()
                self.process = None
            raise RuntimeError(f"Failed to start Tailscale forwarder: {e}")

    def _create_clean_binary_symlink(self):
        """Create a temporary symlink with a clean process name"""
        import tempfile
        import os

        # Create a temporary directory for the symlink
        temp_dir = tempfile.mkdtemp(prefix="baseshift_")
        clean_name = "baseshift-dubhub-ts-forwarder"
        clean_path = os.path.join(temp_dir, clean_name)

        try:
            # Create symlink with clean name
            os.symlink(self.binary_path, clean_path)
            return clean_path
        except OSError:
            # If symlink fails, just use original path
            logger.warning(
                "Failed to create clean process name symlink, using original binary path"
            )
            return self.binary_path

    def stop(self) -> Dict[str, Any]:
        """
        Stop the Tailscale forwarder.

        Returns:
            Dict with success status and message
        """
        if not self.process or self.process.poll() is not None:
            return {"success": True, "message": "Forwarder was not running"}

        logger.info("Stopping Tailscale forwarder")

        try:
            # Try graceful shutdown first
            self.process.terminate()

            # Wait for process to exit
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't exit gracefully
                logger.warning("Forwarder didn't exit gracefully, forcing kill")
                self.process.kill()
                self.process.wait()

            self.process = None
            self.local_port = None

            logger.info("Tailscale forwarder stopped")
            return {"success": True, "message": "Forwarder stopped"}

        except Exception as e:
            logger.error(f"Error stopping forwarder: {e}")
            return {"success": False, "error": str(e)}

    def status(self) -> Dict[str, Any]:
        """
        Get the status of the Tailscale forwarder.

        Returns:
            Dict with status information
        """
        if not self.process:
            return {"success": True, "status": "stopped", "local_port": None}

        if self.process.poll() is not None:
            # Process has exited
            self.process = None
            self.local_port = None
            return {"success": True, "status": "stopped", "local_port": None}

        return {
            "success": True,
            "status": "running",
            "local_port": self.local_port,
            "pid": self.process.pid,
        }

    def get_connection_string(self, original_connection_string: str) -> str:
        """
        Convert a connection string to use the local Tailscale forwarded port.

        Args:
            original_connection_string: The original database connection string

        Returns:
            Modified connection string with localhost and local port
        """
        if not self.local_port:
            raise RuntimeError("Tailscale forwarder is not running")

        # This is a simplified implementation - you may need to adjust
        # based on your specific connection string format
        parts = original_connection_string.split("@")
        if len(parts) != 2:
            raise ValueError("Invalid connection string format")

        credentials, rest = parts
        host_port_db = rest.split("/")
        if len(host_port_db) < 2:
            raise ValueError("Invalid connection string format")

        database_and_params = "/".join(host_port_db[1:])

        # Replace with localhost and local port
        new_connection_string = (
            f"{credentials}@localhost:{self.local_port}/{database_and_params}"
        )

        logger.info(f"Converted connection string to use local port {self.local_port}")
        return new_connection_string

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        try:
            self.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def create_tailscale_forwarder() -> TailscaleForwarder:
    """Factory function to create a TailscaleForwarder instance."""
    return TailscaleForwarder()


# ----------------------------
# Helper functions (module-scope)
# ----------------------------

def _get_cached_binary_path(binary_name: str) -> Path:
    """Return the cache path for the forwarder binary under ~/.baseshift/binaries."""
    home_dir = Path.home()
    cache_dir = home_dir / ".baseshift" / "binaries"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / binary_name


def _resolve_download_url(binary_name: str) -> Optional[str]:
    """
    Resolve the download URL for the forwarder binary using environment variables.

    Supported env vars:
      - BASESHIFT_TS_FORWARDER_URL: full URL to the binary (highest priority)
      - BASESHIFT_TS_FORWARDER_BASE_URL: base URL which hosts binaries named
        like 'baseshift-dubhub-ts-forwarder-<os>-<arch>[.exe]'

    Returns:
      A URL string if resolvable, otherwise None.
    """
    full_url = os.environ.get("BASESHIFT_TS_FORWARDER_URL")
    if full_url:
        return full_url

    base_url = os.environ.get("BASESHIFT_TS_FORWARDER_BASE_URL")
    if base_url:
        # Ensure no trailing slash duplication
        if base_url.endswith("/"):
            return f"{base_url}{binary_name}"
        return f"{base_url}/{binary_name}"

    return None


def _download_binary(url: str, dest_path: Path) -> None:
    """
    Download the binary from 'url' to 'dest_path' atomically and mark executable (if unix).
    """
    tmp_path = dest_path.with_suffix(".tmp")
    try:
        logger.info(f"Downloading Tailscale forwarder from {url}")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        # On unix-like systems, set executable bit
        if os.name != "nt":
            current_mode = os.stat(tmp_path).st_mode
            os.chmod(tmp_path, current_mode | 0o111)
        tmp_path.replace(dest_path)
        logger.info(f"Downloaded forwarder to {dest_path}")
    finally:
        # Best-effort cleanup
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
