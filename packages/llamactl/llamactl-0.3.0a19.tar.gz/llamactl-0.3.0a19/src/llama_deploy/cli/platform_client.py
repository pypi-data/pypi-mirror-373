from __future__ import annotations

from datetime import datetime

import httpx
from pydantic import BaseModel, TypeAdapter


class PlatformClient:
    def __init__(self, auth_token: str, platform_url: str):
        self.auth_token = auth_token
        self.platform_url = platform_url
        self.client = httpx.AsyncClient(base_url=platform_url)

    async def list_projects(self) -> list[Project]:
        response = await self.client.get("/api/v1/projects")
        response.raise_for_status()
        return ProjectList.validate_python(response.json())

    async def list_organizations(self) -> list[Organization]:
        response = await self.client.get("/api/v1/organizations")
        response.raise_for_status()
        return OrganizationList.validate_python(response.json())

    async def validate_auth_token(self) -> bool:
        response = await self.client.get("/api/v1/organizations/default")
        try:
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError:
            if response.status_code == 401:
                return False
            raise


class Organization(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime


class Project(BaseModel):
    id: str
    name: str
    organization_id: str
    created_at: datetime
    updated_at: datetime


OrganizationList = TypeAdapter(list[Organization])
ProjectList = TypeAdapter(list[Project])
