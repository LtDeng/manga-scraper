from pathlib import Path


class ImageStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def list_images(self) -> list[Path]:
        return sorted(
            p for p in self.directory.iterdir()
            if p.suffix.lower() in (".jpg", ".png", ".webp")
        )
