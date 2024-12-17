from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base

if TYPE_CHECKING:
    from storage.sqlalchemy.tables import Response, User


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии", init=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )

    # добавьте ваши колонки сюда

    user: Mapped["User"] = relationship(default=None, repr=False)  # noqa
    responses: Mapped[list["Response"]] = relationship(default=list, lazy="noload")  # noqa
