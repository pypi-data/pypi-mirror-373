from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class DV3FEndpoint(BaseEndpoint):
    """
    Endpoints DV3F (accès restreint): mutations, geomutations et mutation par id.

    Permet d'interroger les mutations foncières et leurs géométries via l'API DV3F.
    """

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
        codtypproa: Optional[str] = None,
        codtypprov: Optional[str] = None,
        filtre: Optional[str] = None,
        segmtab: Optional[str] = None,
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
        Retourne les mutations issues de DV3F pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            anneemut (str, optionnel): Année de mutation (>=2010).
            anneemut_min (str, optionnel): Année minimale.
            anneemut_max (str, optionnel): Année maximale.
            codtypbien (str, optionnel): Typologie de bien (séparés par virgule).
            idnatmut (str, optionnel): Nature de mutation (séparés par virgule).
            vefa (str, optionnel): Vente en l'état futur d'achèvement.
            codtypproa (str, optionnel): Typologie acheteur (séparés par virgule).
            codtypprov (str, optionnel): Typologie vendeur (séparés par virgule).
            filtre (str, optionnel): Code pour exclure des transactions particulières.
            segmtab (str, optionnel): Note de segment terrain à bâtir.
            sbati_min (float, optionnel): Surface bâtie minimale.
            sbati_max (float, optionnel): Surface bâtie maximale.
            sterr_min (float, optionnel): Surface terrain minimale.
            sterr_max (float, optionnel): Surface terrain maximale.
            valeurfonc_min (float, optionnel): Valeur foncière minimale (€).
            valeurfonc_max (float, optionnel): Valeur foncière maximale (€).
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            DataFrame ou liste de dictionnaires des mutations.
        """
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
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            codtypproa=codtypproa,
            codtypprov=codtypprov,
            filtre=filtre,
            segmtab=segmtab,
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
            endpoint="/dv3f/mutations",
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
        codtypproa: Optional[str] = None,
        codtypprov: Optional[str] = None,
        filtre: Optional[str] = None,
        segmtab: Optional[str] = None,
        sbati_min: Optional[float] = None,
        sbati_max: Optional[float] = None,
        sterr_min: Optional[float] = None,
        sterr_max: Optional[float] = None,
        valeurfonc_min: Optional[float] = None,
        valeurfonc_max: Optional[float] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les mutations issues de DV3F pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            anneemut (str, optionnel): Année de mutation (>=2010).
            anneemut_min (str, optionnel): Année minimale.
            anneemut_max (str, optionnel): Année maximale.
            codtypbien (str, optionnel): Typologie de bien (séparés par virgule).
            idnatmut (str, optionnel): Nature de mutation (séparés par virgule).
            vefa (str, optionnel): Vente en l'état futur d'achèvement.
            codtypproa (str, optionnel): Typologie acheteur (séparés par virgule).
            codtypprov (str, optionnel): Typologie vendeur (séparés par virgule).
            filtre (str, optionnel): Code pour exclure des transactions particulières.
            segmtab (str, optionnel): Note de segment terrain à bâtir.
            sbati_min (float, optionnel): Surface bâtie minimale.
            sbati_max (float, optionnel): Surface bâtie maximale.
            sterr_min (float, optionnel): Surface terrain minimale.
            sterr_max (float, optionnel): Surface terrain maximale.
            valeurfonc_min (float, optionnel): Valeur foncière minimale (€).
            valeurfonc_max (float, optionnel): Valeur foncière maximale (€).
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            GeoDataFrame des mutations géolocalisées.
        """
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
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            anneemut=anneemut,
            anneemut_min=anneemut_min,
            anneemut_max=anneemut_max,
            codtypbien=codtypbien,
            idnatmut=idnatmut,
            vefa=vefa,
            codtypproa=codtypproa,
            codtypprov=codtypprov,
            filtre=filtre,
            segmtab=segmtab,
            sbati_min=sbati_min,
            sbati_max=sbati_max,
            sterr_min=sterr_min,
            sterr_max=sterr_max,
            valeurfonc_min=valeurfonc_min,
            valeurfonc_max=valeurfonc_max,
            fields=fields,
            page=page,
            page_size=page_size,
        )
        return self._fetch(
            endpoint="/dv3f/geomutations",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )

    def mutation_by_id(
        self,
        idmutation: int,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne la mutation DV3F pour l'identifiant fiscal demandé.

        Args:
            idmutation (int, obligatoire): Identifiant fiscal de la mutation.
            format_output (str, optionnel): 'dict'.

        Returns:
            Dictionnaire de la mutation.
        """
        if idmutation is None:
            raise ValidationError("idmutation est obligatoire")
        return self._fetch(
            endpoint=f"/dv3f/mutations/{idmutation}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )
