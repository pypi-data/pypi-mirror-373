from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP
from maleo.types.base.datetime import OptionalDatetime


class CreateTimestamp:
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UpdateTimestamp:
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class LifecyleTimestamp(UpdateTimestamp, CreateTimestamp):
    pass


class DeleteTimestamp:
    deleted_at: Mapped[OptionalDatetime] = mapped_column(
        "deleted_at", TIMESTAMP(timezone=True)
    )


class RestoreTimestamp:
    restored_at: Mapped[OptionalDatetime] = mapped_column(
        "restored_at", TIMESTAMP(timezone=True)
    )


class DeactivateTimestamp:
    deactivated_at: Mapped[OptionalDatetime] = mapped_column(
        "deactivated_at", TIMESTAMP(timezone=True)
    )


class ActivateTimestamp:
    activated_at: Mapped[datetime] = mapped_column(
        "activated_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class StatusTimestamp(
    ActivateTimestamp, DeactivateTimestamp, RestoreTimestamp, DeleteTimestamp
):
    pass


class DataTimestamp(StatusTimestamp, LifecyleTimestamp):
    pass
