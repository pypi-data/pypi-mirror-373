from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelConfig(BaseModel):
    app_name: str
    deployment: str
    model: str


class AppConfig(BaseModel):
    model: ModelConfig


class File(BaseModel):
    name: str
    type: Literal["file"]


class Folder(BaseModel):
    name: str
    type: Literal["folder"]
    items: List[Union[File, 'Folder']] = Field(default_factory=list)


class FolderClassificationRequest(BaseModel):
    items: List[str]


class FolderClassificationResponse(BaseModel):
    category: Literal["matter", "other"]
    reasoning: Optional[str] = None


class FolderClassification(BaseModel):
    category: Literal["matter", "other"]
    reasoning: str
    model_config = ConfigDict(extra="forbid")