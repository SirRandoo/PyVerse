from asyncio import Lock
from logging import getLogger
from logging import Logger
from typing import Final

from aiohttp import ClientSession
from yarl import URL

from .data import SearchQueryDataEntry
from .data import SearchQueryResponse
from .errors import NuGetError
from .errors import PackageQueryTimeoutError
from .errors import ServiceTimeoutError

__all__ = ["NuGetClient"]


class NuGetClient:
    """A mini client for interacting with the NuGet package registry.

    Attributes:
        NUGET_PACKAGE_SOURCE_URL:
            The URL of the official NuGet package registry's index.json.
    """

    NUGET_PACKAGE_SOURCE_URL: Final[str] = (
        "https://api.nuget.org/v3/index.json"
    )

    SEARCH_QUERY_SERVICE_NAME: Final[str] = "SearchQueryService"

    def __init__(self):
        self._session = ClientSession()
        self._catalog_lock: Lock = Lock()
        self._logger: Logger = getLogger(__name__)
        self._catalog_query_url: URL | None = None

    async def query_package(
        self, package_name: str, include_prereleases: bool = True
    ) -> list[SearchQueryDataEntry] | None:
        """Queries the NuGet package registry for a specific package.

        Args:
            package_name:
                The name of the package that should be queried for.
            include_prereleases:
                Whether to include prerelease versions of the package in the
                results.
        Returns:
            The list of packages that match the package name.
        """
        try:
            response = await self._query_package(
                package_name, include_prereleases
            )
        except PackageQueryTimeoutError as e:
            self._logger.error(f"Nuget query timed out", exc_info=e)

            return None

        return response.data

    async def _query_package(
        self, package_name: str, include_prereleases: bool = True
    ) -> SearchQueryResponse:
        if not self._catalog_query_url:
            await self._init_catalog_query_url()

        request_url = self._catalog_query_url.with_query(
            {"q": package_name, "prerelease": include_prereleases}
        )

        async with self._session.get(request_url) as response:
            if not response.ok:
                raise PackageQueryTimeoutError()

            return await response.json()

    async def _init_catalog_query_url(self):
        if self._catalog_query_url:
            return

        await self._catalog_lock.acquire()

        if self._catalog_query_url:
            self._catalog_lock.release()

            return

        async with self._session.get(self.NUGET_PACKAGE_SOURCE_URL) as resp:
            if not resp.ok:
                raise ServiceTimeoutError()

            response = await resp.json()
            for resource in response.get("resources", {}):
                resource_type = resource.get("@type", None)

                if resource_type != NuGetClient.SEARCH_QUERY_SERVICE_NAME:
                    continue

                query_id = resource.get("id", None)

                if not query_id:
                    self._catalog_lock.release()

                    raise NuGetError(
                        f"The 'id' property is missing from "
                        f"{NuGetClient.SEARCH_QUERY_SERVICE_NAME}'s service"
                        f"definition."
                    )

                self._catalog_query_url = URL(query_id)
                self._catalog_lock.release()

                return
