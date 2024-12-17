from dataclasses import fields
from typing import TYPE_CHECKING

from repositories.base import BaseRepository

if TYPE_CHECKING:
    from storage.sqlalchemy.tables import User  # noqa
    from web.schemas import UserCreateSchema, UserUpdateSchema  # noqa


class UserRepository(BaseRepository["User", "UserCreateSchema", "UserUpdateSchema"]):
    async def create(
        self, user_create_dto: "UserCreateSchema", hashed_password: str = None
    ) -> "User":
        fields_set = set([field.name for field in fields(self.model)])
        async with self.session() as session:
            user = self.model(
                **user_create_dto.model_dump(include=fields_set),
                hashed_password=hashed_password,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user
