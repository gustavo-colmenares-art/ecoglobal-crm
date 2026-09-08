from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    canal: Mapped[str] = mapped_column(String(20), default="whatsapp")
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nombre_contacto: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str] = mapped_column(String(30), default="nuevo")
    # estados: nuevo | en_conversacion | cotizacion | servicio_directo | convertido | no_atendido
    tipo_interes: Mapped[str | None] = mapped_column(String(30))  # cotizacion | servicio_directo
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"))
    servicio_id: Mapped[int | None] = mapped_column(ForeignKey("servicios.id"))
    asignado_a: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    notas: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    mensajes: Mapped[list["LeadMensaje"]] = relationship(
        back_populates="lead", order_by="LeadMensaje.enviado_en"
    )


class LeadMensaje(Base):
    __tablename__ = "lead_mensajes"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    direccion: Mapped[str] = mapped_column(String(10))  # entrante | saliente
    texto: Mapped[str] = mapped_column(Text)
    enviado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lead: Mapped["Lead"] = relationship(back_populates="mensajes")
