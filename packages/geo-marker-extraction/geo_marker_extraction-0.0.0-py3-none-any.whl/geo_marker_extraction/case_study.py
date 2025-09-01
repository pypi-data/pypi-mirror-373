import re
from pathlib import Path


def remove_non_numeric(s: str) -> int:
    return int(re.sub(r"\D", "", s))


def get_image_files() -> list[Path]:
    # TODO: download if required
    image_files = []
    for folder in ["passerine", "non-passerine"]:
        image_files += sorted(
            Path(folder).glob("*.png"),
            key=lambda x: remove_non_numeric(x.name),
        )
    return image_files
