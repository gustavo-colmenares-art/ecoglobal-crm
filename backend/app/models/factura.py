from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # FAC-2024-00001
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"), nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    fecha_emision: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    descuento: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    estado: Mapped[str] = mapped_column(String(30), default="borrador")
    # estados: borrador | emitida | enviada | parcialmente_pagada | pagada | vencida | anulada
    observaciones: Mapped[str | None] = mapped_column(Text)
    condiciones_pago: Mapped[str | None] = mapped_column(Text)  # ej. "30 días"
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["FacturaItem"]] = relationship(back_populates="factura")
    pagos: Mapped[list["Pago"]] = relationship(back_populates="factura")
    gestiones: Mapped[list["SeguimientoCartera"]] = relationship(back_populates="factura")


class FacturaItem(Base):
    __tablename__ = "factura_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id"), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=1)
    precio_unitario: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    descuento_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    tipo_residuo_id: Mapped[int | None] = mapped_column(ForeignKey("tipos_residuo.id"))

    factura: Mapped["Factura"] = relationship(back_populates="items")
