"""Tool Registry for workload-specific extraction tools."""

import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

from ..api import create_registry_client
from ..scripts.downloader import ScriptDownloader


class ToolRegistry:
    """Manages workload-specific extraction tools via API registry and script downloader."""

    def __init__(self, scripts_dir: str = "scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.api_client = create_registry_client()
        self.script_downloader = ScriptDownloader()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure scripts directory exists."""
        self.scripts_dir.mkdir(exist_ok=True)

    def get_workload_tool(self, workload_name: str) -> dict[str, Any] | None:
        """Get extraction tool for a specific workload (case-insensitive)."""
        try:
            return self.api_client.get_workload_tool(workload_name)
        except Exception as e:
            logger.error(f"Failed to get workload tool for '{workload_name}': {e}")
            return None

    def list_workloads(self) -> list[str]:
        """List all available workloads in registry."""
        try:
            return self.api_client.list_workload_names()
        except Exception as e:
            logger.error(f"Failed to list workloads: {e}")
            return []

    def execute_extraction_tool(
        self, workload_name: str, input_path: str, metrics: list[str]
    ) -> dict[str, Any]:
        """Execute an extraction tool for a specific workload."""
        try:
            workload_name = workload_name.lower()
            tool_info = self.get_workload_tool(workload_name)

            if not tool_info:
                logger.error(
                    f"❌ No extraction tool found for workload: {workload_name}"
                )
                return {"error": f"No extraction tool for {workload_name}"}

            # Get script path from API and download if needed
            script_name = tool_info.get("script", "extractor.sh")
            try:
                script_path = self.script_downloader.get_script(
                    workload_name, script_name
                )
                logger.info(f"🔧 Using script: {script_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download script for {workload_name}: {e}")
                return {"error": f"Script download failed: {e}"}

            logger.info(f"🔧 Executing extraction script: {script_path}")
            result = subprocess.run(
                [str(script_path), input_path, ",".join(metrics)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"✅ Data extraction successful for {workload_name}")
                return {
                    "success": True,
                    "raw_output": result.stdout.strip(),
                    "workload": workload_name,
                    "script": str(script_path),
                }
            else:
                logger.error(f"❌ Extraction script failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "workload": workload_name,
                    "script": str(script_path),
                }

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Data extraction script timed out for {workload_name}")
            return {"error": f"Script execution timed out for {workload_name}"}
        except Exception as e:
            logger.error(f"❌ Error executing data extraction script: {e}")
            return {"error": str(e)}

    def get_registry_info(self) -> dict[str, Any]:
        """Get registry information and statistics."""
        try:
            workloads = self.api_client.get_all_workloads()
            workload_names = [
                w.get("workloadName", "") for w in workloads if w.get("workloadName")
            ]

            # Get cache info from script downloader
            cache_info = self.script_downloader.get_cache_info()

            return {
                "total_workloads": len(workload_names),
                "workloads": workload_names,
                "scripts_directory": str(self.scripts_dir),
                "source": "API Registry + Git Scripts",
                "script_cache": cache_info,
            }
        except Exception as e:
            logger.error(f"Failed to get registry info: {e}")
            return {
                "total_workloads": 0,
                "workloads": [],
                "scripts_directory": str(self.scripts_dir),
                "source": "API Registry + Git Scripts (Error)",
                "error": str(e),
            }

    def clear_script_cache(self, workload: str | None = None) -> None:
        """Clear script cache.

        Args:
            workload: Specific workload to clear, or None for all
        """
        self.script_downloader.clear_cache(workload)

    def add_workload(self, workload_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new workload to the registry.

        Args:
            workload_data: Dictionary containing workload information
                - workloadName: Name of the workload
                - metrics: List of metrics to extract
                - script: Script filename
                - description: Optional description
                - status: Workload status

        Returns:
            Dictionary with operation result

        Raises:
            RuntimeError: If workload creation fails
        """
        try:
            workload_name = workload_data.get("workloadName")
            if not workload_name:
                raise ValueError("workloadName is required")

            # Check if workload already exists
            if self.api_client.workload_exists(workload_name):
                raise RuntimeError(f"Workload '{workload_name}' already exists")

            # Validate required fields
            metrics = workload_data.get("metrics", [])
            if not metrics:
                raise ValueError("At least one metric is required")

            script = workload_data.get("script", "extractor.sh")

            logger.info(f"➕ Adding workload: {workload_name}")
            logger.info(f"   - Metrics: {', '.join(metrics)}")
            logger.info(f"   - Script: {script}")
            if workload_data.get("description"):
                logger.info(f"   - Description: {workload_data['description']}")

            # Create workload via API
            result = self.api_client.create_workload(workload_data)

            if result:
                return {
                    "success": True,
                    "message": f"Workload '{workload_name}' successfully created",
                    "workload": workload_name,
                    "data": result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create workload '{workload_name}' via API",
                }

        except Exception as e:
            error_msg = f"Failed to add workload: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def update_workload(
        self, workload_name: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an existing workload in the registry.

        Args:
            workload_name: Name of the workload to update
            updates: Dictionary containing fields to update
                - metrics: List of metrics to extract
                - script: Script filename
                - description: Description
                - status: Workload status

        Returns:
            Dictionary with operation result

        Raises:
            RuntimeError: If workload update fails
        """
        try:
            # Check if workload exists
            if not self.api_client.workload_exists(workload_name):
                raise RuntimeError(f"Workload '{workload_name}' not found")

            # Get current workload data to get the ID
            current_workload = self.api_client.get_workload_by_name(workload_name)
            if not current_workload:
                raise RuntimeError(f"Could not retrieve workload '{workload_name}'")

            workload_id = current_workload.get("workloadId")
            if not workload_id:
                raise RuntimeError(f"Workload '{workload_name}' has no ID")

            # Prepare update data
            update_data = {}
            if "metrics" in updates:
                metrics = updates["metrics"]
                if not metrics:
                    raise ValueError("At least one metric is required")
                update_data["metrics"] = [metric.strip() for metric in metrics]

            if "script" in updates:
                update_data["script"] = updates["script"]

            if "description" in updates:
                update_data["description"] = updates["description"]

            if "status" in updates:
                update_data["status"] = updates["status"]

            if not update_data:
                return {"success": False, "error": "No updates specified"}

            # Update workload via API
            logger.info(f"🔄 Updating workload: {workload_name}")
            for field, value in update_data.items():
                logger.info(f"   - {field}: {value}")

            result = self.api_client.update_workload(workload_id, update_data)

            if result:
                return {
                    "success": True,
                    "message": f"Workload '{workload_name}' successfully updated",
                    "workload": workload_name,
                    "updates": update_data,
                    "data": result,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update workload '{workload_name}' via API",
                }

        except Exception as e:
            error_msg = f"Failed to update workload: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_workload_details(self, workload_name: str) -> dict[str, Any] | None:
        """Get detailed information about a specific workload.

        Args:
            workload_name: Name of the workload

        Returns:
            Dictionary with workload details or None if not found
        """
        try:
            workload = self.api_client.get_workload_by_name(workload_name)
            if not workload:
                return None

            # Add cache status information
            try:
                script_name = workload.get("script", "extractor.sh")
                script_path = self.script_downloader.get_script(
                    workload_name, script_name
                )
                cache_status = "✅ Cached" if script_path.exists() else "❌ Not cached"
                script_path_str = str(script_path) if script_path.exists() else "N/A"
            except Exception:
                cache_status = "❌ Download failed"
                script_path_str = "N/A"

            workload["script_cache_status"] = cache_status
            workload["script_local_path"] = script_path_str

            return workload

        except Exception as e:
            logger.error(f"Failed to get workload details for '{workload_name}': {e}")
            return None

    def close(self):
        """Close the registry and cleanup resources."""
        if hasattr(self, "api_client"):
            self.api_client.close()
