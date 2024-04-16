import dataclasses
import json
import pathlib
import typing

from .rimworld import _find_rimworld_install_path
from .workshop import get_rimworld_workshop_root, WorkshopItem
from .workshop import index_workshop_files

__all__ = ["get_environment", "BuildEnvironment"]


@dataclasses.dataclass(frozen=True, slots=True)
class BuildEnvironment:
    """A dataclass representing the current build environment.

    Attributes:
        rimworld_install_path:
            The path to the directory RimWorld is installed in.
        workshop_root:
            The path to the directory workshop items for RimWorld were
            downloaded into.
    """

    rimworld_install_path: pathlib.Path
    workshop_root: pathlib.Path

    def iter_workshop_files(self) -> typing.Iterator[WorkshopItem]:
        """Iterates through the workshop folder for RimWorld.

        Returns:
            This method returns a dataclass containing basic information about
            the workshop item, including the path to the workshop item on disk,
            the package id of the workshop item, and the workshop id of the
            workshop item.
        """
        yield from index_workshop_files(self.workshop_root)


def get_environment() -> BuildEnvironment:
    state = _load_persistable_state()

    return BuildEnvironment(
        state["rimworld_install_path"], state["workshop_root"]
    )


def _load_persistable_state() -> dict:
    state_file = pathlib.Path.cwd().joinpath(".rimworld")
    state: dict = {}

    if not state_file.exists():
        state = _generate_default_state(state_file)

    if not state:
        with state_file.open("r") as file:
            state = json.load(file)

    return state


def _generate_default_state(state_file_location: pathlib.Path) -> dict:
    state: dict = {}

    rimworld_path: pathlib.Path | None = _find_rimworld_install_path()

    if rimworld_path is None:
        raise SystemError(
            "No rimworld installation could be found on this system."
        )

    state["rimworld_install_path"] = str(rimworld_path)
    state["workshop_path"] = str(get_rimworld_workshop_root(rimworld_path))

    with state_file_location.open("w") as file:
        json.dump(state, file)

    return state
