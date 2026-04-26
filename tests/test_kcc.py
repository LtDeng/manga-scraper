from pathlib import Path

import pytest

from image_scraper.services.kcc import KccError, _to_host_path, build_kcc_command


def test_build_kcc_command(monkeypatch):
    monkeypatch.setenv("LIBRARY_ROOT", "/app/library")
    monkeypatch.setenv("HOST_LIBRARY_ROOT", "/host/library")
    monkeypatch.setenv("KCC_DOCKER_IMAGE", "kcc:test")
    monkeypatch.setenv("KCC_EXECUTABLE", "kcc-c2e")
    monkeypatch.setenv("KCC_FLAGS", "--profile=KPW --manga-style")

    command = build_kcc_command(
        Path("/app/library/series/one-piece/chapters/chapter-1175/images"),
        Path("/app/library/series/one-piece/epub"),
    )

    assert command[:3] == ["docker", "run", "--rm"]
    assert "--entrypoint" in command
    assert "kcc-c2e" in command
    assert "kcc:test" in command
    assert "/host/library/series/one-piece/chapters/chapter-1175/images:/images" in command
    assert "/host/library/series/one-piece/epub:/output" in command
    assert "--profile=KPW" in command
    assert "--manga-style" in command
    assert "--forcecolor" in command


def test_to_host_path_translates_from_library_root(monkeypatch):
    monkeypatch.setenv("LIBRARY_ROOT", "/app/library")
    monkeypatch.setenv("HOST_LIBRARY_ROOT", "/host/library")

    translated = _to_host_path(Path("/app/library/series/demo/chapters/1/images"))

    assert translated == Path("/host/library/series/demo/chapters/1/images")


def test_to_host_path_errors_when_host_library_root_missing(monkeypatch):
    monkeypatch.setenv("LIBRARY_ROOT", "/app/library")
    monkeypatch.delenv("HOST_LIBRARY_ROOT", raising=False)

    with pytest.raises(KccError, match="HOST_LIBRARY_ROOT is required"):
        _to_host_path(Path("/app/library/series/demo"))


def test_to_host_path_errors_for_path_outside_library_root(monkeypatch):
    monkeypatch.setenv("LIBRARY_ROOT", "/app/library")
    monkeypatch.setenv("HOST_LIBRARY_ROOT", "/host/library")

    with pytest.raises(KccError, match="outside LIBRARY_ROOT"):
        _to_host_path(Path("/tmp/not-in-library"))
