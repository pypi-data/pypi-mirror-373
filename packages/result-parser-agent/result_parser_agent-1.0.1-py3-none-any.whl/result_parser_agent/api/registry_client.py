"""
Simple API client for parser registry operations.

This client provides the essential functionality needed for the CLI and registry
operations, integrating with the existing Pydantic configuration.
"""

import logging
from typing import Any

import requests
from requests.exceptions import RequestException

from ..config.settings import APIConfig

logger = logging.getLogger(__name__)


class RegistryClient:
    """
    Simple client for parser registry API operations.

    Provides only the essential functionality needed for CLI and registry operations.
    """

    def __init__(self, config: APIConfig | None = None):
        """Initialize the registry client."""
        self.config = config or APIConfig()
        self.base_url = self.config.PARSER_REGISTRY_URL.rstrip("/")
        self.timeout = self.config.PARSER_REGISTRY_TIMEOUT

        # Simple session for requests
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        logger.info(f"Initialized registry client for {self.base_url}")

    def _get_url(self, endpoint: str = "") -> str:
        """Construct full URL for API endpoint."""
        return f"{self.base_url}/parserRegistry{endpoint}"

    def _make_request(
        self, method: str, endpoint: str = "", data: dict | None = None
    ) -> dict[str, Any]:
        """Make HTTP request and return response data."""
        try:
            url = self._get_url(endpoint)
            kwargs = {"timeout": self.timeout}

            if data:
                kwargs["json"] = data

            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_all_workloads(self) -> list[dict[str, Any]]:
        """Get all workloads from the registry."""
        try:
            data = self._make_request("GET")
            workloads = data if isinstance(data, list) else data.get("data", [])
            logger.info(f"Retrieved {len(workloads)} workloads from registry")
            return workloads
        except Exception as e:
            logger.error(f"Failed to get workloads: {e}")
            return []

    def get_workload_by_name(self, workload_name: str) -> dict[str, Any] | None:
        """Get a specific workload by name (case-insensitive)."""
        try:
            workloads = self.get_all_workloads()
            for workload in workloads:
                if workload.get("workloadName", "").lower() == workload_name.lower():
                    return workload
            return None
        except Exception as e:
            logger.error(f"Failed to get workload '{workload_name}': {e}")
            return None

    def list_workload_names(self) -> list[str]:
        """Get list of workload names from the registry."""
        try:
            workloads = self.get_all_workloads()
            return [
                w.get("workloadName", "") for w in workloads if w.get("workloadName")
            ]
        except Exception:
            return []

    def workload_exists(self, workload_name: str) -> bool:
        """Check if a workload exists in the registry."""
        return self.get_workload_by_name(workload_name) is not None

    def get_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get extraction tool info for a specific workload."""
        workload = self.get_workload_by_name(workload_name)
        if workload:
            return {
                "script": workload.get("script", ""),
                "description": workload.get("description", ""),
                "metrics": workload.get("metrics", []),
                "status": workload.get("status", "active"),
            }
        return None

    def create_workload(self, workload_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new workload in the registry.

        Args:
            workload_data: Dictionary containing workload information

        Returns:
            Created workload data or None if creation failed
        """
        try:
            logger.info(
                f"Creating workload: {workload_data.get('workloadName', 'Unknown')}"
            )
            result = self._make_request("POST", data=workload_data)
            logger.info(
                f"Successfully created workload: {workload_data.get('workloadName', 'Unknown')}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to create workload: {e}")
            return None

    def update_workload(
        self, workload_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update an existing workload in the registry.

        Args:
            workload_id: ID of the workload to update
            updates: Dictionary containing fields to update

        Returns:
            Updated workload data or None if update failed
        """
        try:
            logger.info(f"Updating workload ID: {workload_id}")
            result = self._make_request("PUT", endpoint=f"/{workload_id}", data=updates)
            logger.info(f"Successfully updated workload ID: {workload_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to update workload ID {workload_id}: {e}")
            return None

    def get_workload_by_id(self, workload_id: str) -> dict[str, Any] | None:
        """Get a specific workload by ID.

        Args:
            workload_id: ID of the workload to retrieve

        Returns:
            Workload data or None if not found
        """
        try:
            result = self._make_request("GET", endpoint=f"/{workload_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get workload ID {workload_id}: {e}")
            return None

    def delete_workload(self, workload_id: str) -> bool:
        """Delete a workload from the registry.

        Args:
            workload_id: ID of the workload to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            logger.info(f"Deleting workload ID: {workload_id}")
            self._make_request("DELETE", endpoint=f"/{workload_id}")
            logger.info(f"Successfully deleted workload ID: {workload_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete workload ID {workload_id}: {e}")
            return False

    def close(self):
        """Close the client session."""
        self.session.close()
        logger.info("Registry client session closed")


# Convenience function to create client
def create_registry_client() -> RegistryClient:
    """Create a registry client instance."""
    return RegistryClient()
