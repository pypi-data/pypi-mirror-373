"""The main geojson_aoi package."""

from ._async.parser import parse_aoi_async as parse_aoi_async
from ._sync.parser import parse_aoi as parse_aoi
from .dbconfig import DbConfig as DbConfig
