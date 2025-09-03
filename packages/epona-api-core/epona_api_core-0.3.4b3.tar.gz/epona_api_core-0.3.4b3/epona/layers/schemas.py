from typing import Optional

from pydantic import BaseModel


class GeometryRequestPayload(BaseModel):
    id_entity: str
    entity_type: str


class GeometriaPayloadSchema(BaseModel):
    id_entidade: str
    entidade: str
    coords: dict
    representacao: Optional[str] = None
    tipo_geom: str
    zoom: Optional[int] = None


class GeometriaResponseSchema(GeometriaPayloadSchema):
    id: str
    suuid: str
    coords: Optional[dict] = None


class SGLFeature(BaseModel):
    id: Optional[str] = ""
    suuid: Optional[str] = ""
    coords: dict
    entity: Optional[str] = ""
    entityId: Optional[str] = ""
    geomType: str
    representation: Optional[str] = ""
    zoom: Optional[str] = ""
