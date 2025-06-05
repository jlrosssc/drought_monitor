import logging
import requests
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, SENSOR_NAME, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    zone = hass.states.get('zone.home')
    if zone and 'latitude' in zone.attributes and 'longitude' in zone.attributes:
        latitude = zone.attributes['latitude']
        longitude = zone.attributes['longitude']
    else:
        latitude = hass.config.latitude
        longitude = hass.config.longitude
        _LOGGER.warning("Falling back to config lat/lon: %s, %s", latitude, longitude)

    async_add_entities([DroughtSensor(latitude, longitude)], True)

class DroughtSensor(Entity):
    def __init__(self, lat, lon):
        self._name = "Drought Monitor"
        self._state = "Unknown"
        self._lat = lat
        self._lon = lon

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        try:
            payload = {
                "f": "json",
                "geometry": f"{self._lon},{self._lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "false"
            }
            response = requests.get(API_URL, params=payload, timeout=10)
            data = response.json()
            self._state = data['features'][0]['attributes']['DM'] if data['features'] else "None"
        except Exception as e:
            _LOGGER.error("Failed to fetch drought data: %s", e)
            self._state = "Error"
