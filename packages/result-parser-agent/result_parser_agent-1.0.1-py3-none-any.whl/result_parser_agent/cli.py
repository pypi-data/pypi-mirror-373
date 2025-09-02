"""Command-line interface for the Results Parser Agent."""

import asyncio
import json
import sys
from pathlib import Path

import typer
from loguru import logger

from .agent.parser_agent import ResultsParserAgent
from .config.settings import ParserConfig, settings
from .models.schema import StructuredResults
from .tools.registry import ToolRegistry

# Global tool registry instance for CLI operations
_cli_tool_registry = None


def get_cli_tool_registry(silent: bool = True) -> ToolRegistry:
    """Get or create the CLI tool registry instance."""
    global _cli_tool_registry
    if _cli_tool_registry is None:
        _cli_tool_registry = ToolRegistry()
    return _cli_tool_registry


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    logger.remove()

    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    if verbose:
        log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if verbose else "INFO",
        colorize=True,
    )


def validate_input_path(input_path: str) -> Path:
    """Validate and return input path."""
    path = Path(input_path)
    if not path.exists():
        raise typer.BadParameter(f"Input path does not exist: {input_path}")
    return path


def validate_metrics(metrics: list[str]) -> list[str]:
    """Validate metrics list."""
    if not metrics:
        raise typer.BadParameter("At least one metric must be specified")
    return [metric.strip() for metric in metrics]


def validate_workload(workload: str, tool_registry: ToolRegistry) -> str:
    """Validate workload with case-insensitive matching."""
    available_workloads = tool_registry.list_workloads()

    # Case-insensitive workload matching
    workload_lower = workload.lower()
    matched_workload = None

    for available_workload in available_workloads:
        if available_workload.lower() == workload_lower:
            matched_workload = available_workload
            break

    if not matched_workload:
        logger.error(f"❌ Invalid workload: {workload}")
        logger.info("💡 Use 'result-parser registry' to see available workloads")
        logger.info(f"💡 Available workloads: {', '.join(available_workloads)}")
        sys.exit(1)

    return matched_workload


def load_config(provider: str | None = None, model: str | None = None) -> ParserConfig:
    """Load configuration from environment variables and CLI options."""
    config = settings

    if provider:
        config.LLM_PROVIDER = provider
        logger.info(f"🔧 Overriding provider to: {provider}")

    if model:
        config.LLM_MODEL = model
        logger.info(f"🔧 Overriding model to: {model}")

    return config


def save_output(results: StructuredResults, output_path: str) -> None:
    """Save results to output file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(results.model_dump(), f, indent=2)

    logger.info(f"💾 Results saved to: {output_file}")


def analyze_results(results: StructuredResults, requested_metrics: list[str]) -> None:
    """Analyze and log extraction results."""
    if not results.iterations:
        logger.warning("⚠️  No data extracted from the input files")
        logger.info("🔍 This could indicate:")
        logger.info("   - Requested metrics don't exist in the data")
        logger.info("   - Files are empty or don't contain the expected format")
        logger.info("   - Directory structure doesn't match expected pattern")
        logger.info("💡 Try:")
        logger.info("   - Check if the requested metrics exist in your data files")
        logger.info("   - Verify the input path contains the expected file structure")
        logger.info("   - Use --verbose flag for detailed debugging information")
        return

    total_iterations = len(results.iterations)
    total_instances = sum(len(iter.instances) for iter in results.iterations)
    total_metrics = sum(
        len(inst.statistics) for iter in results.iterations for inst in iter.instances
    )

    logger.info("📊 Extraction analysis:")
    logger.info(f"   - Total iterations: {total_iterations}")
    logger.info(f"   - Total instances: {total_instances}")
    logger.info(f"   - Total metrics extracted: {total_metrics}")

    # Validate completeness
    agent = ResultsParserAgent()
    is_complete = agent.validate_extraction_completeness(results, requested_metrics)

    if is_complete:
        logger.success("✅ All requested metrics successfully extracted!")
    else:
        logger.warning("⚠️  Some requested metrics may be missing")


def show_registry_info() -> None:
    """Display tool registry information."""
    try:
        tool_registry = get_cli_tool_registry(silent=False)
        registry_info = tool_registry.get_registry_info()

        logger.info("📋 Tool Registry Information:")
        logger.info(f"   - Total workloads: {registry_info.get('total_workloads', 0)}")
        logger.info(
            f"   - Available workloads: {', '.join(registry_info.get('workloads', [])) if registry_info.get('workloads') else 'None'}"
        )
        logger.info(f"   - Registry source: {registry_info.get('source', 'Unknown')}")
        logger.info(
            f"   - Scripts directory: {registry_info.get('scripts_directory', 'Unknown')}"
        )

        # Show script cache information
        script_cache = registry_info.get("script_cache", {})
        if script_cache:
            logger.info("   - Script Cache:")
            logger.info(
                f"     * Total cached scripts: {script_cache.get('total_scripts', 0)}"
            )
            logger.info(f"     * Cache size: {script_cache.get('cache_size', 0)} bytes")
            if script_cache.get("workloads"):
                logger.info("     * Cached workloads:")
                for workload_info in script_cache["workloads"]:
                    logger.info(
                        f"       - {workload_info['name']}: {workload_info['script_count']} scripts ({workload_info['size_bytes']} bytes)"
                    )

        if registry_info.get("workloads"):
            logger.info("   - Workload details:")
            for workload in registry_info["workloads"]:
                logger.info(f"     * {workload}")
        else:
            logger.info("   - No workloads registered yet")

    except Exception as e:
        logger.error(f"❌ Error getting registry info: {e}")


def manage_script_cache(
    action: str = typer.Argument(..., help="Cache action: info, clear, clear-all"),
    workload: str = typer.Option(
        None, "--workload", "-w", help="Specific workload for clear action"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Manage script cache for downloaded workload scripts."""
    setup_logging(verbose)

    try:
        tool_registry = get_cli_tool_registry(silent=True)

        if action == "info":
            cache_info = tool_registry.script_downloader.get_cache_info()
            logger.info("📦 Script Cache Information:")
            logger.info(
                f"   - Total cached scripts: {cache_info.get('total_scripts', 0)}"
            )
            logger.info(f"   - Cache size: {cache_info.get('cache_size', 0)} bytes")
            logger.info(
                f"   - Cache directory: {tool_registry.script_downloader.cache_dir}"
            )

            if cache_info.get("workloads"):
                logger.info("   - Cached workloads:")
                for workload_info in cache_info["workloads"]:
                    logger.info(
                        f"     * {workload_info['name']}: {workload_info['script_count']} scripts ({workload_info['size_bytes']} bytes)"
                    )
            else:
                logger.info("   - No scripts cached yet")

        elif action == "clear":
            if not workload:
                logger.error("❌ Workload name required for 'clear' action")
                logger.info(
                    "💡 Use: result-parser cache clear --workload <workload_name>"
                )
                sys.exit(1)

            tool_registry.clear_script_cache(workload)
            logger.info(f"✅ Cleared script cache for workload: {workload}")

        elif action == "clear-all":
            tool_registry.clear_script_cache()
            logger.info("✅ Cleared all script cache")

        else:
            logger.error(f"❌ Invalid action: {action}")
            logger.info("💡 Valid actions: info, clear, clear-all")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Cache management failed: {e}")
        if verbose:
            import traceback

            logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


def add_workload(
    name: str = typer.Argument(..., help="Workload name"),
    metrics: str = typer.Option(
        ..., "--metrics", "-m", help="Comma-separated list of metrics"
    ),
    script: str = typer.Option(
        "extractor.sh", "--script", "-s", help="Script filename"
    ),
    description: str = typer.Option(
        "", "--description", "-d", help="Workload description"
    ),
    status: str = typer.Option(
        "active", "--status", "-st", help="Workload status (active, inactive)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Add a new workload to the registry."""
    setup_logging(verbose)

    try:
        tool_registry = get_cli_tool_registry(silent=True)

        # Prepare workload data
        workload_data = {
            "workloadName": name,
            "metrics": [metric.strip() for metric in metrics.split(",")],
            "script": script,
            "description": description,
            "status": status,
        }

        # Add workload via registry
        result = tool_registry.add_workload(workload_data)

        if result["success"]:
            logger.success(f"✅ {result['message']}")
            if "note" in result:
                logger.info(f"💡 {result['note']}")
        else:
            logger.error(f"❌ {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Failed to add workload: {e}")
        if verbose:
            import traceback

            logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


def update_workload(
    name: str = typer.Argument(..., help="Workload name to update"),
    metrics: str = typer.Option(
        None, "--metrics", "-m", help="Comma-separated list of metrics"
    ),
    script: str = typer.Option(None, "--script", "-s", help="Script filename"),
    description: str = typer.Option(
        None, "--description", "-d", help="Workload description"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Update an existing workload in the registry."""
    setup_logging(verbose)

    try:
        tool_registry = get_cli_tool_registry(silent=True)

        # Prepare update data
        updates = {}
        if metrics:
            updates["metrics"] = [metric.strip() for metric in metrics.split(",")]
        if script:
            updates["script"] = script
        if description:
            updates["description"] = description

        if not updates:
            logger.warning("⚠️  No updates specified")
            logger.info(
                "💡 Use --metrics, --script, or --description to specify changes"
            )
            return

        # Update workload via registry
        result = tool_registry.update_workload(name, updates)

        if result["success"]:
            logger.success(f"✅ {result['message']}")
            if "note" in result:
                logger.info(f"💡 {result['note']}")
        else:
            logger.error(f"❌ {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Failed to update workload: {e}")
        if verbose:
            import traceback

            logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


def show_workload(
    name: str = typer.Argument(..., help="Workload name to show details for"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Show detailed information about a specific workload."""
    setup_logging(verbose)

    try:
        tool_registry = get_cli_tool_registry(silent=True)

        # Get workload details
        workload = tool_registry.get_workload_details(name)

        if not workload:
            logger.error(f"❌ Workload '{name}' not found")
            sys.exit(1)

        logger.info(f"🔧 Workload Details: {workload.get('workloadName', 'Unknown')}")
        logger.info(f"   - ID: {workload.get('workloadId', 'Unknown')}")
        logger.info(f"   - Metrics: {', '.join(workload.get('metrics', []))}")
        logger.info(f"   - Script: {workload.get('script', 'Unknown')}")
        if workload.get("description"):
            logger.info(f"   - Description: {workload['description']}")
        logger.info(f"   - Created: {workload.get('createdOn', 'Unknown')}")
        logger.info(f"   - Modified: {workload.get('lastModifiedOn', 'Unknown')}")
        logger.info(
            f"   - Script Status: {workload.get('script_cache_status', 'Unknown')}"
        )
        if workload.get("script_local_path") != "N/A":
            logger.info(f"   - Local Path: {workload['script_local_path']}")

    except Exception as e:
        logger.error(f"❌ Failed to get workload details: {e}")
        if verbose:
            import traceback

            logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


def parse_results(
    input_path: str = typer.Argument(..., help="Path to file or directory to parse"),
    metrics: str = typer.Option(
        ..., "--metrics", "-m", help="Comma-separated list of metrics to extract"
    ),
    workload: str = typer.Option(
        ..., "--workload", "-w", help="Workload name for tool selection"
    ),
    output: str = typer.Option(
        "results.json", "--output", "-o", help="Output file path"
    ),
    provider: str = typer.Option(None, "--provider", "-p", help="LLM provider to use"),
    model: str = typer.Option(None, "--model", help="LLM model to use"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """Parse benchmark results and extract metrics."""

    setup_logging(verbose)

    try:
        # Validate workload (case-insensitive)
        tool_registry = get_cli_tool_registry(silent=True)
        workload = validate_workload(workload, tool_registry)

        # Validate other inputs
        validated_path = validate_input_path(input_path)
        metric_list = validate_metrics(metrics.split(","))

        # Load configuration
        load_config(provider, model)

        logger.info(f"📁 Processing results from: {validated_path}")
        logger.info(f"📊 Target metrics: {metric_list}")
        logger.info(f"🔧 Workload: {workload}")

        # Initialize agent and parse results
        agent = ResultsParserAgent()

        async def run_parsing():
            return await agent.parse_results(str(validated_path), metric_list, workload)

        results = asyncio.run(run_parsing())

        # Analyze and save results
        analyze_results(results, metric_list)
        save_output(results, output)

        if results.iterations:
            logger.success("🎉 Parsing completed successfully!")
            logger.info(f"✅ Used workload-specific tool: {workload}")
        else:
            logger.warning("⚠️  No data extracted - check your input and metrics")

    except Exception as e:
        logger.error(f"❌ Parsing failed: {e}")
        if verbose:
            import traceback

            logger.error(f"🔍 Full traceback:\n{traceback.format_exc()}")
        sys.exit(1)


# Create the main Typer app
app = typer.Typer(
    name="result-parser",
    help="Results Parser Agent - Extract metrics from benchmark result files",
    add_completion=False,
)

# Add commands to the app
app.command(name="parse")(parse_results)
app.command(name="registry")(show_registry_info)
app.command(name="cache")(manage_script_cache)
app.command(name="add-workload")(add_workload)
app.command(name="update-workload")(update_workload)
app.command(name="show-workload")(show_workload)

if __name__ == "__main__":
    app()
