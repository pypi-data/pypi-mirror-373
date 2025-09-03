import logging
from typing import List, Optional

from fastapi import (APIRouter, File, HTTPException, Security, UploadFile,
                     status)

from epona.auth import schemas as auth
from epona.auth.services import get_current_active_user

from . import schemas, services

router = APIRouter()


@router.post("/save-geometry", response_model=str, status_code=status.HTTP_201_CREATED)
async def save_geometry(
    payload: schemas.GeometryPayload,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["layers:create"]),
) -> str:
    try:
        return await services.save_geometry(payload, user)
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            detail="Geometria não foi salva",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.post(
    "/get-geometries",
    response_model=Optional[List[schemas.GeometryResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_geometries(
    payload: schemas.GetGeometryPayload,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["layers:read"]),
) -> Optional[List[schemas.GeometryResponse]]:
    try:
        return await services.get_geometries(payload, user)
    except (ValueError, Exception) as err:
        logging.error(err)
        raise HTTPException(
            detail="Geometria não encontrada", status_code=status.HTTP_404_NOT_FOUND
        )


@router.post("/delete-geometry", response_model=str, status_code=status.HTTP_200_OK)
async def delete_geometry(
    payload: schemas.GeometryPayload,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["layers:delete"]),
) -> Optional[str]:
    try:
        return await services.delete_geometry(payload, user)
    except Exception as err:
        logging.error(err)


@router.get(
    "/get-layer",
    response_model=Optional[List[schemas.GeometryResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_layer(
    layer: str,
    user: auth.UserSchema = Security(get_current_active_user, scopes=["layers:read"]),
) -> Optional[List[schemas.GeometryResponse]]:
    try:
        return await services.get_layer(layer, user)
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            detail=f"Falha ao recuperar layer {layer}",
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.post(
    "/load-geometry",
    response_model=Optional[schemas.SGLFeature],
    status_code=status.HTTP_200_OK,
)
async def load_geometry(
    upload: UploadFile = File(...),
    user: auth.UserSchema = Security(get_current_active_user, scopes=["layers:create"]),
) -> Optional[schemas.SGLFeature]:
    try:
        return await services.load_geometry(upload, user)
    except Exception as err:
        logging.error(err)
        raise HTTPException(
            detail=f"Falha ao carregar arquivo. {str(err)}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
