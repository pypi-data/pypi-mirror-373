"""
Models for geolocation clusterization.


"""

import random
import re
import traceback
import sys

# from functools import reduce

# from glom import glom, Iter, T, Flatten, Coalesce, Fold, Merge

# from datetime import datetime
from math import cos, radians, degrees

from typing import Optional, Dict, List, Union
from typing_extensions import Self


from pydantic import model_validator

from shapely.geometry import (
    shape,
    Point as _Point,
    Polygon as _Polygon,
    MultiPolygon as _MultiPolygon,
)


# from agptools.containers import walk, rebuild
from agptools.helpers import DATE
from agptools.logs import logger
from agptools.containers import flatten

# from syncmodels.definitions import EDGE
from syncmodels.model import BaseModel, Field
from syncmodels.model.model import Datetime
from syncmodels.model.geojson import (
    GeometryCollection,
    Point,
    polygon_from_points,
    polygon_with_centroid,
)  # , Polygon, MultiPolygon


#
from ..definitions import (
    GEO_DEFAULT_GRID,
    GEO_DEFAULT_REGION,
    GEO_NS,
    GEO_BOUNDARIES_DB,
    GEO_GRID_THING,
    GEO_REGION_THING,
    GEO_CONFIG_THING,
    UID_TYPE,
)
from ..helpers.geojson import POINT


# -------------------------------------------------------------------
# System loggers
# -------------------------------------------------------------------
log = logger(__name__)


# Madrid 40.5, -3.7
# https://metar-taf.com/es/airport/LEMG-malaga-costa-del-sol-airport
# 36.6798, -4.49589
DEFAULT_CENTER = POINT(
    {
        "lon": -4.49589,
        "lat": 36.6798,
    }
)
GEO_FILTER_DEFAULT_GRID_ID = "grid_agp_2x2"
EARTH_RADIUS_KM = 6371.0


class GeoFilterDefinition(BaseModel):
    """Represents a geo filter configuration."""

    id: str = Field(
        description="ID of the GeoFilterDefinition",
        examples=[
            GEO_DEFAULT_GRID,
            GEO_DEFAULT_REGION,
            # f"{GEO_NS}://{GEO_BOUNDARIES_DB}/{GEO_CONFIG_THING}/{GEO_GRID_THING}:default_grid",
            # f"{GEO_NS}://{GEO_BOUNDARIES_DB}/{GEO_CONFIG_THING}/{GEO_REGION_THING}:default_region",
        ],
    )
    id__: Optional[str] = Field(
        None,
        description="Original FQUI of the GeoFilterDefinition",
        examples=[
            # f"{GEO_NS}://{GEO_BOUNDARIES_DB}/{GEO_GRID_THING}/default_grid",
            # f"{GEO_NS}://{GEO_BOUNDARIES_DB}/{GEO_REGION_THING}/default_region",
        ],
    )

    updated: Optional[Datetime] = Field(
        None,
        description="The datetime filter update datetime.",
    )


class GridDefinition(GeoFilterDefinition):
    """Represents a grid definition."""

    # id: str = Field(
    #     "default_grid_definition",
    #     description="The uid of the grid definition",
    #     examples=["default_grid_definition"],
    # )
    center: Point = Field(
        DEFAULT_CENTER,
        description="geographic center of the grid",
        examples=[DEFAULT_CENTER],
    )

    size: float = Field(
        2,  # 2x2, 5x5
        description="grid size in Km",
        examples=[
            5,
        ],
    )
    dx: Optional[float] = Field(
        None,
        description="relative horizontal cell size in degrees. Is computed if not provided",
    )
    dy: Optional[float] = Field(
        None,
        description="relative vertical cell size in degrees. Is computed if not provided",
    )

    @model_validator(mode="after")
    def setup_dx_dy(self) -> Self:
        if not self.dx:
            y0 = self.center.coordinates[0]
            self.dx = degrees(self.size / (EARTH_RADIUS_KM * cos(radians(y0))))
            self.dy = degrees(self.size / EARTH_RADIUS_KM)

        return self

    def coordinates_to_geokey(self, p: List, **data):
        """Fast conversion from geo coordinates to grid point.
        doesn't check for point
        """
        dx = p[0] - self.center.coordinates[0]
        dy = p[1] - self.center.coordinates[1]

        # Round to nearest grid point
        nx = int(dx // self.dx)
        ny = int(dy // self.dy)
        return {"nx": nx, "ny": ny}

    def grid_to_center_coordinates(self, p: Union[List, Dict]):
        """Fast conversion from grid point to coordinates."""
        if isinstance(p, Dict):
            nx = p["nx"]
            ny = p["ny"]
        else:
            nx, ny = p

        x = self.center.coordinates[0] + self.dx * (nx + 0.5)
        y = self.center.coordinates[1] + self.dy * (ny + 0.5)

        point = POINT([x, y])
        return point

    def grid_to_cell(self, p: Union[List, Dict]):
        """Fast conversion from grid point to coordinates."""
        if isinstance(p, Dict):
            nx = p["nx"]
            ny = p["ny"]
        else:
            nx, ny = p

        x0 = self.center.coordinates[0]
        y0 = self.center.coordinates[1]

        x1 = self.center.coordinates[0] + self.dx * nx
        y1 = self.center.coordinates[1] + self.dy * ny

        p00 = Point(coordinates=[x0, y0])
        p01 = Point(coordinates=[x0, y1])
        p11 = Point(coordinates=[x1, y1])
        p10 = Point(coordinates=[x1, y0])

        geojson = polygon_from_points(p00, p01, p11, p10)

        return geojson

    def geokey_to_geojson(self, p: Union[List, Dict]) -> GeometryCollection:
        """Fast conversion from grid point to coordinates."""
        if isinstance(p, Dict):
            nx = p["nx"]
            ny = p["ny"]
        else:
            nx, ny = p

        x0 = self.center.coordinates[0]
        y0 = self.center.coordinates[1]

        x1 = self.center.coordinates[0] + self.dx * nx
        y1 = self.center.coordinates[1] + self.dy * ny

        p00 = Point(coordinates=[x0, y0])
        p01 = Point(coordinates=[x0, y1])
        p11 = Point(coordinates=[x1, y1])
        p10 = Point(coordinates=[x1, y0])

        geojson = polygon_with_centroid(p00, p01, p11, p10)

        return geojson


REGION_CACHE = {}  # external to RegionDefinition


class RegionDefinition(GeoFilterDefinition):
    """Represents a grid grid filter configuration."""

    regions: Optional[Dict[str, GeometryCollection]] = Field(
        None,
        description="The list of regions to filter.",
        examples=["Region A", "Region B"],
    )

    def coordinates_to_geokey(self, p: List, **data):
        """Fast conversion from geo coordinates to region."""
        for uid, region in self.regions.items():
            if not (geometry_collection := REGION_CACHE.get(uid)):
                geometry_collection = shape(region.model_dump())
                REGION_CACHE[uid] = geometry_collection

            point = _Point(*p)
            if any(geom.contains(point) for geom in geometry_collection.geoms):
                # is inside
                return {"district": uid}

        log.debug("[%s] is not inside any region!", p)
        foo = 1

    def geokey_to_geojson(self, *p) -> GeometryCollection:
        """Fast conversion from grid point to coordinates."""

        for key in flatten(p, klass=str):
            if region := self.regions.get(key):
                return region


# TODO: move to definitions ...
DEVICE_ID = "device_id"


class DeviceDefinition(GeoFilterDefinition):
    def coordinates_to_geokey(self, p: List, **data):
        """TBD"""
        if device_id := data.get(DEVICE_ID):
            return {"device_id": device_id}
        log.warning("[%s] has not '%s'", p, DEVICE_ID)
        return {}

    def geokey_to_geojson(self, *p) -> GeometryCollection:
        """TBD"""
        pass


# ---------------------------------------------------------
# Geo-References
# ---------------------------------------------------------
class GeoReference(BaseModel):
    """Represents a geo filter configuration."""

    id: str = Field(
        description="ID of the GeoFilterDefinition",
        examples=[
            "default",
        ],
    )
    id__: str = Field(
        description="ID of the GeoFilterDefinition",
        examples=[
            f"{GEO_NS}://{GEO_BOUNDARIES_DB}/{GEO_GRID_THING}/default:p0p0",
        ],
    )


class GridGeoReference(GeoReference):
    """Represents a geo filter configuration."""

    # id__: str = Field(
    #     description="URI of the referenced item",
    #     # examples=["bar_geofilter_config"]
    # )
    nx: int = Field(description="relative horizontal cell from grid center")
    ny: int = Field(description="relative vertical cell from grid center")


# ---------------------------------------------------------
# Definitions
# ---------------------------------------------------------

center = DEFAULT_CENTER.model_dump()
GEO_FILTER_DEFAULT_GRID_DEFINITION = GridDefinition(
    **{"id": GEO_FILTER_DEFAULT_GRID_ID, "center": center}
)
# {'id': 'grid_madrid_2x2',
# 'id__': None,
# 'updated': None,
# 'center': {'type': 'Point', 'coordinates': [-3.7, 40.5]},
# 'size': 2,
# 'dx': 0.018024001016756164,
# 'dy': 0.01798643211837461}


# ---------------------------------------------------------
# GeoDiscriminator
# ---------------------------------------------------------
# TODO: split into several files all classes that work together
class GeoDiscriminator:
    def geo_key(self, point):
        raise NotImplementedError()


class GridDiscriminator(GeoDiscriminator):
    def geo_key(self, point):
        raise NotImplementedError()
