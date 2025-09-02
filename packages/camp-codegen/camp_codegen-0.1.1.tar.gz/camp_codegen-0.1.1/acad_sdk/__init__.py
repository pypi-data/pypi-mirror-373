# acad_sdk
# Minimal Python SDK for AI Deployment API

from .client import AcadClient, AcadError
from .weather import WeatherClient, WeatherError

__all__ = [
    "AcadClient",
    "AcadError",
    "WeatherClient",
    "WeatherError",
]
__version__ = "0.1.0"
