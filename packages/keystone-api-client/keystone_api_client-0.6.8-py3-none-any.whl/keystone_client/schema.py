"""Schema objects used to define available API endpoints."""

from dataclasses import dataclass
from os import path


class Endpoint(str):
    """API endpoint agnostic to the baseAPI URL."""

    def join_url(self, base: str, *append) -> str:
        """Join the endpoint with a base URL.

        This method returns URLs in a format that avoids trailing slash
        redirects from the Keystone API.

        Args:
            base: The base URL.
            *append: Partial paths to append onto the url.

        Returns:
            The base URL join with the endpoint.
        """

        url = path.join(base, self)
        for partial_path in filter(lambda x: x is not None, append):
            url = path.join(url, str(partial_path))

        return url.rstrip('/') + '/'


@dataclass
class Schema:
    """Schema defining the complete set of API endpoints."""

    allocations: Endpoint = Endpoint("allocations/allocations")
    clusters: Endpoint = Endpoint("allocations/clusters")
    requests: Endpoint = Endpoint("allocations/requests")
    teams: Endpoint = Endpoint("users/teams")
    memberships: Endpoint = Endpoint("users/membership")
    users: Endpoint = Endpoint("users/users")
