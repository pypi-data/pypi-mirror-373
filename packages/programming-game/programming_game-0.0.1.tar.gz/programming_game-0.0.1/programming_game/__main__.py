import asyncio
import importlib
import os
import signal
import sys

import click
from loguru import logger

# Add current working directory to the Python path
# This allows us to import from a local bot_logic directory
sys.path.insert(0, os.getcwd())

# --- Credentials ---
CREDENTIALS = {
    "id": os.getenv("GAME_CLIENT_ID"),
    "key": os.getenv("GAME_CLIENT_KEY"),
}


async def run_bot(script_module: str, log_level: str = "INFO"):
    """
    Initializes and runs the game client with the specified script.
    """

    try:
        module_name, instance_name = script_module.split(":", 1)
    except ValueError:
        logger.error(
            f"Invalid script format: '{script_module}'. "
            f"Please use the format 'module.path:instance_name'."
        )
        return

    try:
        module = importlib.import_module(module_name)
        client = getattr(module, instance_name)
    except (ImportError, AttributeError) as e:
        logger.opt(exception=True).error(
            f"Could not import '{instance_name}' from '{module_name}': {e}"
        )
        return

    if not CREDENTIALS["id"] or not CREDENTIALS["key"]:
        logger.error(
            "Missing credentials. Please set GAME_CLIENT_ID and GAME_CLIENT_KEY environment variables."
        )
        return

    # Update credentials
    client._credentials = CREDENTIALS
    client._log_level = log_level

    loop = asyncio.get_running_loop()

    async def shutdown(sig: signal.Signals):
        logger.warning(f"Received shutdown signal: {sig.name}")
        if client:
            await client.disconnect()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s)))

    try:
        await client.connect()
    except asyncio.CancelledError:
        logger.info("Main client connection task was cancelled.")


@click.group()
def cli():
    """A command-line interface for the game client."""
    pass


import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    """Handles file changes and triggers a restart of the bot process."""

    def __init__(self, script_module, log_level="INFO"):
        self.script_module = script_module
        self.log_level = log_level
        self.process = None
        self.last_restart_time = 0
        self.debounce_period = 2  # Cooldown period in seconds
        self.start_process()

    def start_process(self):
        """Starts the main.py script as a subprocess."""
        if self.process and self.process.poll() is None:
            logger.info("Terminating existing bot process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully, killing it.")
                self.process.kill()
            logger.info("Process terminated.")

        logger.success("Starting new bot process...")
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "programming_game",
                "run",
                self.script_module,
                "--log-level",
                self.log_level,
            ]
        )

    def on_any_event(self, event):
        logger.trace(
            f"Event received: type={event.event_type}, path='{event.src_path}'"
        )

        # More robust filtering
        if (
            event.is_directory
            or not event.src_path.endswith(".py")
            or "__pycache__" in event.src_path
            or ".git" in event.src_path
            or os.path.basename(event.src_path).startswith(".")
        ):
            return

        current_time = time.time()
        if current_time - self.last_restart_time < self.debounce_period:
            return

        self.last_restart_time = current_time
        logger.warning(
            f"Detected '{event.event_type}' on file: '{event.src_path}'. Restarting bot..."
        )
        self.start_process()

    def stop(self):
        """Stops the subprocess when the observer is stopped."""
        if self.process and self.process.poll() is None:
            logger.info("Stopping bot process...")
            self.process.terminate()
            self.process.wait()


def run_with_reloader(
    script_module: str, paths_to_watch: list[str] = None, log_level: str = "INFO"
):
    """Main function to set up and run the file observer."""
    # Configure logger to show DEBUG messages
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    event_handler = ChangeHandler(script_module, log_level)
    observer = Observer()
    for path in paths_to_watch or []:
        observer.schedule(event_handler, path, recursive=True)
        logger.info(f"Watching for file changes in '{path}/'...")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        event_handler.stop()
        observer.stop()
        observer.join()
        logger.info("Shutdown complete.")


@cli.command()
@click.argument("script_module")
@click.option("--reload", is_flag=True, help="Enable auto-reloading.")
@click.option(
    "--log-level",
    default="INFO",
    help="Set the log level (e.g., DEBUG, INFO, WARNING).",
)
def run(script_module: str, reload: bool, log_level: str):
    """
    Runs the game client with the specified bot script.

    SCRIPT_MODULE: The Python module path to the bot script (e.g., bot_logic.example_bot).
    """
    if reload:
        # Directories to monitor for changes
        run_with_reloader(
            script_module, [os.getcwd(), os.path.dirname(__file__)], log_level
        )
    else:
        try:
            asyncio.run(run_bot(script_module, log_level))
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Bot stopping...")
        finally:
            logger.info("Shutdown process complete.")


if __name__ == "__main__":
    cli()
