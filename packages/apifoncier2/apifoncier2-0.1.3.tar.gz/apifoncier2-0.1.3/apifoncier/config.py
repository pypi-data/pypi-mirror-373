import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration du client API."""

    api_key: Optional[str] = None
    base_url: str = "https://apidf-preprod.cerema.fr/"
    timeout: int = 60
    max_retries: int = 3
    progress_bar: bool = True
    version: str = "1.0.0"

    def __post_init__(self):
        """Post-initialisation pour récupérer les variables d'environnement."""
        if not self.api_key:
            self.api_key = os.getenv("APIFONCIER_API_KEY")

        env_base_url = os.getenv("APIFONCIER_BASE_URL")
        if env_base_url:
            self.base_url = env_base_url
