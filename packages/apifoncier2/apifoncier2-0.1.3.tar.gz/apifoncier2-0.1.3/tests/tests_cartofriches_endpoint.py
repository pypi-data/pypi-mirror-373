"""Tests pour l'endpoint Cartofriches."""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
import geopandas as gpd

from apifoncier.endpoints.cartofriches import CartofrichesEndpoint
from apifoncier.exceptions import ValidationError


class TestCartofrichesEndpoint:
    """Tests pour la classe CartofrichesEndpoint."""

    @pytest.fixture
    def mock_client(self):
        """Mock du client ApiFoncier."""
        client = Mock()
        client.config.base_url = "https://datafoncier.cerema.fr/api"
        return client

    @pytest.fixture
    def endpoint(self, mock_client):
        """Instance de CartofrichesEndpoint pour les tests."""
        return CartofrichesEndpoint(mock_client)

    @pytest.fixture
    def mock_friches_response(self):
        """Réponse simulée pour les friches."""
        return {
            "count": 2,
            "next": None,
            "results": [
                {
                    "site_id": "SITE_001",
                    "nom_site": "Friche industrielle A",
                    "surface": 5000.0,
                    "urba_zone_type": "AU",
                    "commune": "Lille",
                },
                {
                    "site_id": "SITE_002",
                    "nom_site": "Friche urbaine B",
                    "surface": 3000.0,
                    "urba_zone_type": "U",
                    "commune": "Roubaix",
                },
            ],
        }

    @pytest.fixture
    def mock_geofriches_response(self):
        """Réponse simulée pour les géofriches."""
        return {
            "type": "FeatureCollection",
            "count": 1,
            "next": None,
            "features": [
                {
                    "type": "Feature",
                    "id": "SITE_001",
                    "properties": {
                        "site_id": "SITE_001",
                        "nom_site": "Friche géolocalisée",
                        "surface": 4000.0,
                    },
                    "geometry": {"type": "Point", "coordinates": [3.0632, 50.6292]},
                }
            ],
        }

    # ======================== TESTS MÉTHODE FRICHES ========================

    def test_friches_with_code_insee_success(self, endpoint, mock_friches_response):
        """Test réussi avec code INSEE."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(code_insee="59350")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        endpoint._fetch.assert_called_once()

        # Vérification des paramètres passés
        call_args = endpoint._fetch.call_args
        assert call_args[1]["endpoint"] == "/cartofriches/friches"
        assert "code_insee" in call_args[1]["params"]

    def test_friches_with_codes_insee_success(self, endpoint, mock_friches_response):
        """Test réussi avec liste de codes INSEE."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(codes_insee=["59350", "59100"])

        assert isinstance(result, pd.DataFrame)
        endpoint._fetch.assert_called_once()

        # Vérification que les codes sont joints par virgule
        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["code_insee"] == "59350,59100"

    def test_friches_with_coddep_success(self, endpoint, mock_friches_response):
        """Test réussi avec code département."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(coddep="59")

        assert isinstance(result, pd.DataFrame)
        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["coddep"] == "59"

    def test_friches_with_bbox_success(self, endpoint, mock_friches_response):
        """Test réussi avec bounding box."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        bbox = [3.0, 50.6, 3.5, 51.0]
        result = endpoint.friches(in_bbox=bbox)

        assert isinstance(result, pd.DataFrame)
        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["in_bbox"] == "3.0,50.6,3.5,51.0"

    def test_friches_with_lon_lat_success(self, endpoint, mock_friches_response):
        """Test réussi avec coordonnées lon/lat."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(lon_lat=[3.0632, 50.6292])

        assert isinstance(result, pd.DataFrame)
        call_params = endpoint._fetch.call_args[1]["params"]
        # Vérifie que la bbox a été générée automatiquement
        assert "in_bbox" in call_params

    def test_friches_with_contains_lon_lat_success(
        self, endpoint, mock_friches_response
    ):
        """Test réussi avec contains_lon_lat."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(contains_lon_lat=[3.0632, 50.6292])

        assert isinstance(result, pd.DataFrame)
        call_params = endpoint._fetch.call_args[1]["params"]
        assert "contains_geom" in call_params
        assert "Point" in call_params["contains_geom"]

    def test_friches_with_surface_filters(self, endpoint, mock_friches_response):
        """Test avec filtres de surface."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(
            code_insee="59350", surface_min=1000.0, surface_max=10000.0
        )

        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["surface_min"] == 1000.0
        assert call_params["surface_max"] == 10000.0

    def test_friches_with_all_optional_params(self, endpoint, mock_friches_response):
        """Test avec tous les paramètres optionnels."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        result = endpoint.friches(
            code_insee="59350",
            surface_min=500.0,
            surface_max=5000.0,
            urba_zone_type="AU",
            fields="all",
            ordering="surface",
            page=1,
            page_size=100,
            paginate=True,
            format_output="dict",
        )

        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["urba_zone_type"] == "AU"
        assert call_params["fields"] == "all"
        assert call_params["ordering"] == "surface"
        assert call_params["page"] == 1
        assert call_params["page_size"] == 100

    # ===================== TESTS DE VALIDATION D'ERREURS ===================

    def test_friches_no_location_param_error(self, endpoint):
        """Test d'erreur quand aucun paramètre de localisation."""
        with pytest.raises(
            ValidationError, match="Au moins un paramètre de localisation"
        ):
            endpoint.friches()

    def test_friches_invalid_code_insee_error(self, endpoint):
        """Test d'erreur avec code INSEE invalide."""
        with pytest.raises(
            ValidationError,
            match="Le code INSEE doit être au format 2A123, 2B123 ou 12345",
        ):
            endpoint.friches(code_insee="invalid")

    def test_friches_too_many_codes_insee_error(self, endpoint):
        """Test d'erreur avec trop de codes INSEE."""
        codes = [f"59{i:03d}" for i in range(11)]  # 11 codes
        with pytest.raises(ValidationError, match="Maximum 10 codes INSEE"):
            endpoint.friches(codes_insee=codes)

    def test_friches_invalid_coddep_error(self, endpoint):
        """Test d'erreur avec code département invalide."""
        with pytest.raises(
            ValidationError,
            match="Le code INSEE doit être au format 2A, 2B ou 01 à 95, 971 à 976",
        ):
            endpoint.friches(coddep="invalid")

    def test_friches_bbox_too_large_error(self, endpoint):
        """Test d'erreur avec bbox trop grande."""
        large_bbox = [3.0, 50.6, 4.5, 52.0]  # > 1.0° x 1.0°
        with pytest.raises(
            ValidationError, match="L'emprise ne doit pas excéder 1.0° x 1.0°"
        ):
            endpoint.friches(in_bbox=large_bbox)

    def test_friches_invalid_bbox_error(self, endpoint):
        """Test d'erreur avec bbox invalide."""
        with pytest.raises(ValidationError, match="Bounding box invalide"):
            endpoint.friches(in_bbox=[3.0, 50.6, 2.0, 50.5])  # min > max

    def test_friches_invalid_contains_lon_lat_error(self, endpoint):
        """Test d'erreur avec contains_lon_lat invalide."""
        with pytest.raises(
            ValidationError,
            match="Le contains_lon_lat doit être une liste de 2 éléments",
        ):
            endpoint.friches(contains_lon_lat=[3.0, 50.6, 2.0])  # Trop d'éléments

    def test_friches_invalid_lon_lat_error(self, endpoint):
        """Test d'erreur avec lon_lat invalide."""
        with pytest.raises(
            ValidationError, match="lon_lat doit contenir exactement 2 valeurs"
        ):
            endpoint.friches(lon_lat=[3.0])

    # ======================= TESTS MÉTHODE GEOFRICHES ======================

    def test_geofriches_success(self, endpoint, mock_geofriches_response):
        """Test réussi pour geofriches."""
        endpoint._fetch = Mock(
            return_value=gpd.GeoDataFrame.from_features(mock_geofriches_response)
        )

        result = endpoint.geofriches(code_insee="59350")

        assert isinstance(result, gpd.GeoDataFrame)
        endpoint._fetch.assert_called_once()

        # Vérifier que geo=True est passé
        call_args = endpoint._fetch.call_args[1]
        assert call_args["geo"] is True
        assert call_args["endpoint"] == "/cartofriches/geofriches"

    def test_geofriches_with_bbox(self, endpoint, mock_geofriches_response):
        """Test geofriches avec bbox."""
        endpoint._fetch = Mock(
            return_value=gpd.GeoDataFrame.from_features(mock_geofriches_response)
        )

        bbox = [3.0, 50.6, 3.1, 50.7]
        result = endpoint.geofriches(in_bbox=bbox, paginate=True)

        call_params = endpoint._fetch.call_args[1]["params"]
        assert call_params["in_bbox"] == "3.0,50.6,3.1,50.7"
        assert endpoint._fetch.call_args[1]["paginate"] is True

    def test_geofriches_validation_error(self, endpoint):
        """Test d'erreur de validation pour geofriches."""
        with pytest.raises(ValidationError):
            endpoint.geofriches()  # Aucun paramètre de localisation

    # ==================== TESTS MÉTHODE FRICHE_BY_ID ====================

    def test_friche_by_id_success(self, endpoint):
        """Test réussi pour friche_by_id."""
        mock_friche_detail = {
            "site_id": "SITE_123",
            "nom_site": "Friche détaillée",
            "surface": 2500.0,
            "description": "Description complète",
        }
        endpoint._fetch = Mock(return_value=mock_friche_detail)

        result = endpoint.friche_by_id("SITE_123")

        assert result == mock_friche_detail
        endpoint._fetch.assert_called_once_with(
            endpoint="/cartofriches/friches/SITE_123",
            params={},
            format_output="dict",
            geo=False,
            paginate=False,
        )

    def test_friche_by_id_empty_site_id_error(self, endpoint):
        """Test d'erreur avec site_id vide."""
        with pytest.raises(ValidationError, match="site_id est obligatoire"):
            endpoint.friche_by_id("")

    def test_friche_by_id_none_site_id_error(self, endpoint):
        """Test d'erreur avec site_id None."""
        with pytest.raises(ValidationError, match="site_id est obligatoire"):
            endpoint.friche_by_id(None)

    # ===================== TESTS D'INTÉGRATION =========================

    def test_friches_format_output_variations(self, endpoint, mock_friches_response):
        """Test des différents formats de sortie."""
        # Test format dataframe
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )
        result_df = endpoint.friches(code_insee="59350", format_output="dataframe")
        assert isinstance(result_df, pd.DataFrame)

        # Test format dict
        endpoint._fetch = Mock(return_value=mock_friches_response["results"])
        result_dict = endpoint.friches(code_insee="59350", format_output="dict")
        assert isinstance(result_dict, list)

    # ==================== TESTS DE PERFORMANCE/EDGE CASES ================

    def test_friches_empty_response(self, endpoint):
        """Test avec réponse vide."""
        endpoint._fetch = Mock(return_value=pd.DataFrame())

        result = endpoint.friches(code_insee="59350")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_geofriches_empty_response(self, endpoint):
        """Test geofriches avec réponse vide."""
        endpoint._fetch = Mock(return_value=gpd.GeoDataFrame())

        result = endpoint.geofriches(code_insee="59350")

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) == 0

    def test_friches_boundary_bbox_size(self, endpoint, mock_friches_response):
        """Test avec bbox à la limite autorisée (1.0° x 1.0°)."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        # Exactement 1.0° x 1.0° - devrait passer
        boundary_bbox = [3.0, 50.6, 4.0, 51.6]
        result = endpoint.friches(in_bbox=boundary_bbox)

        assert isinstance(result, pd.DataFrame)

    def test_friches_boundary_codes_count(self, endpoint, mock_friches_response):
        """Test avec exactement 10 codes INSEE (limite)."""
        endpoint._fetch = Mock(
            return_value=pd.DataFrame(mock_friches_response["results"])
        )

        codes = [f"59{i:03d}" for i in range(10)]  # Exactement 10 codes
        result = endpoint.friches(codes_insee=codes)

        assert isinstance(result, pd.DataFrame)
        call_params = endpoint._fetch.call_args[1]["params"]
        assert len(call_params["code_insee"].split(",")) == 10

    # ======================= TESTS DE FIXTURES ==========================

    def test_mock_friches_response_structure(self, mock_friches_response):
        """Vérifie la structure de la réponse simulée."""
        assert "count" in mock_friches_response
        assert "results" in mock_friches_response
        assert isinstance(mock_friches_response["results"], list)
        assert len(mock_friches_response["results"]) > 0

        # Vérifier la structure d'une friche
        friche = mock_friches_response["results"][0]
        required_fields = ["site_id", "nom_site", "surface"]
        for field in required_fields:
            assert field in friche

    def test_mock_geofriches_response_structure(self, mock_geofriches_response):
        """Vérifie la structure de la réponse géographique simulée."""
        assert mock_geofriches_response["type"] == "FeatureCollection"
        assert "features" in mock_geofriches_response
        assert isinstance(mock_geofriches_response["features"], list)

        if mock_geofriches_response["features"]:
            feature = mock_geofriches_response["features"][0]
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature
