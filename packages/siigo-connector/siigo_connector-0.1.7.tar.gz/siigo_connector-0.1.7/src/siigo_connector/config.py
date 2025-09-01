from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    base_url: str = "https://api.siigo.com"
    timeout: float = 30.0
    user_agent: str = (
        "siigo_connector/0.1.0 (+https://github.com/arendondiosa/siigo-connector-py)"
    )
    username: str | None = None
    access_key: str | None = None
    partner_id: str | None = None
