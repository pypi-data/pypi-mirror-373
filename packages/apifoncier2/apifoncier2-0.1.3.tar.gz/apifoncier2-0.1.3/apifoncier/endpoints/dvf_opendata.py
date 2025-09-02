from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from .base import BaseEndpoint


class DVFOpenDataEndpoint(BaseEndpoint):
    """
    Endpoints DVF Open Data : mutations et geomutations.

    Permet d'interroger les mutations foncières DVF+ et leurs géométries via l'API Open Data.
    """

    def __init__(self, client):
        """
        Initialise l'endpoint DVF Open Data.

        Args:
            client: Instance du client principal.
        """
        super().__init__(client)

    def mutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les mutations issues de DVF+ pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE de la commune.
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [min_lon, min_lat, max_lon, max_lat].
            lon_lat (List[float], optionnel): [longitude, latitude].
            contains_lon_lat (List[float], optionnel): [longitude, latitude] pour filtrer par point contenu dans l'emprise.
            anneemut (str, optionnel): Année de la mutation au format YYYY.
            anneemut_min (str, optionnel): Année de mutation minimale au format YYYY.
            anneemut_max (str, optionnel): Année de mutation maximale au format YYYY.
            codtypbien (str, optionnel): Code du type de bien.
            idnatmut (str, optionnel): Identifiant national de la mutation.
            vefa (str, optionnel): Statut VEFA (Vente en l'État Futur d'Achèvement).
            sbati_min (float, optionnel): Superficie bâtie minimale.
            sbati_max (float, optionnel): Superficie bâtie maximale.
            sterr_min (float, optionnel): Superficie terrain minimale.
            sterr_max (float, optionnel): Superficie terrain maximale.
            valeurfonc_min (float, optionnel): Valeur foncière minimale.
            valeurfonc_max (float, optionnel): Valeur foncière maximale.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            ordering (str, optionnel): Critère de tri des résultats.
            page (int, optionnel): Numéro de la page pour la pagination.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Activer la pagination ou non.
            format_output (str, optionnel): Format de sortie ('dataframe' ou 'dict').

        Returns:
            DataFrame ou liste de dictionnaires des mutations.
        """

        # Validation des paramètres de localisation avec mutualisation
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            contains_geom=auto_contains_geom,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/dvf_opendata/mutations",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def geomutations(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        anneemut: Optional[str] = None,
        anneemut_min: Optional[str] = None,
        anneemut_max: Optional[str] = None,
        codtypbien: Optional[str] = None,
        idnatmut: Optional[str] = None,
        vefa: Optional[str] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[gpd.GeoDataFrame, List[dict]]:
        """
        Retourne, en GeoJSON, les mutations issues de DVF+ pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE de la commune.
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [min_lon, min_lat, max_lon, max_lat].
            lon_lat (List[float], optionnel): [longitude, latitude].
            contains_lon_lat (List[float], optionnel): [longitude, latitude] pour filtrer par point contenu dans l'emprise.
            anneemut (str, optionnel): Année de la mutation au format YYYY.
            anneemut_min (str, optionnel): Année de mutation minimale au format YYYY.
            anneemut_max (str, optionnel): Année de mutation maximale au format YYYY.
            codtypbien (str, optionnel): Code du type de bien.
            idnatmut (str, optionnel): Identifiant national de la mutation.
            vefa (str, optionnel): Statut VEFA (Vente en l'État Futur d'Achèvement).
            sbati_min (float, optionnel): Superficie bâtie minimale.
            sbati_max (float, optionnel): Superficie bâtie maximale.
            sterr_min (float, optionnel): Superficie terrain minimale.
            sterr_max (float, optionnel): Superficie terrain maximale.
            valeurfonc_min (float, optionnel): Valeur foncière minimale.
            valeurfonc_max (float, optionnel): Valeur foncière maximale.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            ordering (str, optionnel): Critère de tri des résultats.
            page (int, optionnel): Numéro de la page pour la pagination.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Activer la pagination ou non.
            format_output (str, optionnel): Format de sortie ('dataframe' ou 'dict').

        Returns:
            GeoDataFrame ou liste de dictionnaires des mutations géolocalisées.
        """

        # Validation des paramètres de localisation avec mutualisation
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            contains_geom=auto_contains_geom,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/dvf_opendata/geomutations",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )
