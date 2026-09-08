from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Manifiesto(Base):
    __tablename__ = "manifiestos"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # MAN-2024-00001
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"), nullable=False)
    operario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_generacion: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    fecha_recoleccion: Mapped[date | None] = mapped_column(Date)
    fecha_retorno: Mapped[date | None] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(30), default="generado")
    # estados: generado | en_campo | recibido | declarado | cerrado
    firma_cliente: Mapped[bool] = mapped_column(Boolean, default=False)
    nombre_receptor: Mapped[str | None] = mapped_column(String(120))
    cargo_receptor: Mapped[str | None] = mapped_column(String(100))
    observaciones_campo: Mapped[str | None] = mapped_column(Text)
    observaciones_retorno: Mapped[str | None] = mapped_column(Text)
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["ManifiestoItem"]] = relationship(back_populates="manifiesto")
    historial: Mapped[list["ManifiestoHistorial"]] = relationship(
        back_populates="manifiesto", order_by="ManifiestoHistorial.cambiado_en"
    )


class ManifiestoItem(Base):
    __tablename__ = "manifiesto_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    manifiesto_id: Mapped[int] = mapped_column(ForeignKey("manifiestos.id"), nullable=False)
    tipo_residuo_id: Mapped[int] = mapped_column(ForeignKey("tipos_residuo.id"), nullable=False)
    cantidad_declarada: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    cantidad_real: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    unidad_medida: Mapped[str | None] = mapped_column(String(20))
    descripcion_adicional: Mapped[str | None] = mapped_column(Text)
    numero_contenedor: Mapped[str | None] = mapped_column(String(50))
    observaciones: Mapped[str | None] = mapped_column(Text)

    manifiesto: Mapped["Manifiesto"] = relationship(back_populates="items")


class ManifiestoHistorial(Base):
    __tablename__ = "manifiesto_historial"

    id: Mapped[int] = mapped_column(primary_key=True)
    manifiesto_id: Mapped[int] = mapped_column(ForeignKey("manifiestos.id"), nullable=False)
    estado_antes: Mapped[str | None] = mapped_column(String(30))
    estado_nuevo: Mapped[str | None] = mapped_column(String(30))
    cambiado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    nota: Mapped[str | None] = mapped_column(Text)
    cambiado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    manifiesto: Mapped["Manifiesto"] = relationship(back_populates="historial")
