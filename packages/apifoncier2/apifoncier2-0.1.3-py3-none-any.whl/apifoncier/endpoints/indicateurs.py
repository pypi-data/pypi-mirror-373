from typing import Optional, List, Union
import pandas as pd

from ..exceptions import ValidationError
from .base import BaseEndpoint


class IndicateurEndpoint(BaseEndpoint):
    """
    Endpoints Indicateurs territoriaux (accès libre) - consommation d'espace et marché immobilier.

    Permet d'interroger les indicateurs de consommation d'espace, d'accessibilité,
    d'activité, de prix et de valorisation via l'API.
    """

    def __init__(self, client):
        """
        Initialise l'endpoint Indicateurs.

        Args:
            client: Instance du client principal.
        """
        super().__init__(client)

    def _process_codes(self, codes: Union[str, List[str]], max_codes: int = 10) -> str:
        """
        Traite les codes en entrée (str ou List[str]) et retourne une chaîne formatée.

        Args:
            codes: Code unique ou liste de codes.
            max_codes: Nombre maximum de codes autorisés.

        Returns:
            Chaîne avec les codes séparés par des virgules.
        """
        if isinstance(codes, str):
            return codes
        elif isinstance(codes, list):
            if len(codes) > max_codes:
                raise ValidationError(f"Maximum {max_codes} codes autorisés")
            if not codes:
                raise ValidationError("La liste de codes ne peut pas être vide")
            return ",".join(codes)
        else:
            raise ValidationError("Les codes doivent être de type str ou List[str]")

    # ==================== CONSOMMATION D'ESPACE (UNIFIÉ) ====================

    def conso(
        self,
        code: str,
        echelle: str,
        annee: Optional[int] = None,
        annee_min: Optional[int] = None,
        annee_max: Optional[int] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Renvoie les indicateurs de consommation d'espace pour la période comprise entre annee_min et annee_max, bornes incluses.

        Args:
            code (str, obligatoire): Code INSEE communal ou départemental.
            echelle (str, obligatoire): 'communes' ou 'departements'.
            annee (int, optionnel): Année spécifique.
            annee_min (int, optionnel): Année minimale.
            annee_max (int, optionnel): Année maximale.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.

        Returns:
            DataFrame ou liste de dictionnaires avec les indicateurs de consommation d'espace.
        """
        if not code:
            raise ValidationError("Le paramètre 'code' est obligatoire")
        if echelle not in ["communes", "departements"]:
            raise ValidationError("L'échelle doit être 'communes' ou 'departements'")

        params = self._build_params(
            annee=annee,
            annee_min=annee_min,
            annee_max=annee_max,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint=f"/indicateurs/conso_espace/{echelle}/{code}",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    # ==================== INDICATEURS DE MARCHÉ - ACCESSIBILITÉ ====================

    def accessibilite(
        self,
        codes_aav: Union[str, List[str]],
        annee: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Retourne les indicateurs d'accessibilité financière tri-annuels issus de DV3F.

        Args:
            codes_aav (str ou List[str], obligatoire): Code(s) INSEE d'une aire d'attraction des villes (max 10).
            annee (str, optionnel): Année.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.

        Returns:
            DataFrame ou liste de dictionnaires avec les indicateurs d'accessibilité.
        """
        if not codes_aav:
            raise ValidationError("Le paramètre 'codes_aav' est obligatoire")

        processed_codes = self._process_codes(codes_aav, max_codes=10)

        params = self._build_params(
            code=processed_codes,
            annee=annee,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/indicateurs/dv3f/accessibilite",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    # ==================== INDICATEURS DE MARCHÉ - ACTIVITÉ ====================

    def activite(
        self,
        codes: Union[str, List[str]],
        echelle: str,
        annee: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Renvoie les indicateurs d'activité du marché tri-annuels issus de DV3F.

        Args:
            codes (str ou List[str], obligatoire): Code(s) INSEE géographique(s) associé(s) à l'échelle (max 10).
            echelle (str, obligatoire): 'communes', 'epci', 'aav', 'departements', 'regions', 'france'.
            annee (str, optionnel): Année centrale de la période de 3 ans.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.

        Returns:
            DataFrame ou liste de dictionnaires avec les indicateurs d'activité.
        """
        if not codes:
            raise ValidationError("Le paramètre 'codes' est obligatoire")
        if not echelle:
            raise ValidationError("Le paramètre 'echelle' est obligatoire")

        echelles_valides = [
            "communes",
            "epci",
            "aav",
            "departements",
            "regions",
            "france",
        ]
        if echelle not in echelles_valides:
            raise ValidationError(
                f"L'échelle doit être parmi : {', '.join(echelles_valides)}"
            )

        processed_codes = self._process_codes(codes, max_codes=10)

        params = self._build_params(
            code=processed_codes,
            echelle=echelle,
            annee=annee,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint="/indicateurs/dv3f/activite",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    # ==================== PRIX (UNIFIÉ ANNUEL/TRIENNAL) ====================

    def prix(
        self,
        codes: Union[str, List[str]],
        echelle: str,
        type_prix: str = "annuel",
        annee: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Renvoie les indicateurs de prix et de volume annuels ou tri-annuels issus de DV3F.

        Args:
            codes (str ou List[str], obligatoire): Code(s) INSEE géographique(s) associé(s) à l'échelle (max 10).
            echelle (str, obligatoire): 'communes', 'epci', 'aav', 'departements', 'regions', 'france'.
            type_prix (str, optionnel): 'annuel' ou 'triennal'.
            annee (str, optionnel): Année de mutation ou centrale pour triennal.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.

        Returns:
            DataFrame ou liste de dictionnaires avec les indicateurs de prix.
        """
        if not codes:
            raise ValidationError("Le paramètre 'codes' est obligatoire")
        if not echelle:
            raise ValidationError("Le paramètre 'echelle' est obligatoire")
        if type_prix not in ["annuel", "triennal"]:
            raise ValidationError("Le type_prix doit être 'annuel' ou 'triennal'")

        echelles_valides = [
            "communes",
            "epci",
            "aav",
            "departements",
            "regions",
            "france",
        ]
        if echelle not in echelles_valides:
            raise ValidationError(
                f"L'échelle doit être parmi : {', '.join(echelles_valides)}"
            )

        processed_codes = self._process_codes(codes, max_codes=10)

        params = self._build_params(
            code=processed_codes,
            echelle=echelle,
            annee=annee,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint=f"/indicateurs/dv3f/prix/{type_prix}",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )

    # ==================== VALORISATION (UNIFIÉ AAV/EPCI) ====================

    def valorisation(
        self,
        code: str,
        echelle: str,
        annee: Optional[str] = None,
        ordering: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = 500,
        paginate: bool = True,
        format_output: str = "dataframe",
    ) -> Union[pd.DataFrame, List[dict]]:
        """
        Renvoie les indicateurs tri-annuels de valorisation d'une commune dans son AAV ou EPCI issus de DV3F.

        Args:
            code (str, obligatoire): Code INSEE de l'AAV ou de l'EPCI.
            echelle (str, obligatoire): 'aav' ou 'epci'.
            annee (str, optionnel): Année centrale de la période de 3 ans.
            ordering (str, optionnel): Champ de tri.
            page (int, optionnel): Page de résultats.
            page_size (int, optionnel): Nombre de résultats par page.
            paginate (bool, optionnel): Pagination automatique.
            format_output (str, optionnel): 'dataframe' ou 'dict'.
            fields (str, optionnel): 'all' pour obtenir tous les champs, None sinon.

        Returns:
            DataFrame ou liste de dictionnaires avec les indicateurs de valorisation.
        """
        if not code:
            raise ValidationError("Le paramètre 'code' est obligatoire")
        if echelle not in ["aav", "epci"]:
            raise ValidationError("L'échelle doit être 'aav' ou 'epci'")

        params = self._build_params(
            annee=annee,
            ordering=ordering,
            page=page,
            page_size=page_size,
        )

        return self._fetch(
            endpoint=f"/indicateurs/dv3f/valorisation/{echelle}/{code}",
            params=params,
            format_output=format_output,
            geo=False,
            paginate=paginate,
        )
