from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id"), nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    medio_pago: Mapped[str | None] = mapped_column(String(50))  # transferencia | cheque | efectivo | otro
    referencia: Mapped[str | None] = mapped_column(String(100))
    banco: Mapped[str | None] = mapped_column(String(100))
    observaciones: Mapped[str | None] = mapped_column(Text)
    registrado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    registrado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    factura: Mapped["Factura"] = relationship(back_populates="pagos")


class SeguimientoCartera(Base):
    __tablename__ = "seguimiento_cartera"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id"), nullable=False)
    tipo_gestion: Mapped[str | None] = mapped_column(String(50))  # llamada | email | visita | acuerdo_pago
    fecha_gestion: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    resultado: Mapped[str | None] = mapped_column(Text)
    proxima_accion: Mapped[str | None] = mapped_column(Text)
    fecha_proxima: Mapped[date | None] = mapped_column(Date)
    gestionado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    factura: Mapped["Factura"] = relationship(back_populates="gestiones")
