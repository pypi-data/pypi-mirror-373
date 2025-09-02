"""Pydantic models for structured output schema."""

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    """Statistics model for individual metrics."""

    metricName: str = Field(..., description="Name of the metric")
    metricValue: str = Field(..., description="Value of the metric")


class Instance(BaseModel):
    """Instance model containing statistics."""

    instanceIndex: int = Field(..., description="Index of the instance")
    statistics: list[Statistics] = Field(
        ..., description="List of statistics for this instance"
    )


class Iteration(BaseModel):
    """Iteration model containing instances."""

    iterationIndex: int = Field(..., description="Index of the iteration")
    instances: list[Instance] = Field(
        ..., description="List of instances for this iteration"
    )


class StructuredResults(BaseModel):
    """Simplified results model containing iterations directly."""

    iterations: list[Iteration] = Field(..., description="List of iterations")
