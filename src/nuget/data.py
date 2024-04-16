from dataclasses import dataclass
from typing import Self

from semver import Version
from yarl import URL

__all__ = [
    "SearchQueryResponse",
    "SearchQueryContext",
    "SearchQueryDataEntry",
    "SearchQueryPackageVersion",
    "SearchQueryPackageType",
]


@dataclass(slots=True)
class SearchQueryContext:
    base: URL
    vocab: URL

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return SearchQueryContext(
            base=URL(data["@base"]),
            vocab=URL(data["@vocab"]),
        )

    def to_json(self) -> dict:
        return {
            "@base": str(self.base),
            "@vocab": str(self.vocab),
        }


@dataclass(slots=True)
class SearchQueryPackageType:
    name: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return SearchQueryPackageType(data["name"])

    def to_json(self) -> dict:
        return {
            "name": self.name,
        }


@dataclass(slots=True)
class SearchQueryPackageVersion:
    id: URL
    downloads: int
    version: Version

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return SearchQueryPackageVersion(
            id=data["@id"],
            downloads=data["downloads"],
            version=Version.parse(data["version"]),
        )

    def to_json(self) -> dict:
        return {
            "@id": str(self.id),
            "downloads": self.downloads,
            "version": str(self.version),
        }


@dataclass(slots=True)
class SearchQueryDataEntry:
    id_url: URL
    type: str
    authors: list[str]
    description: str
    icon_url: URL
    id: str
    license_url: URL
    owners: list[str]
    package_types: [SearchQueryPackageType]
    project_url: URL
    registration: URL
    summary: str
    tags: list[str]
    title: str
    total_downloads: int
    verified: bool
    version: Version
    versions: list[SearchQueryPackageVersion]
    vulnerabilities: list

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return SearchQueryDataEntry(
            id_url=URL(data["@id"]),
            type=data["@type"],
            authors=data["authors"],
            description=data["description"],
            icon_url=URL(data["iconUrl"]),
            id=data["id"],
            owners=data["owners"],
            package_types=[
                SearchQueryPackageType.from_json(package_type)
                for package_type in data["packageTypes"]
            ],
            project_url=URL(data["projectUrl"]),
            license_url=URL(data["licenseUrl"]),
            registration=URL(data["registration"]),
            summary=data["summary"],
            tags=data["tags"],
            title=data["title"],
            total_downloads=data["totalDownloads"],
            verified=data["verified"],
            version=Version.parse(data["version"]),
            versions=[
                SearchQueryPackageVersion.from_json(version)
                for version in data["versions"]
            ],
            vulnerabilities=data["vulnerabilities"],
        )

    def to_json(self) -> dict:
        return {
            "@id": str(self.id_url),
            "@type": self.type,
            "authors": self.authors,
            "description": self.description,
            "iconUrl": str(self.icon_url),
            "id": self.id,
            "licenseUrl": str(self.license_url),
            "owners": self.owners,
            "packageTypes": [type_.to_json() for type_ in self.package_types],
            "projectUrl": str(self.project_url),
            "registration": str(self.registration),
            "summary": self.summary,
            "tags": self.tags,
            "title": self.title,
            "totalDownloads": self.total_downloads,
            "verified": self.verified,
            "version": str(self.version),
            "versions": [version.to_json() for version in self.versions],
            "vulnerabilities": self.vulnerabilities,
        }


@dataclass(slots=True)
class SearchQueryResponse:
    context: SearchQueryContext
    data: list[SearchQueryDataEntry]
    total_hits: int

    @classmethod
    def from_json(cls, data: dict) -> Self:
        return SearchQueryResponse(
            context=SearchQueryContext.from_json(data["@context"]),
            data=[
                SearchQueryDataEntry.from_json(data_entry)
                for data_entry in data["data"]
            ],
            total_hits=data["totalHits"],
        )

    def to_json(self) -> dict:
        return {
            "@context": str(self.context.to_json()),
            "data": [data_entry.to_json() for data_entry in self.data],
            "totalHits": self.total_hits,
        }
