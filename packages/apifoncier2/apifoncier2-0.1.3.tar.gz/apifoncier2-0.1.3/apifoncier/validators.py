import re
from typing import Optional, Dict, Any, Union, List, Tuple
from .exceptions import ValidationError


def validate_code_insee(code: str):
    """
    Valide un code INSEE.

    Args:
        code_insee: Code INSEE à valider

    Raises:
        ValidationError: Si le code INSEE est invalide
    """
    if not isinstance(code, str):
        raise ValidationError("Le code INSEE doit être une chaîne de caractères")

    # Pattern pour codes corses : 2A ou 2B suivi de 3 chiffres
    corse_pattern = r"^2[ABab]\d{3}$"
    classic_pattern = r"^\d{5}$"

    if not (re.match(corse_pattern, code) or re.match(classic_pattern, code)):
        raise ValidationError("Le code INSEE doit être au format 2A123, 2B123 ou 12345")


def validate_coddep(code: str):
    """
    Valide un code INSEE.

    Args:
        code_insee: Code INSEE à valider

    Raises:
        ValidationError: Si le code INSEE est invalide
    """
    if not isinstance(code, str):
        raise ValidationError("Le code département doit être une chaîne de caractères")

    # Pattern pour codes corses : 2A ou 2B
    corse_pattern = r"^2[ABab]$"
    classic_pattern = r"^\d{2,3}$"

    if not (re.match(corse_pattern, code) or re.match(classic_pattern, code)):
        raise ValidationError(
            "Le code INSEE doit être au format 2A, 2B ou 01 à 95, 971 à 976"
        )


def validate_bbox(bbox: List[float], max_size: float):
    """
    Valide une bounding box.

    Args:
        bbox: Liste [xmin, ymin, xmax, ymax]
        max_size: Taille maximale autorisée en degrés

    Raises:
        ValidationError: Si la bounding box est invalide
    """
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise ValidationError("La bounding box doit être une liste de 4 éléments")

    if not all(isinstance(coord, (int, float)) for coord in bbox):
        raise ValidationError("Les coordonnées doivent être numériques")

    lon_min, lat_min, lon_max, lat_max = bbox
    if lon_min >= lon_max or lat_min >= lat_max:
        raise ValidationError("Bounding box invalide: min >= max")

    width = lon_max - lon_min
    height = lat_max - lat_min

    if width > max_size or height > max_size:
        raise ValidationError(
            f"L'emprise ne doit pas excéder {max_size}° x {max_size}°"
        )


def validate_contains_lon_lat(contains_lon_lat: str) -> Tuple[List[float], str]:
    """
    Valide et convertit contains_lon_lat en bbox et contains_geom.

    Args:
        contains_lon_lat: Coordonnées sous forme "lon,lat"

    Returns:
        Tuple[bbox, contains_geom]: Bbox générée et géométrie GeoJSON

    Raises:
        ValidationError: Si les coordonnées sont invalides
    """
    if not isinstance(contains_lon_lat, list) or len(contains_lon_lat) != 2:
        raise ValidationError("Le contains_lon_lat doit être une liste de 2 éléments")

    if not all(isinstance(coord, (int, float)) for coord in contains_lon_lat):
        raise ValidationError("Les coordonnées doivent être numériques")

    lon, lat = contains_lon_lat

    # Validation des coordonnées géographiques
    if not (-180 <= lon <= 180):
        raise ValidationError("Longitude doit être entre -180 et 180")
    if not (-90 <= lat <= 90):
        raise ValidationError("Latitude doit être entre -90 et 90")

    bbox = [lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01]
    contains_geom = f"{{'type':'Point','coordinates':[{lon},{lat}]}}"

    return bbox, contains_geom


def validate_lon_lat_point(lon_lat: List[float], interval: float = 0.01) -> List[float]:
    """
    Valide des coordonnées lon/lat et génère une bbox.

    Args:
        lon_lat: Liste [longitude, latitude]

    Returns:
        Bbox générée autour du point

    Raises:
        ValidationError: Si les coordonnées sont invalides
    """
    if not isinstance(lon_lat, list):
        raise ValidationError("lon_lat doit être une liste")

    if len(lon_lat) != 2:
        raise ValidationError("lon_lat doit contenir exactement 2 valeurs")

    try:
        lon, lat = float(lon_lat[0]), float(lon_lat[1])
    except (ValueError, TypeError):
        raise ValidationError("Les coordonnées lon_lat doivent être numériques")

    # Validation des coordonnées géographiques
    if not (-180 <= lon <= 180):
        raise ValidationError("Longitude doit être entre -180 et 180")
    if not (-90 <= lat <= 90):
        raise ValidationError("Latitude doit être entre -90 et 90")

    return [lon - interval, lat - interval, lon + interval, lat + interval]
