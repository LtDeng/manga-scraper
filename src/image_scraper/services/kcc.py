from __future__ import annotations

import logging
import os
import shlex
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class KccError(RuntimeError):
    pass


def _resolve_library_roots() -> tuple[Path, Path]:
    library_root = Path(os.getenv("LIBRARY_ROOT", "/app/library")).resolve()
    host_library_root_raw = os.getenv("HOST_LIBRARY_ROOT", "").strip()
    if not host_library_root_raw:
        raise KccError(
            "HOST_LIBRARY_ROOT is required for Dockerized KCC conversion. "
            "Set HOST_LIBRARY_ROOT to the host path mapped to LIBRARY_ROOT "
            "(example: -e HOST_LIBRARY_ROOT=$(pwd)/library)."
        )

    return library_root, Path(host_library_root_raw).resolve()


def _to_host_path(path: Path) -> Path:
    library_root, host_library_root = _resolve_library_roots()
    resolved = path.resolve()
    try:
        relative_path = resolved.relative_to(library_root)
    except ValueError as exc:
        raise KccError(
            f"Path '{resolved}' is outside LIBRARY_ROOT '{library_root}'. "
            "Only files under LIBRARY_ROOT can be mounted into the KCC container."
        ) from exc

    return host_library_root / relative_path


def build_kcc_command(images_dir: Path, output_dir: Path, *, use_entrypoint: bool = True) -> list[str]:
    docker_image = os.getenv("KCC_DOCKER_IMAGE", "ghcr.io/ciromattia/kcc:latest")
    executable = os.getenv("KCC_EXECUTABLE", "kcc-c2e").strip()
    docker_platform = os.getenv("KCC_DOCKER_PLATFORM", "").strip()
    flags = shlex.split(os.getenv("KCC_FLAGS", "--format EPUB --nokepub --manga-style"))
    if "--forcecolor" not in flags:
        flags.append("--forcecolor")
    resolved_images_dir = images_dir.resolve()
    resolved_output_dir = output_dir.resolve()
    host_images_dir = _to_host_path(images_dir)
    host_output_dir = _to_host_path(output_dir)

    command = [
        "docker",
        "run",
        "--rm",
    ]

    if docker_platform:
        command.extend(["--platform", docker_platform])

    command.extend(
        [
            "-v",
            # KCC may create temporary working files while preparing source images.
            f"{host_images_dir}:/images",
            "-v",
            f"{host_output_dir}:/output",
        ]
    )

    # Use the converter binary as container entrypoint so it is never treated
    # as a positional input argument.
    if use_entrypoint and executable:
        command.extend(["--entrypoint", executable])

    command.extend(
        [
            docker_image,
            "/images",
            "-o",
            "/output",
            *flags,
        ]
    )

    logger.debug("KCC images_dir=%s", images_dir)
    logger.debug("KCC images_dir.resolve()=%s", resolved_images_dir)
    logger.debug("KCC translated host images dir=%s", host_images_dir)
    logger.debug("KCC output_dir=%s", output_dir)
    logger.debug("KCC output_dir.resolve()=%s", resolved_output_dir)
    logger.debug("KCC translated host output dir=%s", host_output_dir)
    logger.debug("KCC docker command=%s", " ".join(command))
    return command


def convert_with_kcc(images_dir: Path, output_dir: Path, desired_filename: str) -> Path:
    command = build_kcc_command(images_dir=images_dir, output_dir=output_dir, use_entrypoint=True)
    logger.info("Running KCC command: %s", " ".join(command))

    before = {p.name for p in output_dir.glob("*.epub")}
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise KccError(
            "Docker executable not found. Install Docker CLI and mount host docker socket if running in a container."
        ) from exc

    if (
        result.returncode == 127
        and "--entrypoint" in command
        and "executable file not found in $PATH" in result.stderr
    ):
        logger.warning("KCC entrypoint not available in container, retrying without explicit entrypoint.")
        command = build_kcc_command(images_dir=images_dir, output_dir=output_dir, use_entrypoint=False)
        logger.info("Running fallback KCC command: %s", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        logger.error("KCC command failed (exit=%s)", result.returncode)
        logger.error("KCC stdout: %s", result.stdout.strip())
        logger.error("KCC stderr: %s", result.stderr.strip())
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
