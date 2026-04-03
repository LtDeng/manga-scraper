from pathlib import Path

from image_scraper.services.kcc import build_kcc_command


def test_build_kcc_command(monkeypatch):
    monkeypatch.setenv("KCC_DOCKER_IMAGE", "kcc:test")
    monkeypatch.setenv("KCC_EXECUTABLE", "kcc-c2e")
    monkeypatch.setenv("KCC_FLAGS", "--profile=KPW --manga-style")

    command = build_kcc_command(Path("/images/ch"), Path("/output"))

    assert command[:3] == ["docker", "run", "--rm"]
    assert "kcc:test" in command
    assert "--profile=KPW" in command
    assert "--manga-style" in command
