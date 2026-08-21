import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

_cache_session = requests_cache.CachedSession(".cache", expire_after=1800)
_retry_session = retry(_cache_session, retries=3, backoff_factor=0.3)
_client = openmeteo_requests.Client(session=_retry_session)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_frame(lat: float, lon: float, past_hours: int = 24) -> pd.DataFrame:
    # it returns a DataFrame of hourly precipitation+soil moisture for one point.
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "precipitation",
            "soil_moisture_0_to_1cm",
            "temperature_2m",
        ],
        "past_hours": past_hours,
        "forecast_hours": 1,
        "timezone": "auto",
    }
    responses = _client.weather_api(OPEN_METEO_URL, params=params)
    response = responses[0]
    hourly = response.Hourly()

    df=pd.DataFrame({
        "timestamp":pd.date_range(
            start=pd.to_datetime(hourly.Time(),unit="s",utc=True),
            end=pd.to_datetime(hourly.TimeEnd(),unit="s",utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "precipitation_mm":hourly.Variables(0).ValuesInt64AsNumpy(),
        "soil_moisture":hourly.Variables(1).ValuesAsNumpy(),
        "temperature_c": hourly.Variables(2).ValuesAsNumpy(),
    })
    return df

def get_weather_features(lat: float, lon: float) -> dict:
    """Collapses the hourly frame into the scalar features the model needs."""
    df = get_weather_frame(lat, lon)
    return {
        "rain_24h_mm": float(df["precipitation_mm"].sum()),
        "rain_last_1h_mm": float(df["precipitation_mm"].iloc[-1]),
        "soil_moisture": float(df["soil_moisture"].iloc[-1]),
        "temperature_c": float(df["temperature_c"].iloc[-1]),
    }