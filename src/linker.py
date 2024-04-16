import dataclasses
from logging import getLogger
from pathlib import Path
from typing import Generator
from typing import Self
from xml.etree import cElementTree as ElementTree

from semver import Version
from yaml import safe_load

from .manifest import Manifest
from .nuget import NuGetClient


@dataclasses.dataclass(slots=True)
class DependencyUpdateResult:
    dependency_id: str
    current_version: Version
    previous_version: Version


@dataclasses.dataclass(slots=True)
class NuGetPackage:
    name: str
    version: Version


@dataclasses.dataclass
class Project:
    project_file: Path
    packages: list[NuGetPackage]


class Linker:
    def __init__(self, manifest: Manifest):
        self._projects: list[Project] = []
        self._manifest: Manifest = manifest
        self._global_dependencies: list[Project] = []
        self._nuget_client: NuGetClient = NuGetClient()

    async def update_packages(self) -> Generator[DependencyUpdateResult]:
        for project in self._projects + self._global_dependencies:
            for package in project.packages:
                newer_release_found: bool = False

                for release in await self._nuget_client.query_package(
                    package.name, include_prereleases=False
                ):
                    for version in release.versions:
                        if version.version > package.version:
                            yield DependencyUpdateResult(
                                package.name, package.version, version.version
                            )

                            newer_release_found = True

                            break

                    if newer_release_found:
                        break

    async def update_dependencies(self) -> Generator[DependencyUpdateResult]:
        for dependency in self._manifest.dependencies:
            if dependency.version is None:
                getLogger(__name__).warning(
                    f"Dependency '{dependency.id}' has no valid version."
                )

            # TODO: Index workshop root for mod

            yield DependencyUpdateResult(
                dependency.id,
                Version.parse(dependency.version),
                Version.parse(dependency.version),
            )

    @classmethod
    def create_linker(cls, mod_root: Path) -> Self:
        manifest_path = mod_root.joinpath("manifest.yaml")

        if not manifest_path.exists():
            getLogger(__name__).error(
                f"Manifest file {manifest_path} does not exist. Aborting.."
            )

            raise FileNotFoundError(
                "Manifest file does not exist.", manifest_path
            )

        instance = cls(Linker._load_manifest(manifest_path))
        instance._projects = Linker._resolve_projects(mod_root.joinpath("src"))

        for item in mod_root.iterdir():
            if item.name == "Directory.Packages.props":
                instance._global_dependencies = (
                    instance._projects + Linker._resolve_projects(item)
                )

                break

        return instance

    @classmethod
    def _load_manifest(cls, manifest_path: Path) -> Manifest:
        with manifest_path.open("r", encoding="utf-8") as file:
            contents = safe_load(file)

            return Manifest.from_json(contents)

    @classmethod
    def _resolve_projects(cls, root: Path) -> list[Project]:
        projects: list[Project] = []

        for child in root.iterdir():
            for inner_child in child.iterdir():
                if inner_child.name.endswith(".csproj"):
                    projects.append(Linker._resolve_project(inner_child))

                    break

        return projects

    @classmethod
    def _resolve_project(cls, project_path: Path) -> Project:
        project: Project = Project(project_path, [])

        with open(project_path, "r", encoding="utf-8") as file:
            tree: ElementTree.ElementTree = ElementTree.ElementTree(file=file)
            root = tree.getroot()

            for item_group in root.iter("ItemGroup"):
                for node in item_group.iter():
                    if (
                        node.tag != "PackageReference"
                        or node.tag != "Reference"
                    ):
                        continue

                    project.packages.append(
                        NuGetPackage(
                            node.get("Include"),
                            Version.parse(node.get("Version")),
                        )
                    )

        return project
