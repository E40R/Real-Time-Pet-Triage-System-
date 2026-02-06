"""
Pydantic models for structured health analysis
Separates data structures from business logic
"""
from pydantic import BaseModel, Field
from typing import Optional


class SymptomAnalysis(BaseModel):
    """Structured symptom analysis"""
    symptoms_identified: list[str] = Field(
        description="List of symptoms mentioned",
        default_factory=list
    )
    duration: Optional[str] = Field(
        description="Duration of symptoms if mentioned",
        default=None
    )
    severity_indicators: list[str] = Field(
        description="Indicators of severity",
        default_factory=list
    )
    pet_type: Optional[str] = Field(
        description="Type of pet (dog, cat, etc.)",
        default=None
    )
    age_mentioned: Optional[str] = Field(
        description="Pet age if mentioned",
        default=None
    )


class HealthOverview(BaseModel):
    """Overall health assessment with safety guardrails"""
    health_overview: str = Field(
        description="Brief health summary"
    )
    symptom_analysis: SymptomAnalysis = Field(
        description="Detailed symptom breakdown"
    )
    risk_level: str = Field(
        description="Must be one of: LOW, MODERATE, HIGH, or EMERGENCY"
    )
    recommendations: list[str] = Field(
        description="Actionable recommendations",
        default_factory=list
    )
    safety_flags: list[str] = Field(
        description="Safety concerns and disclaimers",
        default_factory=list
    )
    requires_vet: bool = Field(
        description="Whether immediate vet visit is needed"
    )
