from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer
from uuid import UUID as PythonUUID, uuid4


class DataIdentifier:
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    uuid: Mapped[PythonUUID] = mapped_column(
        "uuid", PostgresUUID(as_uuid=True), default=uuid4, unique=True, nullable=False
    )
