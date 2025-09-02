"""Script downloader for individual workload scripts from git repository using SSH."""

import subprocess
import time
from pathlib import Path

from loguru import logger

from ..config.settings import ParserConfig


class ScriptDownloader:
    """Downloads individual workload scripts from git repository using SSH."""

    def __init__(self, base_url: str | None = None, cache_dir: str | None = None):
        """Initialize script downloader.

        Args:
            base_url: SSH git URL (e.g., git@github.com:owner/repo.git)
            cache_dir: Local directory to cache downloaded scripts
        """
        config = ParserConfig()
        self.base_url = base_url or config.SCRIPTS_BASE_URL
        self.cache_dir = Path(cache_dir or config.SCRIPTS_CACHE_DIR).expanduser()
        self.cache_ttl = config.SCRIPTS_CACHE_TTL

        # Convert HTTPS raw URL to SSH git URL
        if self.base_url.startswith("https://raw.githubusercontent.com/"):
            # Convert: https://raw.githubusercontent.com/AMD-DEAE-CEME/epdw2.0_parser_scripts/main
            # To: git@github.com:AMD-DEAE-CEME/epdw2.0_parser_scripts.git
            parts = self.base_url.replace(
                "https://raw.githubusercontent.com/", ""
            ).split("/")
            if len(parts) >= 2:
                owner_repo = parts[0] + "/" + parts[1]
                self.git_url = f"git@github.com:{owner_repo}.git"
                self.branch = parts[2] if len(parts) > 2 else "main"
            else:
                raise ValueError(f"Invalid raw GitHub URL format: {self.base_url}")
        else:
            # Assume it's already a git URL
            self.git_url = self.base_url
            self.branch = "main"

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Script cache directory: {self.cache_dir}")
        logger.debug(f"Git repository: {self.git_url}")
        logger.debug(f"Git branch: {self.branch}")

    def get_script(self, workload: str, script_name: str = "extractor.sh") -> Path:
        """Get script file path, downloading if not cached or outdated.

        Args:
            workload: Workload name (e.g., 'nginx', 'redis')
            script_name: Script filename (default: 'extractor.sh')

        Returns:
            Path to the local script file

        Raises:
            RuntimeError: If script download fails
        """
        script_path = self.cache_dir / workload / script_name

        if self._should_download(script_path):
            logger.info(f"Downloading {workload} script...")
            self._download_script(workload, script_name, script_path)
            self._make_executable(script_path)
            logger.info(f"✅ Downloaded {workload} script to {script_path}")
        else:
            logger.debug(f"Using cached {workload} script: {script_path}")

        return script_path

    def _should_download(self, script_path: Path) -> bool:
        """Check if script needs downloading (not exists or expired cache).

        Args:
            script_path: Path to the script file

        Returns:
            True if script should be downloaded
        """
        if not script_path.exists():
            return True

        # Check if file is older than cache TTL
        age = time.time() - script_path.stat().st_mtime
        return age > self.cache_ttl

    def _download_script(
        self, workload: str, script_name: str, target_path: Path
    ) -> None:
        """Download single script file using git operations.

        Args:
            workload: Workload name
            script_name: Script filename
            target_path: Local path to save the script

        Raises:
            RuntimeError: If download fails
        """
        try:
            # Create a temporary directory for git operations
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Clone the repository (shallow, sparse checkout for efficiency)
                logger.debug(f"Cloning repository to {temp_path}")
                clone_cmd = [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    self.branch,
                    "--filter",
                    "blob:none",
                    "--sparse",
                    self.git_url,
                    str(temp_path),
                ]

                result = subprocess.run(
                    clone_cmd, capture_output=True, text=True, timeout=60
                )

                if result.returncode != 0:
                    raise RuntimeError(f"Git clone failed: {result.stderr}")

                # Sparse checkout only the specific workload directory
                logger.debug(f"Setting up sparse checkout for {workload}")
                subprocess.run(
                    ["git", "sparse-checkout", "set", f"workloads/{workload}/"],
                    cwd=temp_path,
                    capture_output=True,
                    check=True,
                )

                # Copy the script file
                source_script = temp_path / "workloads" / workload / script_name
                if not source_script.exists():
                    raise RuntimeError(
                        f"Script {script_name} not found in workload {workload}"
                    )

                # Ensure target directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the script
                import shutil

                shutil.copy2(source_script, target_path)

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Git operation timed out for {workload}") from None
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git operation failed for {workload}: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error downloading {workload} script: {e}"
            ) from e

    def _make_executable(self, script_path: Path) -> None:
        """Make script file executable.

        Args:
            script_path: Path to the script file
        """
        try:
            script_path.chmod(0o755)
            logger.debug(f"Made {script_path} executable")
        except Exception as e:
            logger.warning(f"Could not make {script_path} executable: {e}")

    def clear_cache(self, workload: str | None = None) -> None:
        """Clear script cache.

        Args:
            workload: Specific workload to clear, or None for all
        """
        if workload:
            workload_dir = self.cache_dir / workload
            if workload_dir.exists():
                import shutil

                shutil.rmtree(workload_dir)
                logger.info(f"Cleared cache for {workload}")
        else:
            import shutil

            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cleared all script cache")

    def get_cache_info(self) -> dict:
        """Get information about cached scripts.

        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_dir.exists():
            return {"total_scripts": 0, "cache_size": 0, "workloads": []}

        workloads = []
        total_size = 0

        for workload_dir in self.cache_dir.iterdir():
            if workload_dir.is_dir():
                workload_name = workload_dir.name
                script_count = len(list(workload_dir.glob("*.sh")))
                workload_size = sum(
                    f.stat().st_size for f in workload_dir.rglob("*") if f.is_file()
                )

                workloads.append(
                    {
                        "name": workload_name,
                        "script_count": script_count,
                        "size_bytes": workload_size,
                    }
                )
                total_size += workload_size

        return {
            "total_scripts": sum(w["script_count"] for w in workloads),
            "cache_size": total_size,
            "workloads": workloads,
        }
