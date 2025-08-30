"""
Authentication client for Simile API using bearer token authentication.

This client handles authentication-related operations using Google OAuth tokens
rather than API keys.
"""

import httpx
from httpx import AsyncClient
from typing import List, Optional, Union
import uuid
from datetime import datetime

from .models import BaseModel
from .exceptions import (
    SimileAPIError,
    SimileAuthenticationError,
    SimileNotFoundError,
    SimileBadRequestError,
)


# Import the models from auth_api_endpoints
# In production, these would be in a shared models file
class UserInfo(BaseModel):
    """User information from Google authentication"""

    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime
    last_login: datetime


class APIKey(BaseModel):
    """API Key model"""

    key_id: uuid.UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


class APIKeyCreateResponse(BaseModel):
    """Response when creating a new API key"""

    key_id: uuid.UUID
    name: str
    key: str
    key_prefix: str
    created_at: datetime
    expires_at: Optional[datetime] = None


class PopulationAccess(BaseModel):
    """Population access information"""

    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    role: str
    created_at: datetime
    member_count: int
    agent_count: int


class PopulationShareResponse(BaseModel):
    """Response when creating a share code"""

    share_code: str
    population_id: uuid.UUID
    role: str
    expires_at: datetime
    max_uses: Optional[int] = None
    created_at: datetime


class PopulationJoinResponse(BaseModel):
    """Response when joining a population"""

    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    role: str
    message: str = "Successfully joined population"


DEFAULT_BASE_URL = "https://api.simile.ai/api/v1"
TIMEOUT_CONFIG = httpx.Timeout(5.0, read=30.0, write=30.0, pool=30.0)


class SimileAuth:
    """
    Authentication client for Simile API.

    This client uses bearer token authentication from Google OAuth
    instead of API keys.
    """

    def __init__(self, bearer_token: str, base_url: str = DEFAULT_BASE_URL):
        """
        Initialize the authentication client.

        Args:
            bearer_token: The Google OAuth bearer token
            base_url: The base URL of the API
        """
        if not bearer_token:
            raise ValueError("Bearer token is required.")
        self.bearer_token = bearer_token
        self.base_url = base_url.rstrip("/")
        self._client = AsyncClient(
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            timeout=TIMEOUT_CONFIG,
        )

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Union[httpx.Response, BaseModel]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response_model_cls = kwargs.pop("response_model", None)

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()

            if response_model_cls:
                return response_model_cls(**response.json())
            else:
                return response
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", e.response.text)
            except Exception:
                detail = e.response.text

            if status_code == 401:
                raise SimileAuthenticationError(detail=detail)
            elif status_code == 404:
                raise SimileNotFoundError(detail=detail)
            elif status_code == 400:
                raise SimileBadRequestError(detail=detail)
            else:
                raise SimileAPIError(
                    f"API request failed: {e}", status_code=status_code, detail=detail
                )
        except httpx.RequestError as e:
            raise SimileAPIError(f"Request error: {type(e).__name__}: {e}")

    async def get_current_user(self) -> UserInfo:
        """Get current user information."""
        response = await self._request("GET", "auth/me", response_model=UserInfo)
        return response

    async def list_api_keys(self) -> List[APIKey]:
        """List all API keys for the current user."""
        response = await self._request("GET", "auth/api-keys")
        return [APIKey(**key_data) for key_data in response.json()]

    async def create_api_key(
        self, name: str, expires_in_days: Optional[int] = None
    ) -> APIKeyCreateResponse:
        """
        Create a new API key.

        Args:
            name: Name for the API key
            expires_in_days: Optional expiration time in days

        Returns:
            APIKeyCreateResponse with the full key (only shown once)
        """
        payload = {"name": name}
        if expires_in_days is not None:
            payload["expires_in_days"] = expires_in_days

        response = await self._request(
            "POST", "auth/api-keys", json=payload, response_model=APIKeyCreateResponse
        )
        return response

    async def delete_api_key(self, key_id: Union[str, uuid.UUID]) -> dict:
        """
        Delete an API key.

        Args:
            key_id: The ID of the API key to delete

        Returns:
            Success message
        """
        response = await self._request("DELETE", f"auth/api-keys/{str(key_id)}")
        return response.json()

    async def list_accessible_populations(self) -> List[PopulationAccess]:
        """List all populations the current user has access to."""
        response = await self._request("GET", "auth/populations")
        return [PopulationAccess(**pop_data) for pop_data in response.json()]

    async def create_population_share_code(
        self,
        population_id: Union[str, uuid.UUID],
        role: str = "viewer",
        expires_in_hours: Optional[int] = 24,
        max_uses: Optional[int] = None,
    ) -> PopulationShareResponse:
        """
        Create a share code for a population.

        Args:
            population_id: The ID of the population to share
            role: The role to grant (viewer or editor)
            expires_in_hours: Hours until the code expires (default 24)
            max_uses: Maximum number of times the code can be used

        Returns:
            PopulationShareResponse with the share code
        """
        payload = {
            "population_id": str(population_id),
            "role": role,
            "expires_in_hours": expires_in_hours,
        }
        if max_uses is not None:
            payload["max_uses"] = max_uses

        response = await self._request(
            "POST",
            "auth/populations/share",
            json=payload,
            response_model=PopulationShareResponse,
        )
        return response

    async def join_population_with_share_code(
        self, share_code: str
    ) -> PopulationJoinResponse:
        """
        Join a population using a share code.

        Args:
            share_code: The share code to use

        Returns:
            PopulationJoinResponse with population details
        """
        response = await self._request(
            "POST",
            "auth/populations/join",
            json={"share_code": share_code},
            response_model=PopulationJoinResponse,
        )
        return response

    async def aclose(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
