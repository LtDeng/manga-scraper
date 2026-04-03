from __future__ import annotations

import logging
import os
import shlex
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class KccError(RuntimeError):
    pass


def build_kcc_command(images_dir: Path, output_dir: Path) -> list[str]:
    docker_image = os.getenv("KCC_DOCKER_IMAGE", "ciromattia/kcc:latest")
    executable = os.getenv("KCC_EXECUTABLE", "kcc-c2e")
    flags = shlex.split(os.getenv("KCC_FLAGS", ""))

    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{images_dir.resolve()}:/images:ro",
        "-v",
        f"{output_dir.resolve()}:/output",
        docker_image,
        executable,
        "/images",
        "-o",
        "/output",
        *flags,
    ]


def convert_with_kcc(images_dir: Path, output_dir: Path, desired_filename: str) -> Path:
    command = build_kcc_command(images_dir=images_dir, output_dir=output_dir)
    logger.info("Running KCC command: %s", " ".join(command))

    before = {p.name for p in output_dir.glob("*.epub")}
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise KccError(
            "Docker executable not found. Install Docker CLI and mount host docker socket if running in a container."
        ) from exc

    if result.returncode != 0:
        raise KccError(
            "KCC conversion failed with exit code "
            f"{result.returncode}. stdout={result.stdout.strip()} stderr={result.stderr.strip()}"
        )

    after = {p.name for p in output_dir.glob("*.epub")}
    created = sorted(after - before)
    if not created:
        raise KccError(
            "KCC command succeeded but no EPUB was generated in output directory."
        )

    generated_path = output_dir / created[0]
    final_path = output_dir / desired_filename
    if final_path.exists():
        final_path.unlink()
    generated_path.rename(final_path)
    return final_path
