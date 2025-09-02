"""Process management for canvas server lifecycle."""

import asyncio
import atexit
import logging
import os
import signal
import subprocess
import time
from pathlib import Path

import psutil

from .config import config
from .http_client import http_client

logger = logging.getLogger(__name__)


class CanvasProcessManager:
    """Manages the canvas server process lifecycle."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.process_pid: int | None = None
        self._startup_lock = asyncio.Lock()

        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    async def ensure_running(self) -> bool:
        """Ensure canvas server is running and healthy."""
        async with self._startup_lock:
            # Check if process is already running and healthy
            if await self._is_process_healthy():
                return True

            # If auto-start is disabled, just check health
            if not config.server.canvas_auto_start:
                logger.warning("Canvas server not running and auto-start is disabled")
                return False

            # Try to start the process
            success = await self._start_process()
            if not success:
                logger.error("Failed to start canvas server")
                return False

            # Wait for process to become healthy
            return await self._wait_for_health()

    async def _is_process_healthy(self) -> bool:
        """Check if the current process is running and healthy."""
        if not self._is_process_running():
            return False

        return await http_client.check_health()

    def _is_process_running(self) -> bool:
        """Check if the canvas server process is running."""
        if not self.process or not self.process_pid:
            return False

        try:
            # Check if process is still running
            if self.process.poll() is not None:
                logger.debug("Canvas server process has exited")
                self._reset_process_info()
                return False

            # Verify PID is valid
            if not psutil.pid_exists(self.process_pid):
                logger.debug("Canvas server PID no longer exists")
                self._reset_process_info()
                return False

            return True

        except Exception as e:
            logger.debug(f"Error checking process status: {e}")
            self._reset_process_info()
            return False

    async def _start_process(self) -> bool:
        """Start the canvas server process."""
        try:
            project_root = self._get_project_root()
            logger.info(f"Starting canvas server from {project_root}")

            # Kill any existing process
            self._terminate_existing_process()

            # Start new process
            self.process = subprocess.Popen(
                ["npm", "run", "canvas"],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            self.process_pid = self.process.pid
            logger.info(f"Canvas server started with PID: {self.process_pid}")

            # Give the server a moment to start
            await asyncio.sleep(config.server.startup_retry_delay_seconds)

            return True

        except Exception as e:
            logger.error(f"Failed to start canvas server: {e}")
            self._reset_process_info()
            return False

    async def _wait_for_health(self) -> bool:
        """Wait for canvas server to become healthy."""
        logger.info("Waiting for canvas server to become healthy...")

        for attempt in range(config.server.startup_timeout_seconds):
            if not self._is_process_running():
                logger.error("Canvas server process died during startup")
                return False

            if await http_client.check_health(force=True):
                logger.info("Canvas server is healthy and ready")
                return True

            await asyncio.sleep(1)

        logger.error("Canvas server failed to become healthy within timeout")
        self._terminate_current_process()
        return False

    def _terminate_existing_process(self) -> None:
        """Terminate any existing canvas server process."""
        if self.process_pid:
            try:
                # Try to find and kill the process group
                if os.name != "nt":
                    os.killpg(os.getpgid(self.process_pid), signal.SIGTERM)
                else:
                    self.process.terminate()

                # Wait a moment for graceful shutdown
                time.sleep(2)

                # Force kill if still running
                if psutil.pid_exists(self.process_pid):
                    if os.name != "nt":
                        os.killpg(os.getpgid(self.process_pid), signal.SIGKILL)
                    else:
                        self.process.kill()

            except (ProcessLookupError, OSError) as e:
                logger.debug(f"Process already terminated: {e}")
            except Exception as e:
                logger.warning(f"Error terminating existing process: {e}")

        self._reset_process_info()

    def _terminate_current_process(self) -> None:
        """Terminate the current canvas server process."""
        self._terminate_existing_process()

    def _reset_process_info(self) -> None:
        """Reset process information."""
        self.process = None
        self.process_pid = None

    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        current_file = Path(__file__).resolve()
        return current_file.parent.parent

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()

    def cleanup(self):
        """Clean up resources and terminate processes."""
        logger.info("Cleaning up canvas process manager...")
        self._terminate_current_process()

    async def restart(self) -> bool:
        """Restart the canvas server."""
        logger.info("Restarting canvas server...")
        self._terminate_current_process()
        return await self.ensure_running()

    async def stop(self):
        """Stop the canvas server."""
        logger.info("Stopping canvas server...")
        self._terminate_current_process()

    def get_status(self) -> dict:
        """Get process status information."""
        return {
            "running": self._is_process_running(),
            "pid": self.process_pid,
            "healthy": False,  # Will be updated by health check
            "auto_start_enabled": config.server.canvas_auto_start,
        }


# Global process manager instance
process_manager = CanvasProcessManager()
