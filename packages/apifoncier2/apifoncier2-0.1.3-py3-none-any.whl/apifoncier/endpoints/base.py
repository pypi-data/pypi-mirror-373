from typing import Dict, Any, List, Union, Type, Optional, Sequence
from urllib.parse import urlparse

from tqdm import tqdm
import geopandas as gpd
import pandas as pd

from ..validators import (
    validate_code_insee,
    validate_coddep,
    validate_bbox,
    validate_contains_lon_lat,
    validate_lon_lat_point,
)
from ..exceptions import ValidationError


class BaseEndpoint:
    """
    Classe de base pour les endpoints de l'API.

    Cette classe fournit des méthodes communes pour les endpoints, comme la gestion des paramètres et des requêtes.
    """

    def __init__(self, client):
        """
        Initialise l'endpoint avec le client API.

        Args:
            client: Instance du client API.
        """
        self.client = client
        self.progress_bar = client.config.progress_bar

    def set_progress_bar(self, enabled: bool = True) -> None:
        """Active ou désactive l’affichage de la barre de progression."""
        self.progress_bar = enabled

    def _request(
        self, endpoint: str, params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Proxy vers ApiFoncierClient.request (GET JSON)."""
        return self.client.request("GET", endpoint, params=params)

    @staticmethod
    def _strip_base_url(full_url: str, base_url: str) -> str:
        """
        Convertit une URL absolue en chemin relatif à l'API.
        Gère les différences de protocole (http/https).
        """
        base_parsed = urlparse(base_url.rstrip("/"))
        full_parsed = urlparse(full_url)

        # Comparaison en ignorant le protocole
        if base_parsed.netloc == full_parsed.netloc and full_parsed.path.startswith(
            base_parsed.path
        ):
            relative_path = full_parsed.path[len(base_parsed.path) :]
            if full_parsed.query:
                relative_path += f"?{full_parsed.query}"
            return relative_path

        return full_url

    def _extract(
        self, response: Dict[str, Any]
    ) -> tuple[Sequence[Dict[str, Any]], Optional[str], int]:
        """
        Extrait les données, l’URL suivante et le total à partir d’une réponse JSON.
        Gestion des formats « results » et « features ».
        """
        if "results" in response:  # réponse tabulaire
            return (
                response["results"],
                response.get("next"),
                response.get("count", len(response["results"])),
            )
        if "features" in response:  # réponse GeoJSON
            return (
                response["features"],
                response.get("next"),
                response.get("count", len(response["features"])),
            )
        # fallback : objet ou liste brute
        data = response if isinstance(response, list) else [response]
        return data, None, len(data)

    def _collect_pages(
        self,
        endpoint: str,
        params: Dict[str, Any],
        *,
        geo: bool = False,
        paginate: bool = False,
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Récupère une ou plusieurs pages puis concatène dans un (Geo)DataFrame.
        """

        pages: list[Union[pd.DataFrame, gpd.GeoDataFrame]] = []
        total_seen = 0
        current_endpoint = endpoint
        current_params = params
        pbar: Optional[tqdm] = None

        while True:
            resp = self._request(current_endpoint, current_params)
            data, next_url, total = self._extract(resp)

            # première initialisation pbar (après avoir obtenu 'total')
            if self.progress_bar and paginate and data and not pbar:
                pbar = tqdm(total=total, unit="enreg.", desc=endpoint)

            # conversion page -> DataFrame
            if geo:
                df_page = gpd.GeoDataFrame.from_features(
                    {"type": "FeatureCollection", "features": data}
                )

                # Ajout des identifiants en index si disponibles
                if "features" in resp and resp["features"]:
                    try:
                        ids = pd.json_normalize(resp["features"])
                        if "id" in ids.columns:
                            df_page = df_page.set_index(ids["id"].values)
                    except (KeyError, ValueError):
                        # En cas d'erreur, on garde l'index par défaut
                        pass
            else:
                df_page = pd.DataFrame(data)

            pages.append(df_page)

            # mise à jour barre de progression
            total_seen += len(df_page)
            if pbar:
                pbar.update(len(df_page))

            # sortie si pas de pagination demandée ou pas de page suivante
            if not paginate or not next_url:
                break

            current_endpoint = self._strip_base_url(
                next_url, self.client.config.base_url
            )
            current_params = None  # pages suivantes transmises via URL 'next'

        if pbar:
            pbar.close()

        if not pages:
            return gpd.GeoDataFrame() if geo else pd.DataFrame()

        # Concaténation en préservant les index personnalisés pour les GeoDataFrame
        if geo:
            return gpd.GeoDataFrame(pd.concat(pages, ignore_index=False))
        else:
            return pd.concat(pages, ignore_index=True)

    # ------------------ FORMATAGE SELON LE TYPE DEMANDÉ -----------------

    def _to_output(
        self,
        df: Union[pd.DataFrame, gpd.GeoDataFrame],
        *,
        format_output: str,
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame, List[Dict[str, Any]]]:
        """
        Convertit un DataFrame/GeoDataFrame en 4 formats possibles :
        - dataframe (par défaut)   ➜ pd.DataFrame / gpd.GeoDataFrame
        - dict                     ➜ dict ou geojson dict
        """
        if format_output == "dataframe":
            return df

        if format_output == "dict":
            if isinstance(df, gpd.GeoDataFrame):
                records = df.to_geo_dict()
            else:
                records = df.to_dict("records")
            return records

        raise ValueError(f"Format de sortie non supporté : {format_output}")

    # --------------------- MÉTHODE HAUT NIVEAU À UTILISER ----------------

    def _fetch(
        self,
        *,
        endpoint: str,
        params: Dict[str, Any],
        format_output: str = "dataframe",
        geo: bool = False,
        paginate: bool = False,
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame, List[Dict[str, Any]]]:
        """
        Point d’entrée unique pour tous les endpoints concrets.
        1. télécharge une ou plusieurs pages ;
        2. concatène dans un (Geo)DataFrame ;
        3. convertit dans le format demandé.
        """
        df = self._collect_pages(
            endpoint,
            params,
            geo=geo,
            paginate=paginate,
        )
        return self._to_output(df, format_output=format_output)

    @staticmethod
    def _build_params(**kwargs: Any) -> Dict[str, Any]:
        """Filtre les valeurs None des paramètres."""
        return {k: v for k, v in kwargs.items() if v is not None}

    def _validate_location_params(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        coddep: Optional[str] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        max_bbox_size: float = 1.0,
        max_interval: float = 0.01,
        max_codes: int = 10,
    ) -> tuple[Optional[str], Optional[List[float]], Optional[str]]:
        """
        Valide et normalise les paramètres de localisation (mutuel entre endpoints).
        """
        # Vérification qu'au moins un paramètre de localisation est fourni
        location_params = [
            code_insee,
            codes_insee,
            coddep,
            in_bbox,
            lon_lat,
            contains_lon_lat,
        ]
        if not any(param is not None for param in location_params):
            raise ValidationError(
                "Au moins un paramètre de localisation est requis: "
                "code_insee, codes_insee, coddep, in_bbox, lon_lat ou contains_lon_lat"
            )

        # Validation codes_insee
        checked_codes_insee = None
        if codes_insee:
            if len(codes_insee) > max_codes:
                raise ValidationError(f"Maximum {max_codes} codes INSEE autorisés")
            for code in codes_insee:
                validate_code_insee(code)
            checked_codes_insee = ",".join(codes_insee)
        elif code_insee:
            validate_code_insee(code_insee)
            checked_codes_insee = code_insee

        if coddep:
            validate_coddep(coddep)

        # Gestion des paramètres géographiques
        bbox_result = None
        contains_geom = None

        if contains_lon_lat:
            bbox_result, contains_geom = validate_contains_lon_lat(contains_lon_lat)

        elif in_bbox:
            validate_bbox(in_bbox, max_bbox_size)
            bbox_result = in_bbox

        elif lon_lat:
            bbox_result = validate_lon_lat_point(lon_lat, max_interval)

        return checked_codes_insee, bbox_result, contains_geom
