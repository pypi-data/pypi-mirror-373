from typing import Optional

from pydantic import BaseModel


class GetGeometryPayload(BaseModel):
    id_entity: str
    entity_type: str


class GeometryPayload(BaseModel):
    id_entity: str
    entity_type: str
    cords: dict
    representation: Optional[str] = None
    geom_type: str
    zoom: Optional[int] = None


class GeometryResponse(GeometryPayload):
    id: str
    suuid: str
    cords: Optional[dict] = None


class SGLFeature(BaseModel):
    id: Optional[str] = ""
    suuid: Optional[str] = ""
    cords: dict
    entity: Optional[str] = ""
    entityId: Optional[str] = ""
    geomType: str
    representation: Optional[str] = ""
    zoom: Optional[str] = ""
