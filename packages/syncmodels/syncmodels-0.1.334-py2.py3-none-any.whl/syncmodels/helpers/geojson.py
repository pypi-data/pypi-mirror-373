import re
from typing import List, Tuple, Dict

from pyproj import Transformer


from gdaltools import ogr2ogr, GdalToolsError
from pydantic_geojson import (
    PointModel,
    LineStringModel,
    PolygonModel,
    MultiPolygonModel,
)

from agptools.helpers import STR, INT, FLOAT, DATE
from agptools.logs import logger

from ..crawler import iPlugin


# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
log = logger(__name__)

# -------------------------------------------------------------------
# GeoJSON Pydantic models
# -------------------------------------------------------------------
Geometry = PointModel | LineStringModel | PolygonModel | MultiPolygonModel


def POINT(x):
    "try to parse a point GeoJSON coordinate into a PointModel."
    if x is not None:
        return PointModel(coordinates=x)
    return x


def LINESTRING(x):
    "try to parse a linestring GeoJSON coordinate into a LineStringModel."
    if x is not None:
        return LineStringModel(coordinates=x)
    return x


def POLYGON(x):
    "try to parse a polygon GeoJSON coordinate into a PolygonModel."
    if x is not None:
        return PolygonModel(coordinates=x)
    return x


def MULTIPOLYGON(x):
    "try to parse a multipolygon GeoJSON coordinate into a MultiPolygonModel."
    if x is not None:
        return MultiPolygonModel(coordinates=x)
    return x


def SIMPLE_OR_MULTIPOLYGON(x):
    """Determine if x is a simple polygon or a multipolygon
    and map it accordingly."""
    if x is None:
        return None

    if isinstance(x[0], list) and len(x[0]) > 0:
        if all(isinstance(coord, (int, float)) for coord in x[0][0]):
            return POLYGON(x)
        elif all(isinstance(sub, list) for sub in x[0]):
            return MULTIPOLYGON(x)

    raise ValueError("The geometry is not a valid polygon or multipolygon.")


# ----------------------------------------------------------
# Geo-JSON Re-projection
# ----------------------------------------------------------


def reproject_file(
    input_path: str,
    output_path: str,
    source_crs: str | None = None,
    target_crs: str | None = None,
    encoding: str = "UTF-8",
) -> None:
    """
    Reprojects a file from source_crs to target_crs.
    """
    ogr = ogr2ogr()
    ogr.set_encoding(encoding)
    if source_crs:
        ogr.set_input(input_path, srs=source_crs)
    else:
        ogr.set_input(input_path)
    ogr.set_output(output_path, srs=target_crs)
    try:
        ogr.execute()
    except GdalToolsError as why:
        print(f"Reprojecting: Error: {why}")
        return False
    return True


def reproject_coordinates(
    coordinates: List[float],
    source_crs: str = "EPSG:25830",
    target_crs: str = "EPSG:4326",
) -> Tuple[float, float]:
    """
    Re-projects a set of coordinates from source_crs to target_crs.
    """
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

    if len(coordinates) == 3:
        x, y, _ = coordinates  # Ignore the z coordinate
    elif len(coordinates) == 2:
        x, y = coordinates
    else:
        raise ValueError("Coordinates must be 2D or 3D")

    try:
        x_2, y_2 = transformer.transform(x, y)
    except Exception as e:
        print(f"Error transforming coordinates: {coordinates}")
        raise e
    return x_2, y_2


class ReprojectCoordinatesPlugin(iPlugin):
    """
    Reprojects the x and y coordinates in each incoming file content.

    # TODO: agp: need to implement this plugin properlty??


    record
    {'codLinea': 44.0,
     'codLineaStr': '44',
     'codLineaStrSin': '44',
     'userCodLinea': 'N4',
     'nombreLinea': 'Paseo del Parque - Teatinos - Pto. de la Torre (Nocturno 4)',
     'observaciones': 'Nueva Parada en Teatinos (1472)',
     'cabeceraIda': 'Paseo del Parque',
     'cabeceraVuelta': 'Puerto de la Torre',
     'avisoSinHorarioEs': '',
     'avisoSinHorarioEn': '',
     'tagsAccesibilidad': 'n4,n 4,ene4,ene 4,nocturno4,nocturno '
                          '4,nocturna4,nocturna 4,night4,night 4',
     'paradas': [{'linea': '',
                  'parada': {'codParada': 163,
                             'nombreParada': 'Paseo del Parque -  Ayuntamiento',
                             'direccion': 'PSO PARQUE 4',
                     ---->   'latitud': 36.720093,
                     ---->   'longitud': -4.414305,
                             'lineas': ''},
                  'sentido': 1,
                  'orden': 1,
                  'espera': '',
                  'fechaInicioDemanda': '',
                  'fechaFinDemanda': '',
                  'franjas': []},

        ...
        }



    TODO: use an aprox location by some data when 'COORD_X', COORD_Y are missing
    TODO:
    TODO: example:
     'DOMICILIO_ESTAB': 'AVENIDA SAN SEBASTIAN Nº 4 Plta/Piso BAJO Pta/Letra 12',
     'CODIGO_POSTAL': '29010',
     'LOCALIDAD': None,
     'ID_MUNICIPIO': 4754,

    using selenium + google maps: --> 36.72332406405165, -4.436128087078546


    """

    async def handle(self, stream: List[Dict], context: Dict):
        try:
            target_crs = context.get("target_crs", "EPSG:4326")
        except KeyError:
            raise ValueError("Filtering field and/or value missing in context")

        _stream = []
        N = len(stream)
        for idx, item in enumerate(stream):
            input_crs = item.get("SRID", "25830")  # default crs for Open RTA
            coordinates = [
                item.get("COORD_X", None),
                item.get("COORD_Y", None),
            ]
            if all(coordinates):
                # Clean "," from coordinates, just in case data are strings with ',' decimal format
                coordinates = [float(str(_).replace(",", ".")) for _ in coordinates]

                reprojected_coordinates = reproject_coordinates(
                    coordinates=coordinates,
                    source_crs=input_crs,
                    target_crs=target_crs,
                )
                item["COORD_X"], item["COORD_Y"] = item["coordinates"] = list(
                    reprojected_coordinates
                )
                _stream.append(item)
            if not idx % 500:
                log.info("reprojecting: [%s/%s]: %i%%", idx, N, 100 * idx / N)

        stream[:] = _stream


# ----------------------------------------------------------
# Data Mapping and Cleaning
# ----------------------------------------------------------
def replace_na(value, na_value=-1):
    """Replace 'NA' values marked with a filler value to None"""
    return None if value == na_value else value


def STR_NA(value, na_value="No disponible"):
    """Replace 'NA' values and map to a string"""
    return STR(replace_na(value, na_value=na_value))


def INT_NA(value, na_value=-1):
    """Replace 'NA' values and map to an integer"""
    return INT(replace_na(value, na_value=na_value))


def FLOAT_NA(value, na_value=-1):
    """Replace 'NA' values and map to a float"""
    return FLOAT(replace_na(value, na_value=na_value))


def DATE_NA(value, na_value="19000101"):
    """Replace 'NA' values and map to a date"""
    return DATE(replace_na(value, na_value=na_value))


def clean_html(raw_html, regex=re.compile("<.*?>")):
    """Remove HTML tags from a string"""
    return re.sub(regex, "", raw_html)
