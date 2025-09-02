import subprocess
import time

import click

from zendo.config import appname


@click.group()
def cli():
    """Main entry point for the application."""
    pass


@cli.command()
@click.option("--port", default=8000, help="Port to run the application on.")
def start(port: int):
    """Start the application."""
    while True:
        try:
            # Attempt to run the application
            subprocess.run(
                [
                    "watchmedo",
                    "auto-restart",
                    "-d",
                    ".",
                    "-p",
                    "*.py",
                    "--recursive",
                    "--",
                    "uv",
                    "run",
                    "-m",
                    f"{appname}.app",
                ]
            )
            break  # Exit loop if successful
        except subprocess.CalledProcessError as e:
            print(f"Error starting application: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    cli()
