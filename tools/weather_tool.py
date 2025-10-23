# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict, Any

def get_weather_by_city(city: str, country_code: str = "BR") -> Dict[str, Any]:
    ow_key = os.getenv("OPENWEATHER_API_KEY")
    wa_key = os.getenv("WEATHERAPI_KEY")

    last_error = ""

    if ow_key:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": f"{city},{country_code}", "appid": ow_key, "units": "metric", "lang": "pt_br"}
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            return {
                "provider": "openweathermap",
                "city": city,
                "temp_c": data.get("main", {}).get("temp"),
                "feels_like_c": data.get("main", {}).get("feels_like"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_kph": round((data.get("wind", {}).get("speed", 0) or 0) * 3.6, 1),
                "condition": (data.get("weather", [{}])[0] or {}).get("description", ""),
                "raw": data,
            }
        except Exception as e:
            last_error = f"OpenWeather error: {e}"

    if wa_key:
        try:
            url = "https://api.weatherapi.com/v1/current.json"
            params = {"key": wa_key, "q": city, "lang": "pt"}
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            current = data.get("current", {})
            condition = (current.get("condition") or {}).get("text", "")
            wind_kph = current.get("wind_kph")
            return {
                "provider": "weatherapi",
                "city": data.get("location", {}).get("name", city),
                "temp_c": current.get("temp_c"),
                "feels_like_c": current.get("feelslike_c"),
                "humidity": current.get("humidity"),
                "wind_kph": wind_kph,
                "condition": condition,
                "raw": data,
            }
        except Exception as e:
            last_error = f"WeatherAPI error: {e}"

    raise RuntimeError(f"Não foi possível obter o clima. {last_error or 'Defina OPENWEATHER_API_KEY ou WEATHERAPI_KEY.'}")
