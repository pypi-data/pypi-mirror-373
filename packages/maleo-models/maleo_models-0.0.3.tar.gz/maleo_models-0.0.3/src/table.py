from sqlalchemy.orm import declared_attr
from maleo.utils.formatters.case import to_snake
from .mixins.identifier import DataIdentifier
from .mixins.status import DataStatus
from .mixins.timestamp import DataTimestamp


class BaseTable:
    __abstract__ = True

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)  # type: ignore


class DataTable(DataStatus, DataTimestamp, DataIdentifier):
    pass
