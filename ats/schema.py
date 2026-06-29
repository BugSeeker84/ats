"""Structured content the generator model must return.

The LLM produces ONLY this JSON (validated here); deterministic code renders it into
HTML. The model never emits layout, so styling can't drift between runs.
"""
from pydantic import BaseModel, Field


class SkillGroup(BaseModel):
    category: str
    items: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    title: str
    company: str
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    degree: str
    school: str
    dates: str = ""


class CertItem(BaseModel):
    name: str
    issuer: str = ""
    year: str = ""


class ResumeContent(BaseModel):
    title: str = ""  # JD-aligned positioning title, e.g. "Senior Backend Engineer"
    summary: str = ""
    skills: list[SkillGroup] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certifications: list[CertItem] = Field(default_factory=list)


class CoverLetterContent(BaseModel):
    greeting: str = "Dear Hiring Manager,"
    paragraphs: list[str] = Field(default_factory=list)
    closing: str = "Sincerely,"


class GeneratedContent(BaseModel):
    """The single JSON object the generator returns."""

    resume: ResumeContent
    cover_letter: CoverLetterContent