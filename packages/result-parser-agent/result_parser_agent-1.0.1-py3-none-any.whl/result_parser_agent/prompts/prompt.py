"""Prompts for the results parser agent."""


def get_llm_processing_prompt(raw_output: str, target_metrics: list[str]) -> str:
    """Get a simplified LLM prompt for extracting target metrics from raw output."""
    return f"""You are given raw benchmark output and a list of target metrics to extract.

RAW OUTPUT:
{raw_output}

TARGET METRICS TO EXTRACT:
{target_metrics}

Instructions:
- Extract only the exact values for the target metrics listed above, as they appear in the raw output.
- Use the exact metric names as provided in the target_metrics list.
- Do not invent, estimate, or modify any values. You must use the exact values as they appear in the raw output.
- Do not create fake runs, iterations, or instances; only use what is present in the raw output.
- Do not use placeholder values like "N/A", "null", or "undefined".
- For each metric, provide its value in a structured JSON format, including any run, iteration, or instance information if present in the raw output.
- If a target metric is not present in the raw output, do not include it in the JSON.
- Map the values to the correct metric names in the target_metrics list.
- Map the correct iteration and instance indices to the values.

Return only the JSON structure with the extracted data. Do not include any explanations or extra text.
"""
