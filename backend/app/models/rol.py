from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(unique=True, nullable=False)
    # valores: superadmin | comercial | operaciones | contabilidad | cartera | visualizador
    descripcion: Mapped[str | None] = mapped_column(Text)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")
