from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Servicio(Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # SRV-2024-00001
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    fecha_solicitud: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    fecha_programada: Mapped[date | None] = mapped_column(Date)
    descripcion: Mapped[str | None] = mapped_column(Text)
    direccion_servicio: Mapped[str | None] = mapped_column(Text)
    ciudad_servicio: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(30), default="cotizado")
    # estados: cotizado | confirmado | programado | en_ruta | atendido
    #          manifiesto_pendiente | manifiesto_recibido | completado | cancelado
    prioridad: Mapped[str] = mapped_column(String(20), default="normal")  # baja | normal | alta | urgente
    observaciones: Mapped[str | None] = mapped_column(Text)
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    historial: Mapped[list["ServicioHistorial"]] = relationship(
        back_populates="servicio", order_by="ServicioHistorial.cambiado_en"
    )


class ServicioHistorial(Base):
    __tablename__ = "servicio_historial"

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios.id"), nullable=False)
    estado_antes: Mapped[str | None] = mapped_column(String(30))
    estado_nuevo: Mapped[str | None] = mapped_column(String(30))
    cambiado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    nota: Mapped[str | None] = mapped_column(Text)
    cambiado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    servicio: Mapped["Servicio"] = relationship(back_populates="historial")
