from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from lib.errors.db_errors import DBError


class EntityService[TModel: SQLModel, TId]:
    def __init__(self, entity: str, model_class: type[TModel]) -> None:
        self.entity = entity
        self.model_class = model_class

    async def get(
        self,
        id: TId,
        db: AsyncSession,
    ) -> TModel | None:
        return await db.get(self.model_class, id)

    async def create(
        self,
        dto: TModel,
        db: AsyncSession,
    ) -> TModel | DBError:
        try:
            db.add(dto)
            await db.commit()
            await db.refresh(dto)

            return dto
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):  # type: ignore[valid-type]
                return DBError(
                    f"Failed to create {type(dto).__name__} with error: {e.orig.__cause__}"  # type: ignore[valid-type]
                )

            return DBError(
                f"Failed to create {type(dto).__name__} with error: {e.orig}"
            )

    async def delete(
        self,
        id: TId,
        db: AsyncSession,
    ) -> TModel | None:
        dto = await db.get(self.model_class, id)

        if not dto:
            return None

        await db.delete(dto)
        await db.commit()
        return dto

    async def update(
        self,
        dto: TModel,
        db: AsyncSession,
    ) -> TModel | DBError | None:
        try:
            entity = await self.get(dto.id, db)  # type: ignore[valid-type]

            if not entity:
                return None

            entity.sqlmodel_update(dto.model_dump(exclude_unset=True))

            db.add(entity)
            await db.commit()
            await db.refresh(entity)

            return entity
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):  # type: ignore[valid-type]
                return DBError(
                    f"Failed to update {type(dto).__name__} with error: {e.orig.__cause__}"  # type: ignore[valid-type]
                )

            return DBError(
                f"Failed to update {type(dto).__name__} with error: {e.orig}"
            )
