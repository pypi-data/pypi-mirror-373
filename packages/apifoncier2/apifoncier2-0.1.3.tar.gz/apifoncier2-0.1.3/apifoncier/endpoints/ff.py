from typing import Optional, List, Union
import pandas as pd
import geopandas as gpd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class FFEndpoint(BaseEndpoint):
    """
    Endpoints Fichiers fonciers (accès restreint) et indicateurs territoriaux (accès libre).

    Permet d'interroger les données des parcelles, locaux, TUPs et leurs géométries
    via l'API Fichiers Fonciers.
    """

    def __init__(self, client):
        """
        Initialise l'endpoint Fichiers Fonciers.

        Args:
            client: Instance du client principal.
        """
        super().__init__(client)

    # --- PARCELLES ---
    def parcelles(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        catpro3: Optional[str] = None,
        ctpdl: Optional[str] = None,
        dcntarti_min: Optional[int] = None,
        dcntarti_max: Optional[int] = None,
        dcntnaf_min: Optional[float] = None,
        dcntnaf_max: Optional[float] = None,
        dcntpa_min: Optional[int] = None,
        dcntpa_max: Optional[int] = None,
        idcomtxt: Optional[str] = None,
        idpar: Optional[List[str]] = None,
        jannatmin_min: Optional[int] = None,
        jannatmin_max: Optional[int] = None,
        nlocal_min: Optional[int] = None,
        nlocal_max: Optional[int] = None,
        nlogh_min: Optional[int] = None,
        nlogh_max: Optional[int] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        sprincp_min: Optional[int] = None,
        sprincp_max: Optional[int] = None,
        stoth_min: Optional[int] = None,
        stoth_max: Optional[int] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les parcelles issues des Fichiers Fonciers pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            catpro3 (str, optionnel): Catégorie propriétaire.
            ctpdl (str, optionnel): Type de pdl (copropriété).
            dcntarti_min (int, optionnel): Surface artificialisée minimale (m2).
            dcntarti_max (int, optionnel): Surface artificialisée maximale (m2).
            dcntnaf_min (float, optionnel): Surface NAF minimale (m2).
            dcntnaf_max (float, optionnel): Surface NAF maximale (m2).
            dcntpa_min (int, optionnel): Surface parcelle minimale (m2).
            dcntpa_max (int, optionnel): Surface parcelle maximale (m2).
            idcomtxt (str, optionnel): Libellé commune (recherche texte).
            idpar (List[str], optionnel): Identifiants de parcelle (max 10, séparés par virgule).
            jannatmin_min (int, optionnel): Année construction minimale.
            jannatmin_max (int, optionnel): Année construction maximale.
            nlocal_min (int, optionnel): Nombre de locaux minimal.
            nlocal_max (int, optionnel): Nombre de locaux maximal.
            nlogh_min (int, optionnel): Nombre de logements minimal.
            nlogh_max (int, optionnel): Nombre de logements maximal.
            slocal_min (int, optionnel): Surface parties d'évaluation minimale (m2).
            slocal_max (int, optionnel): Surface parties d'évaluation maximale (m2).
            sprincp_min (int, optionnel): Surface pièces principales pro minimale (m2).
            sprincp_max (int, optionnel): Surface pièces principales pro maximale (m2).
            stoth_min (int, optionnel): Surface pièces d'habitation minimale (m2).
            stoth_max (int, optionnel): Surface pièces d'habitation maximale (m2).
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            DataFrame ou liste de dictionnaires des parcelles.
        """
        # Validation des paramètres de localisation - emprise max 0.02° pour FF
        checked_codes_insee, bbox_result, auto_contains_geom = (
            self._validate_location_params(
                code_insee=code_insee,
                codes_insee=codes_insee,
                coddep=None,
                in_bbox=in_bbox,
                lon_lat=lon_lat,
                contains_lon_lat=contains_lon_lat,
                max_bbox_size=0.02,  # Contrainte FF: 0.02° max
                max_codes=10,
            )
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            in_bbox=",".join(map(str, bbox_result)) if bbox_result else None,
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            ctpdl=ctpdl,
            dcntarti_min=dcntarti_min,
            dcntarti_max=dcntarti_max,
            dcntnaf_min=dcntnaf_min,
            dcntnaf_max=dcntnaf_max,
            dcntpa_min=dcntpa_min,
            dcntpa_max=dcntpa_max,
            idcomtxt=idcomtxt,
            idpar=",".join(idpar) if idpar else None,
            jannatmin_min=jannatmin_min,
            jannatmin_max=jannatmin_max,
            nlocal_min=nlocal_min,
            nlocal_max=nlocal_max,
            nlogh_min=nlogh_min,
            nlogh_max=nlogh_max,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            sprincp_min=sprincp_min,
            sprincp_max=sprincp_max,
            stoth_min=stoth_min,
            stoth_max=stoth_max,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/parcelles",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def parcelle_by_id(
        self,
        idparcelle: str,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne la parcelle des Fichiers fonciers pour l'identifiant idparcelle demandé.

        Args:
            idparcelle (str, obligatoire): Identifiant de la parcelle.
            format_output (str, optionnel): 'dict'.

        Returns:
            Dictionnaire de la parcelle.
        """
        if not idparcelle:
            raise ValidationError("idparcelle est obligatoire")
        return self._fetch(
            endpoint=f"/ff/parcelles/{idparcelle}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )

    def geoparcelles(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        catpro3: Optional[str] = None,
        ctpdl: Optional[str] = None,
        dcntarti_min: Optional[int] = None,
        dcntarti_max: Optional[int] = None,
        dcntnaf_min: Optional[float] = None,
        dcntnaf_max: Optional[float] = None,
        dcntpa_min: Optional[int] = None,
        dcntpa_max: Optional[int] = None,
        idcomtxt: Optional[str] = None,
        idpar: Optional[List[str]] = None,
        jannatmin_min: Optional[int] = None,
        jannatmin_max: Optional[int] = None,
        nlocal_min: Optional[int] = None,
        nlocal_max: Optional[int] = None,
        nlogh_min: Optional[int] = None,
        nlogh_max: Optional[int] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        sprincp_min: Optional[int] = None,
        sprincp_max: Optional[int] = None,
        stoth_min: Optional[int] = None,
        stoth_max: Optional[int] = None,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les parcelles issues des Fichiers Fonciers pour la commune ou l'emprise rectangulaire demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            catpro3 (str, optionnel): Catégorie propriétaire.
            ctpdl (str, optionnel): Type de pdl (copropriété).
            dcntarti_min (int, optionnel): Surface artificialisée minimale (m2).
            dcntarti_max (int, optionnel): Surface artificialisée maximale (m2).
            dcntnaf_min (float, optionnel): Surface NAF minimale (m2).
            dcntnaf_max (float, optionnel): Surface NAF maximale (m2).
            dcntpa_min (int, optionnel): Surface parcelle minimale (m2).
            dcntpa_max (int, optionnel): Surface parcelle maximale (m2).
            idcomtxt (str, optionnel): Libellé commune (recherche texte).
            idpar (List[str], optionnel): Identifiants de parcelle (max 10, séparés par virgule).
            jannatmin_min (int, optionnel): Année construction minimale.
            jannatmin_max (int, optionnel): Année construction maximale.
            nlocal_min (int, optionnel): Nombre de locaux minimal.
            nlocal_max (int, optionnel): Nombre de locaux maximal.
            nlogh_min (int, optionnel): Nombre de logements minimal.
            nlogh_max (int, optionnel): Nombre de logements maximal.
            slocal_min (int, optionnel): Surface parties d'évaluation minimale (m2).
            slocal_max (int, optionnel): Surface parties d'évaluation maximale (m2).
            sprincp_min (int, optionnel): Surface pièces principales pro minimale (m2).
            sprincp_max (int, optionnel): Surface pièces principales pro maximale (m2).
            stoth_min (int, optionnel): Surface pièces d'habitation minimale (m2).
            stoth_max (int, optionnel): Surface pièces d'habitation maximale (m2).
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            GeoDataFrame des parcelles géolocalisées.
        """
        # Validation des paramètres de localisation - même contraintes que parcelles
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
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            ctpdl=ctpdl,
            dcntarti_min=dcntarti_min,
            dcntarti_max=dcntarti_max,
            dcntnaf_min=dcntnaf_min,
            dcntnaf_max=dcntnaf_max,
            dcntpa_min=dcntpa_min,
            dcntpa_max=dcntpa_max,
            idcomtxt=idcomtxt,
            idpar=",".join(idpar) if idpar else None,
            jannatmin_min=jannatmin_min,
            jannatmin_max=jannatmin_max,
            nlocal_min=nlocal_min,
            nlocal_max=nlocal_max,
            nlogh_min=nlogh_min,
            nlogh_max=nlogh_max,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            sprincp_min=sprincp_min,
            sprincp_max=sprincp_max,
            stoth_min=stoth_min,
            stoth_max=stoth_max,
            fields=fields,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/geoparcelles",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )

    # --- LOCAUX ---
    def locaux(
        self,
        code_insee: str,
        # Filtres spécifiques locaux
        catpro3: Optional[str] = None,
        dteloc: Optional[str] = None,
        idpar: Optional[str] = None,
        idprocpte: Optional[str] = None,
        idsec: Optional[str] = None,
        locprop: Optional[List[str]] = None,
        loghlls: Optional[str] = None,
        proba_rprs: Optional[str] = None,
        slocal_min: Optional[int] = None,
        slocal_max: Optional[int] = None,
        typeact: Optional[str] = None,
        fields: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les locaux issus des Fichiers Fonciers pour la commune demandée.

        Args:
            code_insee (str, obligatoire): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            catpro3 (str, optionnel): Catégorie propriétaire.
            dteloc (str, optionnel): Type(s) de local (séparés par virgule).
            idpar (str, optionnel): Identifiant de parcelle.
            idprocpte (str, optionnel): Identifiant de compte communal.
            idsec (str, optionnel): Identifiant de section cadastrale.
            locprop (List[str], optionnel): Localisation généralisée du propriétaire (séparés par virgule).
            loghlls (str, optionnel): Logement social repéré par exonération.
            proba_rprs (str, optionnel): Probabilité résidence principale/secondaire.
            slocal_min (int, optionnel): Surface parties d'évaluation minimale (m2).
            slocal_max (int, optionnel): Surface parties d'évaluation maximale (m2).
            typeact (str, optionnel): Type d'activité.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            DataFrame ou liste de dictionnaires des locaux.
        """
        # /ff/locaux : code_insee obligatoire (pas d'in_bbox)
        checked_codes_insee, _, _ = self._validate_location_params(
            code_insee=code_insee,
            codes_insee=None,
            coddep=None,
            in_bbox=None,
            lon_lat=None,
            contains_lon_lat=None,
            max_bbox_size=0.02,
            max_codes=10,
        )

        # Construction des paramètres
        params = self._build_params(
            code_insee=checked_codes_insee,
            catpro3=catpro3,
            dteloc=dteloc,
            idpar=idpar,
            idprocpte=idprocpte,
            idsec=idsec,
            locprop=",".join(locprop) if locprop else None,
            loghlls=loghlls,
            proba_rprs=proba_rprs,
            slocal_min=slocal_min,
            slocal_max=slocal_max,
            typeact=typeact,
            fields=fields,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/locaux",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def local_by_id(
        self,
        idlocal: str,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne le local des Fichiers fonciers pour l'identifiant fiscal du local demandé.

        Args:
            idlocal (str, obligatoire): Identifiant fiscal du local.
            format_output (str, optionnel): 'dict'.

        Returns:
            Dictionnaire du local.
        """
        if not idlocal:
            raise ValidationError("idlocal est obligatoire")

        # Pas de pagination pour un local unique
        return self._fetch(
            endpoint=f"/ff/locaux/{idlocal}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )

    def proprios(
        self,
        code_insee: str,
        catpro3: Optional[str] = None,
        ccodro: Optional[str] = None,
        fields: Optional[str] = None,
        gtoper: Optional[str] = None,
        idprocpte: Optional[str] = None,
        locprop: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        typedroit: Optional[str] = None,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les droits de propriété issus des Fichiers Fonciers pour la commune demandée.

        Args:
            code_insee (str, obligatoire): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            catpro3 (str, optionnel): Catégorie propriétaire.
            ccodro (str, optionnel): Code(s) du droit réel ou particulier (séparés par virgule).
            fields (str, optionnel): Champs à retourner.
            gtoper (str, optionnel): Indicateur personne physique/morale.
            idprocpte (str, optionnel): Identifiant de compte communal.
            locprop (str, optionnel): Localisation généralisée du propriétaire.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            typedroit (str, optionnel): Type de droit (propriétaire/gestionnaire).
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            DataFrame ou liste de dictionnaires des droits de propriété.
        """
        checked_codes_insee, _, _ = self._validate_location_params(
            code_insee=code_insee,
            codes_insee=None,
            coddep=None,
            in_bbox=None,
            lon_lat=None,
            contains_lon_lat=None,
            max_bbox_size=0.02,
            max_codes=10,
        )
        params = self._build_params(
            code_insee=checked_codes_insee,
            catpro3=catpro3,
            ccodro=ccodro,
            fields=fields,
            gtoper=gtoper,
            idprocpte=idprocpte,
            locprop=locprop,
            ordering=ordering,
            page=page,
            page_size=page_size,
            typedroit=typedroit,
        )
        return self._fetch(
            endpoint="/ff/proprios",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def proprio_by_id(
        self,
        idprodroit: str,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne le droit de propriété des Fichiers fonciers pour l'identifiant idprodroit demandé.

        Args:
            idprodroit (str, obligatoire): Identifiant du droit de propriété.
            format_output (str, optionnel): 'dict'.

        Returns:
            Dictionnaire du droit de propriété.
        """
        if not idprodroit:
            raise ValidationError("idprodroit est obligatoire")
        return self._fetch(
            endpoint=f"/ff/proprios/{idprodroit}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )

    def tups(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        catpro3: Optional[str] = None,
        fields: Optional[str] = None,
        idtup: Optional[List[str]] = None,
        typetup: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les TUPs issues des Fichiers Fonciers pour la commune ou l'emprise demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            catpro3 (str, optionnel): Catégorie propriétaire.
            fields (str, optionnel): Champs à retourner.
            idtup (List[str], optionnel): Identifiants de TUP (max 10, séparés par virgule).
            typetup (str, optionnel): Type de TUP (SIMPLE, PDLMP, UF).
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            DataFrame ou liste de dictionnaires des TUPs.
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
            catpro3=catpro3,
            fields=fields,
            idtup=",".join(idtup) if idtup else None,
            typetup=typetup,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )
        return self._fetch(
            endpoint="/ff/tups",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    def tup_by_id(
        self,
        idtup: str,
        format_output: str = "dict",
    ) -> Union[dict, List[dict]]:
        """
        Retourne la TUP des Fichiers fonciers pour l'identifiant idtup demandé.

        Args:
            idtup (str, obligatoire): Identifiant de la TUP.
            format_output (str, optionnel): 'dict'.

        Returns:
            Dictionnaire de la TUP.
        """
        if not idtup:
            raise ValidationError("idtup est obligatoire")
        return self._fetch(
            endpoint=f"/ff/tups/{idtup}",
            params={},
            format_output=format_output,
            geo=False,
            paginate=False,
        )

    def geotups(
        self,
        code_insee: Optional[str] = None,
        codes_insee: Optional[List[str]] = None,
        in_bbox: Optional[List[float]] = None,
        lon_lat: Optional[List[float]] = None,
        contains_lon_lat: Optional[List[float]] = None,
        catpro3: Optional[str] = None,
        fields: Optional[str] = None,
        idtup: Optional[List[str]] = None,
        typetup: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> gpd.GeoDataFrame:
        """
        Retourne, en GeoJSON, les TUPs issues des Fichiers Fonciers pour la commune ou l'emprise demandée.

        Args:
            code_insee (str, optionnel): Code INSEE communal ou d'arrondissement municipal (max 10, séparés par virgule).
            codes_insee (List[str], optionnel): Liste de codes INSEE.
            in_bbox (List[float], optionnel): [xmin, ymin, xmax, ymax], max 0.02° x 0.02°.
            lon_lat (List[float], optionnel): Coordonnées [lon, lat].
            contains_lon_lat (List[float], optionnel): Coordonnées à contenir [lon, lat].
            catpro3 (str, optionnel): Catégorie propriétaire.
            fields (str, optionnel): Champs à retourner.
            idtup (List[str], optionnel): Identifiants de TUP (max 10, séparés par virgule).
            typetup (str, optionnel): Type de TUP (SIMPLE, PDLMP, UF).
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.

        Returns:
            GeoDataFrame des TUPs géolocalisées.
        """
        # Validation des paramètres de localisation
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
            contains_geom=auto_contains_geom,
            catpro3=catpro3,
            fields=fields,
            idtup=",".join(idtup) if idtup else None,
            typetup=typetup,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/ff/geotups",
            params=params,
            format_output=format_output,
            geo=True,
            paginate=paginate,
        )
