from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.declaracion import Declaracion
from app.models.factura import Factura
from app.models.lead import Lead
from app.models.manifiesto import Manifiesto
from app.models.servicio import Servicio

UMBRAL_MANIFIESTO_DIAS = 3
UMBRAL_DECLARACION_DIAS = 7
UMBRAL_FACTURA_POR_VENCER_DIAS = 5
UMBRAL_COTIZACION_SEGUIMIENTO_DIAS = 8
UMBRAL_LEAD_SIN_ATENDER_DIAS = 2


def manifiestos_demorados(db: Session) -> list[Manifiesto]:
    limite = date.today() - timedelta(days=UMBRAL_MANIFIESTO_DIAS)
    return list(
        db.scalars(
            select(Manifiesto).where(
                Manifiesto.estado == "en_campo",
                Manifiesto.fecha_recoleccion.is_not(None),
                Manifiesto.fecha_recoleccion <= limite,
            )
        ).all()
    )


def declaraciones_sin_certificar(db: Session) -> list[Declaracion]:
    limite = date.today() - timedelta(days=UMBRAL_DECLARACION_DIAS)
    return list(
        db.scalars(
            select(Declaracion).where(
                Declaracion.estado == "enviada",
                Declaracion.fecha_envio.is_not(None),
                Declaracion.fecha_envio <= limite,
            )
        ).all()
    )


def facturas_por_vencer(db: Session) -> list[Factura]:
    limite = date.today() + timedelta(days=UMBRAL_FACTURA_POR_VENCER_DIAS)
    return list(
        db.scalars(
            select(Factura).where(
                Factura.estado.in_(["emitida", "enviada", "parcialmente_pagada"]),
                Factura.fecha_vencimiento.is_not(None),
                Factura.fecha_vencimiento <= limite,
                Factura.fecha_vencimiento >= date.today(),
            )
        ).all()
    )


def facturas_vencidas(db: Session) -> list[Factura]:
    return list(
        db.scalars(
            select(Factura).where(
                Factura.estado.in_(["emitida", "enviada", "parcialmente_pagada", "vencida"]),
                Factura.fecha_vencimiento.is_not(None),
                Factura.fecha_vencimiento < date.today(),
            )
        ).all()
    )


def servicios_cotizados_sin_seguimiento(db: Session) -> list[Servicio]:
    """Servicios que llevan >= 8 días en 'cotizado' sin que el cliente haya
    confirmado ni el servicio se haya cancelado — recordatorio de seguimiento
    comercial."""
    limite = date.today() - timedelta(days=UMBRAL_COTIZACION_SEGUIMIENTO_DIAS)
    return list(
        db.scalars(
            select(Servicio).where(
                Servicio.estado == "cotizado",
                Servicio.actualizado_en <= limite,
            )
        ).all()
    )


def leads_sin_atender(db: Session) -> list[Lead]:
    """Leads de WhatsApp que llegaron y nadie los ha clasificado todavía."""
    limite = date.today() - timedelta(days=UMBRAL_LEAD_SIN_ATENDER_DIAS)
    return list(
        db.scalars(
            select(Lead).where(
                Lead.estado == "nuevo",
                Lead.creado_en <= limite,
            )
        ).all()
    )
