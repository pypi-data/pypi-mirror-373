from typing import Optional
from sqlmodel import SQLModel, Field

class Ned(SQLModel, table=True):
    name: str = Field(default="cisco_ios_ssh", primary_key=True)
    version: str = Field(default="0.0.1")

class AssetBase(SQLModel):
    vendor: str = Field(default="cisco")
    serial_number: str = Field(default="abc123")
    os: str = Field(default="ios")
    os_version: str = Field(default="12.0.1")
    ned_id: Optional[str] = None

class Asset(AssetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)