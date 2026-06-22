import inspect

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_session


def rest_api(cls):
    entity = cls.__name__
    cls.__tablename__ = f"{entity}s"
    route_name = f"{entity.lower()}s"

    if not inspect.isclass(cls):
        raise TypeError(
            f"@{rest_api.__name__} can only applied to a class, got {entity}"
        )

    id_type = cls.model_fields["id"].annotation
    router = APIRouter(prefix=f"/{route_name}", tags=[entity])

    class Wrapper:
        def __init__(self) -> None:
            router.add_api_route("/{id}", self.get, methods=["GET"], response_model=cls)
            router.add_api_route("/", self.create, methods=["POST"], response_model=cls)
            router.add_api_route(
                "/{id}", self.delete, methods=["DELETE"], response_model=cls
            )
            router.add_api_route("/", self.update, methods=["PUT"], response_model=cls)

        async def get(
            self,
            id: id_type,  # type: ignore[valid-type]
            db: AsyncSession = Depends(get_session),
        ):
            dto = await db.get(cls, id)

            if not dto:
                raise HTTPException(404, f"{entity} not found with id:{id}")

            return dto

        async def create(
            self,
            dto: cls,  # type: ignore[valid-type]
            db: AsyncSession = Depends(get_session),
        ) -> cls:  # type: ignore[valid-type]
            db.add(dto)
            await db.commit()
            await db.refresh(dto)

            return dto

        async def delete(
            self,
            id: id_type,  # type: ignore[valid-type]
            db: AsyncSession = Depends(get_session),
        ) -> cls:  # type: ignore[valid-type]
            dto = await db.get(cls, id)

            if not dto:
                raise HTTPException(404, f"{entity} not found with id:{id}")
            await db.delete(dto)
            await db.commit()
            return dto

        async def update(
            self,
            dto: cls,  # type: ignore[valid-type]
            db: AsyncSession = Depends(get_session),
        ) -> cls:  # type: ignore[valid-type]
            entity = await self.get(dto.id, db)

            entity.sqlmodel_update(dto.model_dump(exclude_unset=True))

            db.add(entity)
            await db.commit()
            await db.refresh(entity)

            return entity

    _ = Wrapper()

    cls.router = router

    return cls
