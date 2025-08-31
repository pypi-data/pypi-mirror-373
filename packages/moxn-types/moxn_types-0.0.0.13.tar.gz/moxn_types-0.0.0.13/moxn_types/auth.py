"""Simplified tenant-based authentication models."""

from pydantic import BaseModel, SecretStr


class TenantAuth(BaseModel):
    """
    Tenant-scoped authentication via API key.
    
    Modern, simplified authentication that only requires an API key.
    The API key already contains the tenant context, eliminating the need
    for separate user_id, org_id, or tenant_id fields.
    
    Example:
        ```python
        auth = TenantAuth(api_key="moxn_3Oxskm27Fn...")
        headers = auth.to_headers()
        # {"x-api-key": "moxn_3Oxskm27Fn...", "Content-Type": "application/json"}
        ```
    """
    api_key: SecretStr
    
    def to_headers(self) -> dict[str, str]:
        """Convert to HTTP headers for API requests."""
        return {
            "x-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }
    
    def __repr__(self) -> str:
        """Safe representation that doesn't expose the API key."""
        return f"TenantAuth(api_key=SecretStr('**********'))"