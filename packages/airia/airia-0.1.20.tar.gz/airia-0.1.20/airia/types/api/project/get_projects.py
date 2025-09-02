"""
Pydantic models for project management API responses.

This module defines the data structures returned by project-related endpoints,
including project listings and associated pipeline information.
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Pipeline(BaseModel):
    """
    Basic pipeline information associated with a project.

    Represents a simplified view of pipeline data within project contexts,
    containing only essential identification information.
    """

    id: str
    name: str


class DataSource(BaseModel):
    """
    Basic data source information associated with a project.
    """

    id: Optional[str] = None
    name: Optional[str] = None


class ProjectItem(BaseModel):
    """
    Comprehensive project information and metadata.

    This model represents a complete project entity with all associated resources,
    budget information, security settings, and organizational details. Projects
    serve as containers for pipelines, models, data sources, and other AI resources.

    Attributes:
        tenant_id: Unique identifier for the tenant/organization
        created_at: Timestamp when the project was created
        require_classification: Whether data classification is required
        budget_amount: Optional budget limit for the project
        budget_period: Time period for budget calculations
        budget_alert: Budget alert threshold configuration
        budget_stop: Whether to stop operations when budget is exceeded
        used_budget_amount: Amount of budget currently consumed
        resume_ends_at: When the project resumption period ends
        updated_at: Timestamp of last project modification
        pipelines: List of pipelines associated with this project
        models: AI models available in this project
        data_sources: Data sources configured for this project
        prompts: Prompt templates available in this project
        api_keys: API key configurations for external services
        memories: Memory/context storage configurations
        project_icon: Base64 encoded project icon image
        project_icon_id: Unique identifier for the project icon
        description: Human-readable project description
        project_type: Classification of project type
        classifications: Data classification settings
        id: Unique project identifier
        name: Human-readable project name
    """

    tenant_id: str = Field(alias="tenantId")
    created_at: datetime = Field(alias="createdAt")
    require_classification: bool = Field(alias="requireClassification")
    budget_amount: Optional[Any] = Field(None, alias="budgetAmount")
    budget_period: Optional[Any] = Field(None, alias="budgetPeriod")
    budget_alert: Optional[Any] = Field(None, alias="budgetAlert")
    budget_stop: bool = Field(alias="budgetStop")
    used_budget_amount: Optional[Any] = Field(None, alias="usedBudgetAmount")
    resume_ends_at: Optional[datetime] = Field(None, alias="resumeEndsAt")
    updated_at: datetime = Field(alias="updatedAt")
    pipelines: List[Pipeline]
    models: Optional[Any] = None
    data_sources: List[DataSource] = Field(alias="dataSources")
    prompts: Optional[Any] = None
    api_keys: Optional[Any] = Field(alias="apiKeys")
    memories: Optional[Any] = None
    project_icon: Optional[str] = Field(None, alias="projectIcon")
    project_icon_id: Optional[str] = Field(None, alias="projectIconId")
    description: Optional[str] = None
    project_type: str = Field(alias="projectType")
    classifications: Optional[Any] = None
    id: str
    name: str
