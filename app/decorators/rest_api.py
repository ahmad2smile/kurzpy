from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.core.db_errors import DBError
from app.core.session import get_session
from app.core.type_utils import replace_param_type
from app.decorators.entity_service import EntityService


class RestController[TModel: SQLModel, TId]:
    def __init__(
        self,
        model_class: type[TModel],
        route_name: str,
        class_name: str,
        id_type: type[Any],
        entity_service: EntityService[TModel, TId],
    ) -> None:
        self.entity_service = entity_service
        self.class_name = class_name

        router = APIRouter(prefix=f"/{route_name}", tags=[class_name])
        router.add_api_route(
            "/{id}",
            replace_param_type(self.get, id=id_type),
            methods=["GET"],
            response_model=model_class,
        )
        router.add_api_route(
            "/",
            replace_param_type(self.create, dto=model_class),
            methods=["POST"],
            response_model=model_class,
        )
        router.add_api_route(
            "/{id}",
            replace_param_type(self.delete, id=id_type),
            methods=["DELETE"],
            response_model=model_class,
        )
        router.add_api_route(
            "/",
            replace_param_type(self.update, dto=model_class),
            methods=["PUT"],
            response_model=model_class,
        )

        self.router = router

    async def get(
        self,
        id: TId,
        db: AsyncSession = Depends(get_session),
    ):
        entity = await self.entity_service.get(id, db)

        if not entity:
            raise HTTPException(404, f"{self.class_name} not found with id:{id}")

        return entity

    async def create(
        self,
        dto: TModel,
        db: AsyncSession = Depends(get_session),
    ) -> TModel:
        entity = await self.entity_service.create(dto, db)

        if isinstance(entity, DBError):
            raise HTTPException(status_code=409, detail=str(entity))

        return entity

    async def delete(
        self,
        id: TId,
        db: AsyncSession = Depends(get_session),
    ) -> TModel:
        entity = await self.entity_service.delete(id, db)

        if not entity:
            raise HTTPException(404, f"Failed to delete missing {self.class_name}")

        return entity

    async def update(
        self,
        dto: TModel,
        db: AsyncSession = Depends(get_session),
    ) -> TModel | None:
        entity = await self.entity_service.update(dto, db)

        if not entity:
            raise HTTPException(404, f"Failed to update missing {self.class_name}")

        if isinstance(entity, DBError):
            raise HTTPException(status_code=409, detail=str(entity))

        return entity
