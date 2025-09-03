from pydantic import BaseModel, Field
from typing import Optional

class AIConfig(BaseModel):
    openai_api_key: Optional[str] = None

class GitHubConfig(BaseModel):
    token: Optional[str] = None

class GitLabConfig(BaseModel):
    token: Optional[str] = None

class Config(BaseModel):
    ai: AIConfig = Field(default_factory=AIConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    gitlab: GitLabConfig = Field(default_factory=GitLabConfig)
