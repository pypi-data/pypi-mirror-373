from pydantic import BaseModel, Field, validator
from typing import List, Union
from shapely.geometry import (
    shape,
    Point as _Point,
    Polygon as _Polygon,
    MultiPolygon as _MultiPolygon,
)
from ..definitions import GEOSPECS_KEYS


class BaseGeometry(BaseModel):
    "base of all geometries"


class Point(BaseGeometry):
    # Literal['Point'] can't be serialized to json
    type: str = "Point"
    coordinates: List[float]

    @validator("coordinates")
    def validate_point(cls, v):
        if len(v) != 2:
            raise ValueError(
                "Point coordinates must contain exactly 2 values (longitude, latitude)"
            )
        return v


class LineString(BaseGeometry):
    # Literal['LineString'] can't be serialized to json
    type: str = "LineString"

    coordinates: List[List[float]]

    @validator("coordinates")
    def validate_linestring(cls, v):
        if len(v) < 2:
            raise ValueError("LineString must contain at least two points")
        for coord in v:
            if len(coord) != 2:
                raise ValueError(
                    "Each coordinate must contain exactly 2 values (longitude, latitude)"
                )
        return v


class Polygon(BaseGeometry):
    # Literal['Polygon'] can't be serialized to json
    type: str = "Polygon"

    coordinates: List[List[List[float]]]

    @validator("coordinates")
    def validate_polygon(cls, v):
        if len(v) < 1:
            raise ValueError("Polygon must have at least one ring")
        for ring in v:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError(
                    "Each linear ring in a polygon must have at least 4 coordinates and be closed"
                )
            for coord in ring:
                l = len(coord)
                if l == 3:
                    # remove altitude
                    coord.pop()
                elif l != 2:
                    raise ValueError(
                        f"Each coordinate must contain exactly 2 values (longitude, latitude) but I got: {coord}"
                    )
        return v

    def contains(self, other) -> bool:
        # TODO: agp: Cache boundaries
        container = shape(self.model_dump())
        other = shape(other.model_dump())

        result = container.contains(other)
        return result


class MultiPoint(BaseGeometry):

    # Literal['MultiPoint'] can't be serialized to json
    type: str = "MultiPoint"

    coordinates: List[List[float]]

    @validator("coordinates", each_item=True)
    def validate_multipoint(cls, v):
        if len(v) != 2:
            raise ValueError(
                "Each point in MultiPoint must contain exactly 2 values (longitude, latitude)"
            )
        return v


class MultiLineString(BaseGeometry):

    # Literal['MultiLineString'] can't be serialized to json
    type: str = "MultiLineString"
    coordinates: List[List[List[float]]]

    @validator("coordinates")
    def validate_multilinestring(cls, v):
        for line in v:
            if len(line) < 2:
                raise ValueError(
                    "Each LineString in MultiLineString must contain at least two points"
                )
            for coord in line:
                if len(coord) != 2:
                    raise ValueError(
                        "Each coordinate must contain exactly 2 values (longitude, latitude)"
                    )
        return v


class MultiPolygon(BaseGeometry):
    # Literal['MultiPolygon'] can't be serialized to json
    type: str = "MultiPolygon"

    coordinates: List[List[List[List[float]]]]

    @validator("coordinates")
    def validate_multipolygon(cls, v):
        for polygon in v:
            if len(polygon) < 1:
                raise ValueError("Each Polygon must have at least one ring")

            Polygon.validate_polygon(polygon)

            # for ring in polygon:
            #     if len(ring) < 4 or ring[0] != ring[-1]:
            #         raise ValueError(
            #             "Each linear ring in a polygon must have at least 4 coordinates and be closed"
            #         )
            #     for coord in ring:
            #         if len(coord) != 2:
            #             raise ValueError(
            #                 "Each coordinate must contain exactly 2 values (longitude, latitude)"
            #             )
        return v


class GeometryCollection(BaseGeometry):

    # Literal['GeometryCollection'] can't be serialized to json
    type: str = "GeometryCollection"
    geometries: List[
        Union[
            Point,
            LineString,
            Polygon,
            MultiPoint,
            MultiLineString,
            MultiPolygon,
        ]
    ]

    @validator("geometries", pre=True, each_item=True)
    def validate_geometries(cls, v):
        if "type" not in v and not hasattr(v, "type"):
            raise ValueError(
                "Each geometry in the GeometryCollection must have a 'type' field"
            )
        return v


class Feature(BaseGeometry):
    # Literal['Feature'] can't be serialized to json
    type: str = "Feature"
    geometry: Union[
        Point,
        LineString,
        Polygon,
        MultiPoint,
        MultiLineString,
        MultiPolygon,
        GeometryCollection,
    ]
    properties: dict = {}


class FeatureCollection(BaseGeometry):
    # Literal['FeatureCollection'] can't be serialized to json
    type: str = "FeatureCollection"
    features: List[Feature]


# ------------------------------------------
# constructor helpers
# ------------------------------------------
GEO_FACTORY = {
    "Point": Point,
    "LineString": LineString,
    "Polygon": Polygon,
    "MultiPoint": MultiPoint,
    "MultiLineString": MultiLineString,
    "MultiPolygon": MultiPolygon,
    "GeometryCollection": GeometryCollection,
    "Feature": Feature,
    "FeatureCollection": FeatureCollection,
}


def to_geojson(data):
    factory = GEO_FACTORY[data["type"]]
    item = factory(**data)
    return item


def GEOPOINT(longitude, latitude):
    item = Point(coordinates=[longitude, latitude])
    return item


def to_geometry(coords):
    if coords:
        info = to_geospecs(coords)
        if info:
            return info.get(GEOSPECS_KEYS[0])
    else:
        return None  # just debuging


# USE Defines for these parameters


def to_geospecs(coords):
    if len(coords) in (2, 3) and isinstance(coords[0], float):
        _geometry = _Point(coords)
        geojson = _geometry.__geo_interface__
        geometry = Point(**geojson)
    else:
        polygons = [_Polygon(s) for s in coords]
        _geometry = _MultiPolygon(polygons)
        geojson = _geometry.__geo_interface__
        geometry = MultiPolygon(**geojson)

    # Note: _geometry returns tuples, not list (isn't compatible
    # Note: 100% with geojson specs, so we need to recreate the
    # Note: information using lists instead
    geojson = geometry.model_dump()
    return {
        GEOSPECS_KEYS[0]: geometry,
        GEOSPECS_KEYS[1]: _geometry,
        GEOSPECS_KEYS[2]: geojson,
    }


def update_geospecs(data, coords):
    geospecs = to_geospecs(coords)
    data.update(geospecs)


# ------------------------------------------
# helpers
# ------------------------------------------
def polygon_from_points(*points, closed=True) -> Polygon:
    coordinates = [_.coordinates for _ in points]
    if coordinates and closed:
        coordinates.append(coordinates[0])
    polygon = Polygon(coordinates=[coordinates])
    return polygon


def centroid(polygon: Polygon) -> Point:

    _polygon = shape(polygon.model_dump())
    coords = list(_polygon.centroid.coords)
    centroid = Point(coordinates=coords[0])
    return centroid


def polygon_with_centroid(*points, closed=True) -> GeometryCollection:
    cell = polygon_from_points(*points, closed=closed)
    center = centroid(cell)

    # feature0 = Feature(geometry=cell, properties={"name": "cell",})
    # feature1 = Feature(geometry=center, properties={"name": "center",})
    # feature = FeatureCollection(features=[feature0, feature1])

    collection = GeometryCollection(geometries=[cell, center])

    return collection


# ------------------------------------------
# simple tests
# ------------------------------------------
