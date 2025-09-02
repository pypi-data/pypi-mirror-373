import requests
from typing import Any, Dict, Optional, Tuple


class WeatherError(Exception):
    pass


class WeatherClient:
    """
    Simple weather client built on Open-Meteo APIs (no API key required).

    - Geocoding: https://geocoding-api.open-meteo.com/v1/search?name={name}
    - Forecast:  https://api.open-meteo.com/v1/forecast
    """

    def __init__(self, session: Optional[requests.Session] = None, timeout: int = 30):
        self.session = session or requests.Session()
        self.timeout = timeout

    # -------- helpers --------
    def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.session.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise WeatherError(f"Network error: {e}")
        except ValueError:
            raise WeatherError("Invalid JSON response")

    def geocode(self, name: str) -> Tuple[float, float, str]:
        """
        Resolve a place name to (lat, lon, resolved_name).
        Raises WeatherError if not found.
        """
        data = self._get(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": name, "count": 1, "language": "en", "format": "json"},
        )
        results = data.get("results") or []
        if not results:
            raise WeatherError(f"Location not found: {name}")
        r0 = results[0]
        lat = float(r0.get("latitude"))
        lon = float(r0.get("longitude"))
        resolved = ", ".join([p for p in [r0.get("name"), r0.get("country")]
                               if p]) or name
        return lat, lon, resolved

    def current(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get current weather for coordinates.
        Returns a small dict with temperature (C), wind_speed (km/h), weather_code, and raw payload.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m,apparent_temperature",
            "timezone": "auto",
        }
        data = self._get("https://api.open-meteo.com/v1/forecast", params)
        cur = (data.get("current") or {})
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "temperature_c": cur.get("temperature_2m"),
            "apparent_temperature_c": cur.get("apparent_temperature"),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
            "weather_code": cur.get("weather_code"),
            "raw": data,
        }

    def daily_forecast(self, latitude: float, longitude: float, days: int = 3) -> Dict[str, Any]:
        """
        Get simple daily forecast for up to `days` days.
        Returns date, tmin, tmax, precipitation_sum and code arrays plus raw payload.
        """
        if days < 1:
            days = 1
        if days > 16:
            # Open-Meteo free allows up to 16 days typically
            days = 16
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": days,
            "timezone": "auto",
        }
        data = self._get("https://api.open-meteo.com/v1/forecast", params)
        d = data.get("daily") or {}
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "days": days,
            "date": d.get("time"),
            "tmax_c": d.get("temperature_2m_max"),
            "tmin_c": d.get("temperature_2m_min"),
            "precipitation_sum_mm": d.get("precipitation_sum"),
            "weather_code": d.get("weather_code"),
            "raw": data,
        }

    # -------- convenience --------
    def resolve_location(self, query: str) -> Tuple[float, float, str]:
        """Accepts "<lat>,<lon>" or a place name; returns (lat, lon, resolved_name)."""
        q = query.strip()
        # try comma-separated coordinates
        if "," in q:
            try:
                lat_s, lon_s = [p.strip() for p in q.split(",", 1)]
                lat = float(lat_s)
                lon = float(lon_s)
                return lat, lon, f"{lat},{lon}"
            except ValueError:
                pass
        # fallback to geocoding
        return self.geocode(q)
