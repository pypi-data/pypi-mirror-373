from .base import BaseEndpoint
from .dvf_opendata import DVFOpenDataEndpoint
from .cartofriches import CartofrichesEndpoint
from .dv3f import DV3FEndpoint
from .ff import FFEndpoint
from .indicateurs import IndicateurEndpoint

__all__ = [
    "BaseEndpoint",
    "DVFOpenDataEndpoint",
    "DV3FEndpoint",
    "FFEndpoint",
    "CartofrichesEndpoint",
    "IndicateurEndpoint",
]
