# filespawn/main.py

import os
import click
from rich.progress import Progress


def parse_size(size_str: str) -> int:
    """Parses a human-readable size string (e.g., '10MB', '1GB') into bytes."""
    size_str = size_str.upper()
    if size_str.endswith("KB"):
        return int(size_str.replace("KB", "")) * 1024
    if size_str.endswith("MB"):
        return int(size_str.replace("MB", "")) * 1024 * 1024
    if size_str.endswith("GB"):
        return int(size_str.replace("GB", "")) * 1024 * 1024 * 1024
    try:
        return int(size_str)
    except ValueError:
        raise click.BadParameter(
            f"Cannot parse size '{size_str}'. Use bytes, KB, MB, or GB."
        )


@click.command()
@click.option(
    "-c", "--count", type=int, required=True, help="Number of files to create."
)
@click.option(
    "-s",
    "--size",
    type=str,
    required=True,
    help="Size of each file. Use bytes or suffixes like '10KB', '25MB'.",
)
@click.option(
    "-d",
    "--dir",
    "output_dir",
    default=".",
    help="Directory to create files in. Defaults to the current directory.",
)
@click.option("--name", default="file", help="Base name for the created files.")
@click.option("--ext", default="dummy", help="File extension.")
def spawn(count, size, output_dir, name, ext):
    """
    Creates a specified number of dummy files of a given size.
    """
    try:
        file_size_bytes = parse_size(size)
    except click.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        click.echo(f"Created directory: {output_dir}")

    # Create a chunk of null bytes to write repeatedly for efficiency
    chunk_size = min(file_size_bytes, 1024 * 1024)  # Write in chunks up to 1MB
    chunk = b"\0" * chunk_size

    with Progress() as progress:
        task = progress.add_task("[cyan]Spawning files...", total=count)

        for i in range(1, count + 1):
            filename = f"{name}_{i}.{ext}"
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, "wb") as f:
                    remaining_size = file_size_bytes
                    while remaining_size > 0:
                        bytes_to_write = min(chunk_size, remaining_size)
                        f.write(chunk[:bytes_to_write])
                        remaining_size -= bytes_to_write
            except IOError as e:
                progress.stop()
                click.echo(f"\nError writing file {filepath}: {e}", err=True)
                return

            progress.update(task, advance=1, description=f"[cyan]Created {filename}")

    click.echo(
        f"\n[bold green]Success![/bold green] Created {count} file(s) of {size} each in '{output_dir}'."
    )


if __name__ == "__main__":
    spawn()
