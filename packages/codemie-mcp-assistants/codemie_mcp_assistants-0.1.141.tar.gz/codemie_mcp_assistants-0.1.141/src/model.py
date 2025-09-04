import os
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AssistantInfo(BaseModel):
    """Model representing assistant information from the MCP API"""

    id: str = Field(..., description="Unique identifier of the assistant")
    name: str = Field(..., description="Name of the assistant")
    slug: Optional[str] = Field(None, description="Slug of the assistant")
    description: str = Field(..., description="Description of the assistant")
    project: Optional[str] = Field(None, description="Associated project name")


class AssistantNotFoundError(Exception):
    """Exception raised when an assistant is not found"""

    def __init__(self, assistant_id: str):
        self.assistant_id = assistant_id
        self.message = f"Assistant with ID {assistant_id} not found"
        super().__init__(self.message)


class AuthConfig(BaseModel):
    """Authentication configuration with support for multiple auth methods."""

    username: Optional[str] = Field(
        default=None, description="Username for password-based authentication"
    )
    password: Optional[str] = Field(
        default=None, description="Password for password-based authentication"
    )
    client_id: str = Field(
        default="codemie-sdk",
        description="Client ID for client credentials authentication",
    )
    client_secret: Optional[str] = Field(
        default=None, description="Client secret for client credentials authentication"
    )

    @model_validator(mode="after")
    def validate_auth_method(self) -> "AuthConfig":
        has_user_pass = bool(self.username and self.password)
        has_client_creds = bool(self.client_id and self.client_secret)

        if not (has_user_pass or has_client_creds):
            raise ValueError(
                "Authentication configuration missing. Please provide either:\n"
                "- CODEMIE_USERNAME and CODEMIE_PASSWORD for password authentication\n"
                "- CODEMIE_AUTH_CLIENT_ID and CODEMIE_AUTH_CLIENT_SECRET for client credentials\n"
            )

        if has_user_pass and has_client_creds:
            import warnings

            warnings.warn(
                "Both authentication methods provided. Using client credentials authentication.",
                UserWarning,
            )

        return self


class Settings:
    """Application settings configured via environment variables."""

    # Default values
    DEFAULT_AUTH_CLIENT_ID = "codemie-sdk"
    DEFAULT_AUTH_REALM_NAME = "codemie-prod"
    DEFAULT_AUTH_SERVER_URL = (
        "https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth"
    )
    DEFAULT_CODEMIE_API_DOMAIN = "https://codemie.lab.epam.com/code-assistant-api"

    def __init__(self):
        # Authentication settings
        self.auth = AuthConfig(
            username=os.environ.get("CODEMIE_USERNAME"),
            password=os.environ.get("CODEMIE_PASSWORD"),
            client_id=os.environ.get(
                "CODEMIE_AUTH_CLIENT_ID", self.DEFAULT_AUTH_CLIENT_ID
            ),
            client_secret=os.environ.get("CODEMIE_AUTH_CLIENT_SECRET"),
        )

        # Server configuration
        self.auth_client_id = os.environ.get(
            "CODEMIE_AUTH_CLIENT_ID", self.DEFAULT_AUTH_CLIENT_ID
        )
        self.auth_realm_name = os.environ.get(
            "CODEMIE_AUTH_REALM_NAME", self.DEFAULT_AUTH_REALM_NAME
        )
        self.auth_server_url = os.environ.get(
            "CODEMIE_AUTH_SERVER_URL", self.DEFAULT_AUTH_SERVER_URL
        )
        self.api_domain = os.environ.get(
            "CODEMIE_API_DOMAIN", self.DEFAULT_CODEMIE_API_DOMAIN
        )
        self.assistant_id = os.environ.get("CODEMIE_ASSISTANT_ID")
        self.verify_ssl = os.environ.get("CODEMIE_VERIFY_SSL", "true").lower() == "true"

    def __str__(self):
        """String representation of the settings (excluding sensitive data)."""
        return (
            f"Settings:\n"
            f"  Auth Client ID: {self.auth_client_id}\n"
            f"  Auth Realm Name: {self.auth_realm_name}\n"
            f"  Auth Server URL: {self.auth_server_url}\n"
            f"  API Domain: {self.api_domain}\n"
            f"  Assistant ID: {self.assistant_id}\n"
            f"  Verify SSL: {self.verify_ssl}\n"
        )
