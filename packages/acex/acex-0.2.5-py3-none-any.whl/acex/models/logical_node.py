from sqlmodel import SQLModel, Field
from typing import Optional, Dict

class LogicalNodeBase(SQLModel):
    hostname: str = Field(default="R1")
    role: str = Field(default="core")
    site: Optional[str] = Field(default="HQ")

class LogicalNode(LogicalNodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class LogicalNodeCreate(LogicalNodeBase):
    pass

class LogicalNodeResponse(LogicalNodeBase):
    configuration: Dict = Field(default_factory=dict)
    meta_data: Dict = Field(default_factory=dict)
    interfaces: Dict = Field(default_factory=dict)

class LogicalNodeListResponse(LogicalNodeBase):
    id: int