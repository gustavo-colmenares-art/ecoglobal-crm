"""Importa clientes+servicios pendientes desde el formulario 'orden de compra'.
Uso: docker compose exec backend python scripts/import_pendientes.py archivo.json
"""

import json
import sys
from datetime import date, datetime

sys.path.insert(0, "/app")

from app.core.database import SessionLocal  # noqa: E402
from app.models.cliente import Cliente  # noqa: E402
from app.models.servicio import Servicio  # noqa: E402
from app.services.numbering import generar_numero  # noqa: E402


def importar(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        registros = json.load(f)

    db = SessionLocal()
    try:
        for r in registros:
            cliente = db.query(Cliente).filter_by(nit=r["nit"]).first()
            if not cliente:
                cliente = Cliente(
                    razon_social=r["razon_social"],
                    nit=r["nit"],
                    direccion=r.get("direccion"),
                    telefono=r.get("telefono"),
                    email=r.get("email"),
                    contacto_nombre=r.get("contacto_nombre"),
                )
                db.add(cliente)
                db.flush()
                print(f"Cliente creado: {cliente.razon_social} (id={cliente.id})")
            else:
                print(f"Cliente ya existia: {cliente.razon_social} (id={cliente.id})")

            fecha_programada = None
            if r.get("fecha_programada"):
                fecha_programada = datetime.strptime(r["fecha_programada"], "%Y-%m-%d").date()

            existe_servicio = (
                db.query(Servicio)
                .filter_by(cliente_id=cliente.id, descripcion=r.get("descripcion"))
                .first()
            )
            if existe_servicio:
                print(f"  Servicio ya existia: {existe_servicio.numero}")
                continue

            servicio = Servicio(
                numero=generar_numero(db, Servicio, "SRV"),
                cliente_id=cliente.id,
                fecha_solicitud=date.today(),
                fecha_programada=fecha_programada,
                descripcion=r.get("descripcion"),
                direccion_servicio=r.get("direccion"),
                estado="cotizado",
            )
            db.add(servicio)
            db.flush()
            print(f"  Servicio creado: {servicio.numero}")

        db.commit()
        print("Importacion completada.")
    finally:
        db.close()


if __name__ == "__main__":
    importar(sys.argv[1])
