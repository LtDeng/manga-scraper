from pathlib import Path
from PIL import Image


class PdfCompiler:
    def compile(self, images: list[Path], output_path: Path) -> None:
        if not images:
            raise RuntimeError("No images to compile")

        pil_images = [Image.open(img).convert("RGB") for img in images]
        pil_images[0].save(
            output_path,
            save_all=True,
            append_images=pil_images[1:]
        )
