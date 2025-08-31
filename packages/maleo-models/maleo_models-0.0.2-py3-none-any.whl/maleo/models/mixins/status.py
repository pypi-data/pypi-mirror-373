from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum
from maleo.enums.status import DataStatus as DataStatusEnum


class DataStatus:
    status: Mapped[DataStatusEnum] = mapped_column(
        "status",
        Enum(DataStatusEnum, name="statustype", create_constraints=True),
        default=DataStatusEnum.ACTIVE,
        nullable=False,
    )
