"""Sentinel Hub ingestion — NDWI (water) and NDVI (vegetation) only, as numpy arrays."""
import os
import numpy as np
from dotenv import load_dotenv
from sentinelhub import (
    SHConfig, BBox, CRS, SentinelHubRequest,
    DataCollection, MimeType, bbox_to_dimensions,
)

load_dotenv()

config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Copernicus Dataspace requires the data collection explicitly bound to its service URL —
# without this, requests go to the old services.sentinel-hub.com and get a 401.
s2l2a_cdse = DataCollection.SENTINEL2_L2A.define_from(
    "s2l2a_cdse", service_url="https://sh.dataspace.copernicus.eu"
)

EVALSCRIPT_NDWI_NDVI = """
//VERSION=3
function setup() {
  return {
    input: ["B03", "B04", "B08"],
    output: { bands: 2, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  let ndwi = (s.B03 - s.B08) / (s.B03 + s.B08 + 1e-6);
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04 + 1e-6);
  return [ndwi, ndvi];
}
"""


def get_ndwi_ndvi(bbox_coords: list[float], resolution: int = 60) -> dict:
    """
    bbox_coords: [min_lon, min_lat, max_lon, max_lat]
    Returns mean NDWI/NDVI over the box — lightweight scalars, not the full array.
    """
    bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=resolution)

    request = SentinelHubRequest(
        evalscript=EVALSCRIPT_NDWI_NDVI,
        input_data=[SentinelHubRequest.input_data(
            data_collection=s2l2a_cdse,
            time_interval=("2026-08-01", "2026-08-15"),
            mosaicking_order="leastCC",
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config,
    )
    arr = request.get_data()[0]  # shape (H, W, 2), small array, kept in-memory only
    ndwi_mean = float(np.nanmean(arr[:, :, 0]))
    ndvi_mean = float(np.nanmean(arr[:, :, 1]))
    return {"ndwi": ndwi_mean, "ndvi": ndvi_mean}