from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Declaracion(Base):
    __tablename__ = "declaraciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # DEC-2024-00001
    manifiesto_id: Mapped[int] = mapped_column(ForeignKey("manifiestos.id"), nullable=False)
    planta_id: Mapped[int] = mapped_column(ForeignKey("plantas_certificadoras.id"), nullable=False)
    fecha_envio: Mapped[date | None] = mapped_column(Date)
    fecha_certificacion: Mapped[date | None] = mapped_column(Date)
    numero_certificado: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(30), default="pendiente")
    # estados: pendiente | enviada | certificada | rechazada
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["DeclaracionItem"]] = relationship(back_populates="declaracion")


class DeclaracionItem(Base):
    __tablename__ = "declaracion_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    declaracion_id: Mapped[int] = mapped_column(ForeignKey("declaraciones.id"), nullable=False)
    manifiesto_item_id: Mapped[int | None] = mapped_column(ForeignKey("manifiesto_items.id"))
    tipo_residuo_id: Mapped[int] = mapped_column(ForeignKey("tipos_residuo.id"), nullable=False)
    cantidad: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    unidad_medida: Mapped[str | None] = mapped_column(String(20))
    observaciones: Mapped[str | None] = mapped_column(Text)

    declaracion: Mapped["Declaracion"] = relationship(back_populates="items")
