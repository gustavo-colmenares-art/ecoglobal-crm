"""Elimina clientes de ejemplo/prueba y toda su cadena de registros dependientes.
Uso: docker compose exec backend python scripts/eliminar_clientes_demo.py
"""

import sys

sys.path.insert(0, "/app")

from app.core.database import SessionLocal  # noqa: E402
from app.models.cartera import Pago, SeguimientoCartera  # noqa: E402
from app.models.cliente import Cliente  # noqa: E402
from app.models.declaracion import Declaracion, DeclaracionItem  # noqa: E402
from app.models.factura import Factura, FacturaItem  # noqa: E402
from app.models.manifiesto import Manifiesto, ManifiestoHistorial, ManifiestoItem  # noqa: E402
from app.models.servicio import Servicio, ServicioHistorial  # noqa: E402

NITS_A_ELIMINAR = [
    "900111222-1",  # Industrias Andina S.A.S. (seed)
    "900222333-2",  # Textiles del Norte Ltda. (seed)
    "900333444-3",  # Alimentos del Valle S.A. (seed)
    "900444555-4",  # Metalúrgica Central S.A.S. (seed)
    "900555666-5",  # Química Industrial Ltda. (seed)
    "999888777-1",  # Cliente de Prueba Formulario (prueba de endpoint)
]


def eliminar_cliente(db, cliente: Cliente) -> None:
    servicios = db.query(Servicio).filter_by(cliente_id=cliente.id).all()
    for servicio in servicios:
        for manifiesto in db.query(Manifiesto).filter_by(servicio_id=servicio.id).all():
            for declaracion in db.query(Declaracion).filter_by(manifiesto_id=manifiesto.id).all():
                db.query(DeclaracionItem).filter_by(declaracion_id=declaracion.id).delete()
                db.delete(declaracion)
                db.flush()
            db.query(ManifiestoItem).filter_by(manifiesto_id=manifiesto.id).delete()
            db.query(ManifiestoHistorial).filter_by(manifiesto_id=manifiesto.id).delete()
            db.delete(manifiesto)
            db.flush()

        for factura in db.query(Factura).filter_by(servicio_id=servicio.id).all():
            db.query(Pago).filter_by(factura_id=factura.id).delete()
            db.query(SeguimientoCartera).filter_by(factura_id=factura.id).delete()
            db.query(FacturaItem).filter_by(factura_id=factura.id).delete()
            db.delete(factura)
            db.flush()

        db.query(ServicioHistorial).filter_by(servicio_id=servicio.id).delete()
        db.delete(servicio)
        db.flush()

    db.delete(cliente)
    db.flush()


def main() -> None:
    db = SessionLocal()
    try:
        for nit in NITS_A_ELIMINAR:
            cliente = db.query(Cliente).filter_by(nit=nit).first()
            if not cliente:
                print(f"No encontrado (ya eliminado o no existia): NIT {nit}")
                continue
            print(f"Eliminando: {cliente.razon_social} (NIT {nit})")
            eliminar_cliente(db, cliente)
        db.commit()
        print("Limpieza completada.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
