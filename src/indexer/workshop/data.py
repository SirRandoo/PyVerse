import dataclasses
from pathlib import Path
from xml.etree import cElementTree as ElementTree

__all__ = ["WorkshopItem"]

from semver import Version


@dataclasses.dataclass
class LoadFolder:
    path: Path
    game_version: Version
    requires_active_mods: list[str] = dataclasses.field(default_factory=list)
    requires_inactive_mods: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class WorkshopItem:
    """Represents an item downloaded from RimWorld's Steam workshop.

    Attributes:
        mod_id:
            The package id of the mod.
        steam_id:
            The id of the item on the Steam workshop.
        directory:
            The path to the directory the item was downloaded to.
    """

    mod_id: str
    steam_id: int
    directory: Path

    def __post_init__(self):
        self._load_folders_path: Path = self.directory.joinpath(
            "LoadFolders.xml"
        )

        self._about_file_path: Path = self.directory.joinpath(
            "About/About.xml"
        )

        self._load_folders: list[LoadFolder] = []
        self._highest_load_folder_version: Version | None = None

    def load_folders_for(self, game_version: Version) -> list[LoadFolder]:
        """Returns a list of folders for the given game version.

        Args:
            game_version:
                The version of game to return load folders for.
        Notes:
            This method mimics the standard RimWorld behavior of falling back
            to the next highest version defined in the mod's LoadFolders.xml
            file. For this reason, you may get a list of folders that aren't
            meant to load for a version older than the one specified.
        """
        folders_for_version: list[LoadFolder] = [
            folder
            for folder in self.load_folders()
            if folder.game_version == game_version
        ]

        if folders_for_version:
            return folders_for_version

        return [
            folder
            for folder in self.load_folders()
            if folder.game_version == self._highest_load_folder_version
        ]

    def load_folders(self) -> list[LoadFolder]:
        """Returns the unfiltered list of folders that may be loaded.

        Notes:
            This method will load the folders specified in the LoadFolders.xml,
            if it exists, if it hasn't already. Should no LoadFolder.xml file
            be present in the mod directory, the method will instead fall back
            to standard RimWorld behavior. Either way, this method will cache
            the results of either branch, so subsequent calls to this method
            won't incur further io operations.
        """
        if self._load_folders:
            return self._load_folders

        if not self._load_folders_path.exists():
            return self._generate_load_folders()

        with self._load_folders_path.open("r") as file:
            tree = ElementTree.ElementTree(file=file)

        root_node = tree.getroot()

        for node in root_node.getchildren():
            game_version = Version.parse(node.text.rstrip("v"))

            if (
                self._highest_load_folder_version is None
                or game_version > self._highest_load_folder_version
            ):
                self._highest_load_folder_version = game_version

            for folder in node.getchildren():
                active_mods = folder.get("IfModActive", "")
                inactive_mods = folder.get("IfModNotActive", "")

                self._load_folders.append(
                    LoadFolder(
                        Path(node.text),
                        game_version,
                        [mod for mod in active_mods.split(",") if mod],
                        [mod for mod in inactive_mods.split(",") if mod],
                    )
                )

        return self._load_folders

    def _generate_load_folders(self) -> list[LoadFolder]:
        # By default, RimWorld has a default way of looking for modded content
        # if a mod doesn't include a LoadFolder.xml file. This method mimics
        # this behavior.
        #
        # The standard behavior for RimWorld is as follows:
        #
        # 1. The game will check for folders that are named after a version of
        #    the game. For example, a folder name "1.3" would be loaded on
        #    the RimWorld version 1.3 and above. The exception to this behavior
        #    if is a folder with a higher, more specific, version is also
        #    present in the mod's root directory. This means that if a mod has
        #    both a "1.3" folder, and a "1.4" folder, the game will load
        #    content from the "1.4" on when the 1.4 version of RimWorld is
        #    being used, and content from the "1.3" version will be skipped.
        #
        # 2. The game will always check for a folder named "Common." If a
        #    common folder exists, the game will always load content from it.
        #
        # 3. The game will always check the root directory for the mod for any
        #    modded content, and subsequently load said content.
        #
        #
        # There exists a "forwards compatible" feature for the first iteration
        # of the game, "1.0." On 1.0, the game will load content from the root
        # directory of the mod, unless there's a specific "1.0" directory
        # present in the mod. However, this is only supports content like defs,
        # patches, and assemblies. All other content will be loaded from the
        # root directory.

        if self._load_folders:
            return self._load_folders

        common_folder_path = self.directory.joinpath("Common")
        has_common_folder: bool = common_folder_path.exists()

        for node in self.directory.iterdir():
            if not node.is_dir() or not Version.is_valid(node.name):
                continue

            version = Version.parse(node.name)

            if has_common_folder:
                self._load_folders.append(
                    LoadFolder(common_folder_path, version, [], [])
                )

            self._load_folders.append(LoadFolder(node, version, [], []))
            self._load_folders.append(
                LoadFolder(self.directory, version, [], [])
            )

        return self._load_folders
