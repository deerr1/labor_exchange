from contextlib import AbstractAsyncContextManager
from typing import Callable, Generic, Sequence, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from interfaces import IRepositoryAsync

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], IRepositoryAsync):
    def __init__(
        self,
        model: type[ModelType],
        session: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ):
        self.model = model
        self.session = session

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        async with self.session() as session:
            db_obj = self.model(**obj_in.model_dump())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)

        return db_obj

    async def retrieve(self, include_relations: bool = False, **kwargs) -> ModelType | None:
        async with self.session() as session:
            query = select(self.model).filter_by(**kwargs).limit(1)
            if include_relations:
                query = query.options(selectinload("*"))
            res = await session.execute(query)
            db_obj = res.scalars().first()

        return db_obj

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, include_relations: bool = False
    ) -> Sequence[ModelType]:
        async with self.session() as session:
            query = select(self.model).limit(limit).offset(skip)
            if include_relations:
                query = query.options(selectinload("*"))
            res = await session.execute(query)
            db_obj = res.scalars().all()

        return db_obj

    async def update(self, id: int, obj_in: UpdateSchemaType) -> ModelType:
        async with self.session() as session:
            query = select(self.model).filter_by(id=id).limit(1)
            res = await session.execute(query)
            db_obj = res.scalars().first()

            if not db_obj:
                raise ValueError("Данные не найдены")

            update_data = obj_in.model_dump(exclude_unset=True)
            for k, v in update_data.items():
                setattr(db_obj, k, v)

            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)

        return db_obj

    async def delete(self, id: int):
        async with self.session() as session:
            query = select(self.model).filter_by(id=id).limit(1)
            res = await session.execute(query)
            db_obj = res.scalars().first()

            if db_obj:
                await session.delete(db_obj)
                await session.commit()
            else:
                raise ValueError("Данные не найдены")

        return db_obj
