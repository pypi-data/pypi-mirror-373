"""Client principal pour l'API Données foncières du Cerema."""

import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .config import Config
from .exceptions import ApiFoncierError, AuthenticationError

from .endpoints import (
    DVFOpenDataEndpoint,
    CartofrichesEndpoint,
    DV3FEndpoint,
    FFEndpoint,
    IndicateurEndpoint,
)


class ApiFoncierClient:
    """Client principal pour interagir avec l'API Données foncières du Cerema."""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialise le client API.

        Args:
            config: Dictionnaire de configuration pour le client API.
        """

        self.config = Config(**config) if config else Config()

        self.session = self._create_session()
        self.logger = logging.getLogger(__name__)

        # Endpoints
        self.dvf_opendata = DVFOpenDataEndpoint(self)
        self.dv3f = DV3FEndpoint(self)
        self.ff = FFEndpoint(self)
        self.cartofriches = CartofrichesEndpoint(self)
        self.indicateurs = IndicateurEndpoint(self)

    def _create_session(self) -> requests.Session:
        """Crée une session HTTP configurée."""
        session = requests.Session()

        # Configuration des headers
        session.headers.update(
            {
                "User-Agent": f"apifoncier-python/{self.config.version}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        if self.config.api_key:
            session.headers["Authorization"] = f"Token {self.config.api_key}"

        # Configuration des retries
        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API.

        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint de l'API
            params: Paramètres de requête
            data: Données à envoyer

        Returns:
            Réponse de l'API sous forme de dictionnaire

        Raises:
            APIError: Erreur générale de l'API
            AuthenticationError: Erreur d'authentification
        """
        url = f"{self.config.base_url.rstrip('/')}{endpoint}"

        # Vérifier le cache pour les requêtes GET
        try:
            self.logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout,
            )

            self._handle_response(response)
            result = response.json()

            return result

        except requests.exceptions.Timeout:
            raise ApiFoncierError("Timeout lors de la requête")
        except requests.exceptions.ConnectionError:
            raise ApiFoncierError("Erreur de connexion à l'API")
        except requests.exceptions.RequestException as e:
            raise ApiFoncierError(f"Erreur de requête: {str(e)}")

    def _handle_response(self, response: requests.Response) -> None:
        """Gère les erreurs de réponse HTTP."""
        if response.status_code == 401:
            raise AuthenticationError("Authentification requise ou invalide")
        elif response.status_code == 429:
            raise ApiFoncierError("Limite de taux dépassée")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("detail", "Erreur inconnue")
            except:
                message = f"Erreur HTTP {response.status_code}"
            raise ApiFoncierError(message)

    def close(self) -> None:
        """Ferme la session HTTP."""
        if self.session:
            self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
