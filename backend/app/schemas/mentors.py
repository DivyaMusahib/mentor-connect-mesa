from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MentorSummary(BaseModel):
    mentor_id: str
    name: str
    domain: Optional[str] = None
    company: Optional[str] = None
    master_sector: Optional[str] = None
    sectors_of_expertise: Optional[str] = None
    roles_of_expertise: Optional[str] = None
    seniority: Optional[str] = None
    ai_native: Optional[str] = None
    built_ai_product: Optional[str] = None
    ai_tools_of_expertise: Optional[str] = None
    city: Optional[str] = None
    quality_of_mentorship: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MentorDetail(MentorSummary):
    ai_sub_domain: Optional[str] = None
    tableau: Optional[str] = None
    hubspot: Optional[str] = None
    google_analytics: Optional[str] = None
    jira: Optional[str] = None
    excel: Optional[str] = None
    mixpanel: Optional[str] = None
    activities_participated: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class MentorFilters(BaseModel):
    domain: Optional[str] = None
    sector: Optional[str] = None
    role: Optional[str] = None
    seniority: Optional[str] = None
    ai_tools: Optional[str] = None
    search: Optional[str] = None
