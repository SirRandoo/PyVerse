from dataclasses import dataclass
from dataclasses import field
from enum import StrEnum
from pathlib import Path
from typing import Self

__all__ = [
    "Manifest",
    "ManifestLink",
    "ManifestSupportedVersion",
    "ManifestLinkType",
    "ManifestLoadFolder",
    "ManifestLoadHint",
    "ModDependency",
    "SupportStatus",
    "LoadOrderHint",
]

type Primitive = int | float | bool | str
type JsonValue = Primitive | dict[str, Primitive] | list[Primitive]


class ManifestLinkType(StrEnum):
    """Represents the various types of links the build system supports.

    Attributes:
        SOURCE:
            Indicates that the link provided directs users to the source code
            for the mod.
        DOCUMENTATION:
            Indicates that the link provided directs users to the documentation
            for the mod.
        WEBSITE:
            Indicates that the link provided directs users to the official
            website for the mod.
    """

    SOURCE = "SOURCE"
    WEBSITE = "WEBSITE"
    DOCUMENTATION = "DOCUMENTATION"


@dataclass(slots=True)
class ManifestLink:
    """Represents metadata for a link provided by the mod author for users.

    Attributes:
        type:
            The type of link being described.
        link:
            The actual link to the website.
    """

    type: ManifestLinkType
    link: str

    @classmethod
    def from_json(cls, content: dict[str, str]) -> Self:
        """Creates a new instance of the ManifestLink class from a JSON object.

        Arguments:
            content:
                The JSON object containing information about the manifest link.
        """
        type_: ManifestLinkType = ManifestLinkType(content["type"])
        link: str = content["link"]

        return cls(type_, link)

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        return {"type": str(self.type), "link": self.link}


class SupportStatus(StrEnum):
    """The various types of support statuses available in the build system.

    Attributes:
        SUPPORTED:
            The version of the mod for this game version is actively receiving
            updates from the mod authors, including content updates.
        MAINTENANCE:
            The version of the mod for this game version is actively receiving
            updates from the mod authors. Updates are typically limited to
            fixes.
        UNSUPPORTED:
            The version of the mod for this game version is no longer receiving
            updates from the mod authors.
    """

    SUPPORTED = "SUPPORTED"
    MAINTENANCE = "MAINTENANCE"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(slots=True)
class ManifestSupportedVersion:
    """Represents metadata for the version of the game the mod supports.

    Attributes:
        version:
            The version of the game the mod supports, or a version range of the
            versions of the game the mod supports.
        status:
            The support status users of the mod can expect to receive for this
            version of the game.
    """

    version: str
    status: SupportStatus

    @classmethod
    def from_json(cls, content: dict[str, str]) -> Self:
        """Creates a new instance of ManifestSupportVersion from a JSON object.

        Args:
            content:
                The JSON object containing information about the version of the
                game the mod supports.
        """
        version: str = content["version"]
        status: SupportStatus = SupportStatus(content["status"])

        return cls(version, status)

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        return {"version": self.version, "status": str(self.status)}


@dataclass(slots=True)
class ModDependency:
    """Represents metadata for a dependency the mod requires to function.

    Attributes:
        id:
            The id of the mod being depended upon.
        optional:
            Whether the mod is required in order for this mod to run
            successfully in-game. Optional dependencies, as it implies, are
            optional, but may enable additional functionality in the mod
            should the dependency be active at runtime.
        version:
            The version of the mod this mod was last developed on. Setting this
            attribute does nothing in-game as RimWorld doesn't have any
            capabilities required for this type of feature. This is purely
            informative without mod intervention.
        game_version:
            The version, or range of versions, of the game this dependency is
            applicable to.
    """

    id: str
    optional: bool = field(default=False, init=False)
    version: str | None = field(default=None, init=False)
    game_version: str | None = field(default=None, init=False)

    @classmethod
    def from_json(cls, content: dict[str, str]) -> Self:
        """Creates a new instance of ModDependency from a JSON object.

        Args:
            content:
                The JSON object containing information about the version of the
                mod being depended upon.
        """
        id_: str = content["id"]
        optional: bool = content.get("optional", False)
        version: str | None = content.get("version", None)
        game_version: str | None = content.get("game_version", None)

        dependency = cls(id_)
        dependency.version = version
        dependency.optional = optional
        dependency.game_version = game_version

        return dependency

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        if self.game_version:
            return {
                "id": self.id,
                "version": self.version,
                "optional": self.optional,
                "game_version": self.game_version,
            }
        else:
            return {
                "id": self.id,
                "version": self.version,
                "optional": self.optional,
            }


class LoadOrderHint(StrEnum):
    """The relative positions other mods should be in the game's mod load order.

    Attributes:
        BEFORE:
            Indicates to the game that the associated mod should be placed
            higher in the load order than this mod.
        AFTER:
            Indicates to the game that the associated mod should be placed
            lower in the load order than this mod.
    """

    BEFORE = "BEFORE"
    AFTER = "AFTER"


@dataclass(slots=True)
class ManifestLoadHint:
    """Represents metadata for a load order hint for the mod.

    Attributes:
        id:
            The id of the mod being hinted.
        order:
            The relative position of the mod within the game's mod load order.
    """

    id: str
    order: LoadOrderHint

    @classmethod
    def from_json(cls, content: dict[str, str]) -> Self:
        """Creates a new instance of ManifestLoadHint from a JSON object.

        Args:
            content:
                The JSON representation of the mod being hinted.
        """
        id_: str = content["id"]
        order: LoadOrderHint = LoadOrderHint(content["order"])

        return cls(id_, order)

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        return {"id": self.id, "order": str(self.order)}


@dataclass(slots=True)
class ManifestLoadFolder:
    """Represents metadata for a load folder for the mod.

    Attributes:
        path:
            The path to the directory that should be indexed by the game for
            content files.
        game_version:
            The version of the game, or range of game versions, that this
            folder should be loaded on.
    """

    path: Path
    game_version: str | None = field(default=None, init=False)

    @classmethod
    def from_json(cls, content: dict[str, str | bool]) -> Self:
        """Creates an instance of ManifestLoadFolder class from a JSON object.

        Args:
            content:
                The JSON representation of the folder being loaded by the game.
        """
        path: str = content["path"]
        game_version: str | None = content.get("game_version", None)

        folder = cls(Path(path))

        if game_version:
            folder.game_version = game_version

        return folder

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        if self.game_version:
            return {
                "path": str(self.path.relative_to(Path.cwd())),
                "game_version": self.game_version,
            }
        else:
            return {
                "path": str(self.path.relative_to(Path.cwd())),
            }


@dataclass(slots=True)
class Manifest:
    """Represents metadata for a manifest file for the mod.

    Manifest files describe the mod being developed, its dependencies, the
    structure of the mod, and the game environments the mod will run in.

    Attributes:
        name:
            The human-readable name of the mod.
        id:
            The id of the mod being developed. This attribute is optional since
            the game will generate an id for the mod from the mod's name and
            the first author of the mod. As a result, the build system also
            mimics this behavior internally by defaulting the mod id to the
            one generated by RimWorld.
        description:
            The description of the mod being developed. The text provided is
            displayed in-game in the "mods config" menu, and the first version
            of this text is displayed when the mod is uploaded to Steam
            through the game's "upload" system.
        version:
            The current version of the mod. In the event you'd prefer to link
            the version to the version of a C# project, you can bind the
            version to a given project by settings this attribute to a uri
            similar to a "file" uri, except the scheme is "project" instead.
        authors:
            The authors of the mod being developed. Due to a quirk of RimWorld,
            the build system will insert the first author in the list into a
            separate "author" tag.
        links:
            A collection of links that are provided to the user in some
            contexts. Due to limitations in RimWorld, only one link will be
            displayed to users without mod intervention. Below is the priority
            order for which link will be displayed to users:
              1. The link to the mod's official website
              2. The link to the mod's official documentation
              3. The link to the mod's source code repository
            If you require a special use case, you will need to write your own
            build system, or modify this one to suit your needs.
        supported_versions:
            A collection of game versions the mod contains content for.
        dependencies:
            A collection of mods the mod being developed depends upon in order
            to function.
        load_hints:
            A collection of hints about other mods provided by the developer of
            the mod being developed. These hints provide RimWorld with
            information about where in the load order the mod should be located
            when the mod being developed is active.
        load_folders:
            A collection of folders containing content for the mod being
            developed.
    Notes:
        Since this build system is opinionated, the system will remove any
        XHTML tags found within text displayed in-game in a menu. The manifest
        file is meant to be a descriptor, not a presenter. If presentation of
        your mod's information is important to you, you should create your own
        system, or modify this system.
    """

    name: str
    id: str | None = field(default=None, init=False)

    description: str | None = field(default=None, init=False)
    version: str | None = field(default=None, init=False)
    authors: list[str] = field(default_factory=list, init=False)
    links: list[ManifestLink] = field(default_factory=list, init=False)
    supported_versions: list[ManifestSupportedVersion] = field(
        default_factory=list, init=False
    )
    dependencies: list[ModDependency] = field(default_factory=list, init=False)
    load_hints: list[ManifestLoadHint] = field(
        default_factory=list, init=False
    )
    load_folders: list[ManifestLoadFolder] = field(
        default_factory=list, init=False
    )

    @classmethod
    def from_json(cls, content: dict[str, JsonValue]) -> Self:
        """Creates a new instance of Manifest class from a JSON object.

        Args:
            content:
                The JSON representation of the manifest.
        """
        name: str = content["name"]
        id_: str | None = content.get("id", None)
        description: str | None = content.get("description", None)
        version: str | None = content.get("version", None)
        authors: list[str] = content.get("authors", [])

        links: list[ManifestLink] = [
            ManifestLink.from_json(obj) for obj in content.get("links", [])
        ]

        supported_versions: list[ManifestSupportedVersion] = [
            ManifestSupportedVersion.from_json(obj)
            for obj in content.get("supported_versions", [])
        ]

        dependencies: list[ModDependency] = [
            ModDependency.from_json(obj)
            for obj in content.get("dependencies", [])
        ]

        load_hints: list[ManifestLoadHint] = [
            ManifestLoadHint.from_json(obj)
            for obj in content.get("load_hints", None)
        ]

        load_folders: list[ManifestLoadFolder] = [
            ManifestLoadFolder.from_json(obj)
            for obj in content.get("load_folders", None)
        ]

        manifest = cls(name)
        manifest.id = id_
        manifest.description = description
        manifest.version = version
        manifest.authors = authors
        manifest.links = links
        manifest.supported_versions = supported_versions
        manifest.dependencies = dependencies
        manifest.load_hints = load_hints
        manifest.load_folders = load_folders

        return manifest

    def to_json(self) -> JsonValue:
        """Converts the object to a JSON object."""
        container: dict[str, JsonValue] = {"name": self.name}

        if self.id:
            container["id"] = self.id

        if self.description:
            container["description"] = self.description

        if self.version:
            container["version"] = self.version

        container["authors"] = [author for author in self.authors]
        container["links"] = [link.to_json() for link in self.links]

        container["supported_versions"] = [
            version.to_json() for version in self.supported_versions
        ]

        container["dependencies"] = [
            dependency.to_json() for dependency in self.dependencies
        ]

        container["load_hints"] = [hint.to_json() for hint in self.load_hints]

        container["load_folders"] = [
            folder.to_json() for folder in self.load_folders
        ]

        return container
