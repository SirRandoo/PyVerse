import pathlib
import typing
from xml.etree import cElementTree as ElementTree

from .data import WorkshopItem

__all__ = ["get_rimworld_workshop_root", "index_workshop_files"]


def get_rimworld_workshop_root(
    rimworld_install_dir: pathlib.Path,
) -> pathlib.Path:
    return rimworld_install_dir.joinpath("..", "..", "workshop/content/294100")


def index_workshop_files(
    workshop_root: pathlib.Path,
) -> typing.Generator[WorkshopItem]:
    for directory in workshop_root.iterdir():
        if not directory.is_dir():
            continue

        about_file = directory.joinpath("About/About.xml")

        with about_file.open("r") as file:
            about_tree: ElementTree = ElementTree.ElementTree(file=about_file)
            about_root = about_tree.getroot()

            yield WorkshopItem(
                about_root.find("packageId").text,
                int(directory.name),
                directory,
            )
