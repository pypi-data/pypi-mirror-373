"""
Data models and schemas for MCP as a Judge.

This module contains all Pydantic models used for data validation,
serialization, and API contracts.
"""

from pydantic import BaseModel, Field


class JudgeResponse(BaseModel):
    """Response model for all judge tool evaluations.

    This standardized response format ensures consistent feedback
    across all evaluation tools.
    """

    approved: bool = Field(
        description="Whether the plan/code is approved for implementation"
    )
    required_improvements: list[str] = Field(
        default_factory=list,
        description="Specific improvements needed (empty if approved)",
    )
    feedback: str = Field(
        description="Detailed explanation of the decision and recommendations"
    )


class ObstacleResolutionDecision(BaseModel):
    """Schema for eliciting user decision when agent encounters obstacles.

    Used by the raise_obstacle tool to capture user choices when
    the agent cannot proceed due to blockers or missing information.
    """

    chosen_option: str = Field(
        description="The option the user chooses from the provided list"
    )
    additional_context: str = Field(
        default="",
        description="Any additional context or modifications the user provides",
    )


class RequirementsClarification(BaseModel):
    """Schema for eliciting missing requirements from user.

    Used by the elicit_missing_requirements tool to capture
    clarified requirements when the original request is unclear.
    """

    clarified_requirements: str = Field(
        description="The clarified or additional requirements"
    )
    priority_level: str = Field(
        description="Priority level: 'high', 'medium', or 'low'"
    )
    additional_context: str = Field(
        default="", description="Any additional context about the requirements"
    )


class WorkflowGuidance(BaseModel):
    """Schema for workflow guidance responses.

    Used by the get_workflow_guidance tool to provide
    structured guidance on which tools to use next.
    """

    next_tool: str = Field(
        description="The specific MCP tool that should be called next: 'judge_coding_plan', 'judge_code_change', 'raise_obstacle', or 'elicit_missing_requirements'"
    )
    reasoning: str = Field(
        description="Clear explanation of why this tool should be used next"
    )
    preparation_needed: list[str] = Field(
        default_factory=list,
        description="List of things that need to be prepared before calling the recommended tool",
    )
    guidance: str = Field(
        description="Detailed step-by-step guidance for the AI assistant"
    )


class ResearchValidationResponse(BaseModel):
    """Schema for research validation responses.

    Used by the _validate_research_quality function to parse
    LLM responses about research quality and design alignment.
    """

    research_adequate: bool = Field(
        description="Whether the research is comprehensive enough"
    )
    design_based_on_research: bool = Field(
        description="Whether the design is properly based on research"
    )
    issues: list[str] = Field(
        default_factory=list, description="List of specific issues if any"
    )
    feedback: str = Field(
        description="Detailed feedback on research quality and design alignment"
    )


# Type aliases for better code readability
ToolResponse = JudgeResponse
ElicitationResponse = str
