import json
import logging
import shutil
import tempfile
from typing import List, Optional

from asyncpg import Record
from fastapi import UploadFile
from shapefile import Reader, Shape

from epona.auth.schemas import UserSchema
from epona.settings import conn

from .schemas import (
    GeometriaPayloadSchema,
    GeometriaResponseSchema,
    GeometryRequestPayload,
    SGLFeature
)


async def save_geometry(
    payload: GeometriaPayloadSchema, user: UserSchema
) -> Optional[str]:
    """
    Recebe a geometria de um local, podendo ser um ponto, linha ou polígono especifica,
    e salva (cria ou atualiza) no banco de dados
    """
    try:
        geometry = json.dumps(payload.coords)
        query = (
            "UPDATE geometries "
            "SET representation = $1, zoom = $2,"
            f"  geom = ST_SetSRID(ST_GeomFromGeoJSON('{geometry}'), 4326) "
            "WHERE entity_name=$3 AND id_entity=$4"
            f"  AND geom_type=$5 AND representation=$6"
        )
        result = await conn.execute(
            query,
            [
                payload.representacao if payload.representacao else None,
                payload.zoom if payload.zoom else None,
                payload.entidade,
                payload.id_entidade,
                payload.tipo_geom,
                payload.representacao,
            ],
        )

        if result == "UPDATE 0":
            query = (
                "INSERT INTO geometries "
                "  (client_id, id_entity, entity_name, geom_type, representation, zoom, geom) "
                f"VALUES ($1, $2, $3, $4, $5, $6, "
                f"  ST_SetSRID(ST_GeomFromGeoJSON('{geometry}'), 4326))"
            )
            result = await conn.execute(
                query,
                [
                    user.client_id,
                    payload.id_entidade,
                    payload.entidade,
                    payload.tipo_geom,
                    payload.representacao if payload.representacao else None,
                    payload.zoom if payload.zoom else None,
                ],
            )

        return result
    except Exception as err:
        logging.error(err)


async def get_geometries(
    payload: GeometryRequestPayload, user: UserSchema
) -> Optional[List[GeometriaResponseSchema]]:
    """
    Recebe uma entidade e retorna todas as geometrias relacionadas com essa entidade
    """
    try:
        geom_query = (
            "SELECT "
            "  suuid, id_entity, entity_name, representation, geom_type, zoom, "
            " ST_AsGeoJSON(geom)"
            "FROM geometries WHERE entity_name = $1 AND id_entity = $2"
        )
        result = await conn.fetch_rows(
            geom_query, [payload.entity_type, payload.id_entity]
        )
        geometries = []
        for geom in result:
            geometry = GeometriaResponseSchema(**{"id": geom["suuid"], **dict(geom)})
            geometry.coords = json.loads(geom["st_asgeojson"])
            geometries.append(geometry)
        return geometries
    except Exception as err:
        logging.error(err)


async def delete_geometry(
    payload: GeometriaPayloadSchema, user: UserSchema
) -> Optional[str]:
    """
    Deleta a geomtria de uma entidade especifia se a geometria estiver proxima
    (aprox 100m ) de um ponto fornecido
    """
    try:
        query = (
            "DELETE FROM geometries "
            "WHERE client_id=$1 AND entity_name=$2 AND id_entity=$3 AND geom_type=$4"
            f"  AND representation=$5 AND ST_Intersects(geom, ST_Buffer(ST_SetSRID("
            f"    ST_GeomFromGeoJSON('{json.dumps(payload.coords)}'), 4326), 0.001))"
        )
        return await conn.execute(
            query,
            [
                user.client_id,
                payload.entidade,
                payload.id_entidade,
                payload.tipo_geom,
                payload.representacao,
            ],
        )
    except Exception as err:
        logging.error(err)


async def get_layer(
    entidade: str, user: UserSchema
) -> Optional[List[GeometriaResponseSchema]]:
    """
    Retorna todas as geometria de um tipo de entidade
    """
    try:
        geom_query = (
            "SELECT"
            "  suuid, id_entity, entity_name, representation, geom_type, zoom, "
            " ST_AsGeoJSON(geom)"
            "FROM geometries "
            "WHERE client_id = $1 AND entity_name = $2"
        )
        result = await conn.fetch_rows(geom_query, [user.client_id, entidade])
        return format_response(result)
    except Exception as err:
        logging.error(err)


def format_response(result: Record) -> List[GeometriaResponseSchema]:
    """
    Transforma o resultado da query do banco de dados no Schema de geometrias
    """
    geometrias = []
    for geom in result:
        geometria = GeometriaResponseSchema(**dict(geom))
        geometria.coords = json.loads(dict(geom)["st_asgeojson"])
        geometrias.append(geometria)
    return geometrias


async def load_geometry(
    upload_file: UploadFile, user: UserSchema
) -> Optional[SGLFeature]:
    """
    Le um arquivo shapefile e retorna em GeoJSON
    """
    tempdir = None
    try:
        tempdir = tempfile.TemporaryDirectory()
        filename = f"{tempdir.name}/{user.username}_tempfile.zip"
        with open(filename, "wb") as file:
            file.write(upload_file.file.read())
        shp = Reader(filename)
        if len(shp) != 1:
            raise ValueError("Shapefile contém mais de uma geometria")
        if shp.shapeTypeName not in ["POLYGON", "POLYLINE"]:
            raise ValueError("Geometria deve ser simples e do tipo linha ou poligono")
        geojson, geom_type = shape_to_geojson(shp.shape(0))
        geom = SGLFeature(**{
            "coords": geojson, "geomType": geom_type
        })
        return geom
    except ValueError as err:
        raise err
    except Exception as ex:
        raise ValueError(f"Erro desconhecido: {str(ex)}")
    finally:
        if tempdir:
            shutil.rmtree(tempdir.name)


def shape_to_geojson(shape: Shape) -> (str, str):
    """
    Converte shapefile para GeoJSON
    """
    try:
        geom_type = "Polygon" if shape.shapeTypeName == "POLYGON" else "LineString"
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": geom_type,
                "coordinates": [],
            },
            "properties": {},
        }
        coordinates = []
        if geom_type == "Polygon":
            coordinates = [[[point[0], point[1]] for point in reversed(shape.points)]]
        elif geom_type == "LineString":
            coordinates = [[point[0], point[1]] for point in reversed(shape.points)]
        geojson["geometry"]["coordinates"] = coordinates

        return geojson, geom_type.upper()
    except Exception as err:
        logging.error(err)
