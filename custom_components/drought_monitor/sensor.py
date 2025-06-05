import logging
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SENSOR_NAME, API_URL

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=SENSOR_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    latitude = hass.states.get('zone.home').attributes.get('latitude')
    longitude = hass.states.get('zone.home').attributes.get('longitude')
    name = config.get(CONF_NAME)
    add_entities([DroughtSensor(name, latitude, longitude)], True)

class DroughtSensor(Entity):
    def __init__(self, name, lat, lon):
        self._name = name
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
