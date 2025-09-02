"""Results parser agent with tool registry integration."""

from typing import Any

from langchain_core.language_models import LanguageModelLike
from loguru import logger

from ..config.settings import settings
from ..models.schema import StructuredResults
from ..prompts.prompt import get_llm_processing_prompt
from ..tools.registry import ToolRegistry


class ResultsParserAgent:
    """Results parser agent with tool registry integration."""

    # Class variable for tool registry
    _tool_registry = None

    def __init__(self):
        self.config = settings
        self.model = self._create_llm_model()
        self.structured_llm = self.model.with_structured_output(StructuredResults)

    @classmethod
    def _get_tool_registry(cls) -> ToolRegistry:
        """Get or create the tool registry instance for this class."""
        if cls._tool_registry is None:
            cls._tool_registry = ToolRegistry()
        return cls._tool_registry

    def _create_llm_model(self) -> LanguageModelLike:
        """Create LLM model based on configuration."""
        provider = self.config.LLM_PROVIDER

        if provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=self.config.LLM_MODEL,
                api_key=self.config.GROQ_API_KEY.get_secret_value(),
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.config.LLM_MODEL,
                api_key=self.config.OPENAI_API_KEY.get_secret_value(),
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=self.config.LLM_MODEL,
                api_key=self.config.ANTHROPIC_API_KEY.get_secret_value(),
            )
        elif provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(model=self.config.LLM_MODEL)
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=self.config.LLM_MODEL,
                api_key=self.config.GOOGLE_API_KEY.get_secret_value(),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def parse_results(
        self, input_path: str, metrics: list[str] = None, workload_name: str = None
    ) -> StructuredResults:
        """
        Parse results using workload-specific extraction tools.

        Args:
            input_path: Path to file or directory to parse
            metrics: List of metrics to extract
            workload_name: Name of the workload (for tool selection)

        Returns:
            StructuredResults with extracted data or empty results on failure
        """
        try:
            logger.info("🔧 Agent configuration:")
            logger.info(f"   - Provider: {self.config.LLM_PROVIDER}")
            logger.info(f"   - Model: {self.config.LLM_MODEL}")
            logger.info("   - Tool registry integration enabled")

            if workload_name:
                extraction_result = await self._try_workload_extraction(
                    workload_name, input_path, metrics
                )

                if extraction_result["success"]:
                    logger.info("✅ Data extraction successful, processing with LLM")
                    return await self._process_raw_output_with_llm(
                        extraction_result["raw_output"], metrics
                    )
                else:
                    error_msg = extraction_result.get("error", "Unknown error")
                    logger.error(f"❌ Data extraction failed: {error_msg}")
                    raise ValueError(
                        f"Data extraction failed for '{workload_name}': {error_msg}"
                    )

        except Exception as e:
            logger.error(f"❌ Error in parse_results: {e}")
            logger.warning("🔄 Returning empty results due to error in results parsing")
            return StructuredResults(iterations=[])

    async def _try_workload_extraction(
        self, workload_name: str, input_path: str, metrics: list[str]
    ) -> dict[str, Any]:
        """Try to extract data using workload-specific tool."""
        try:
            logger.info(f"🔧 Attempting data extraction for: {workload_name}")

            tool_registry = self._get_tool_registry()
            tool_info = tool_registry.get_workload_tool(workload_name)

            if not tool_info:
                logger.info(f"📝 No tool found for data extraction: {workload_name}")

            logger.info(f"🛠️  Using existing tool: {tool_info['script']}")
            result = tool_registry.execute_extraction_tool(
                workload_name, input_path, metrics
            )

            if result.get("success"):
                logger.info(f"✅ Data extraction successful for {workload_name}")
                return result
            else:
                logger.warning(f"⚠️  Data extraction failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            logger.error(f"❌ Error in data extraction: {e}")
            return {"success": False, "error": str(e)}

    async def _process_raw_output_with_llm(
        self, raw_output: str, metrics: list[str]
    ) -> StructuredResults:
        """Process raw output from data extraction tool with LLM for structured results."""
        try:
            logger.info("🔧 Processing raw output with LLM for structured results")
            logger.debug(f"📝 Raw output received: {raw_output}")

            prompt = get_llm_processing_prompt(raw_output, metrics)
            logger.debug(f"📝 Full prompt sent to LLM: {prompt}")

            structured_result = await self.structured_llm.ainvoke(prompt)

            logger.info("✅ Successfully processed raw output")
            return structured_result

        except Exception as e:
            logger.error(f"❌ Error processing raw output: {e}")
            return StructuredResults(iterations=[])

    def validate_extraction_completeness(
        self, results: StructuredResults, requested_metrics: list[str]
    ) -> bool:
        """Validate that data for all requested metrics was extracted."""
        if not results.iterations:
            logger.warning("⚠️  No iterations found in results")
            return False

        captured_metrics = set()
        for iteration in results.iterations:
            for instance in iteration.instances:
                for stat in instance.statistics:
                    captured_metrics.add(stat.metricName)

        missing_metrics = set(requested_metrics) - captured_metrics
        if missing_metrics:
            logger.warning(f"⚠️  Missing metrics: {missing_metrics}")
            return False

        logger.info(f"✅ All requested metrics captured: {list(captured_metrics)}")
        return True
