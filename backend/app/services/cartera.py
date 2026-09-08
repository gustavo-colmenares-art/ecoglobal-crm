from datetime import date
from decimal import Decimal

from app.models.factura import Factura

ESTADOS_ACTIVOS = ("emitida", "enviada", "parcialmente_pagada", "vencida")


def saldo_factura(factura: Factura) -> Decimal:
    pagado = sum((p.monto for p in factura.pagos), Decimal("0"))
    return factura.total - pagado


def dias_vencida(factura: Factura) -> int:
    if not factura.fecha_vencimiento:
        return 0
    delta = date.today() - factura.fecha_vencimiento
    return max(delta.days, 0)


def actualizar_estado_por_pago(factura: Factura) -> None:
    saldo = saldo_factura(factura)
    if saldo <= 0:
        factura.estado = "pagada"
    elif factura.estado in ("emitida", "vencida") or saldo < factura.total:
        factura.estado = "parcialmente_pagada"
