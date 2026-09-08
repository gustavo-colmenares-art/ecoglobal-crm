from decimal import ROUND_HALF_UP, Decimal

from app.models.factura import Factura, FacturaItem

IVA_PCT = Decimal("19.00")


def calcular_subtotal_item(cantidad: Decimal, precio_unitario: Decimal, descuento_pct: Decimal) -> Decimal:
    bruto = cantidad * precio_unitario
    descuento = bruto * (descuento_pct / Decimal("100"))
    return (bruto - descuento).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def recalcular_factura(factura: Factura, items: list[FacturaItem]) -> None:
    subtotal = sum((item.subtotal or Decimal("0") for item in items), Decimal("0"))
    iva = (subtotal * IVA_PCT / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    factura.subtotal = subtotal
    factura.iva = iva
    factura.total = subtotal + iva - (factura.descuento or Decimal("0"))
