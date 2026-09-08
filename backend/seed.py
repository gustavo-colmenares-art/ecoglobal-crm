"""Datos semilla para desarrollo. Uso: python seed.py (dentro del contenedor backend)."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.cliente import Cliente
from app.models.planta_certificadora import PlantaCertificadora
from app.models.rol import Rol
from app.models.servicio import Servicio
from app.models.tipo_residuo import TipoResiduo
from app.models.usuario import Usuario
from app.services.numbering import generar_numero

ROLES = ["superadmin", "comercial", "operaciones", "contabilidad", "cartera", "visualizador"]

USUARIOS = [
    ("Administrador", "admin@ecoglobal.com", "admin123", "superadmin"),
    ("Comercial Demo", "comercial@ecoglobal.com", "comercial123", "comercial"),
    ("Operaciones Demo", "operaciones@ecoglobal.com", "operaciones123", "operaciones"),
    ("Contabilidad Demo", "contabilidad@ecoglobal.com", "contabilidad123", "contabilidad"),
    ("Cartera Demo", "cartera@ecoglobal.com", "cartera123", "cartera"),
    ("Visualizador Demo", "visualizador@ecoglobal.com", "visualizador123", "visualizador"),
]

CLIENTES = [
    ("Industrias Andina S.A.S.", "900111222-1", "Bogotá"),
    ("Textiles del Norte Ltda.", "900222333-2", "Medellín"),
    ("Alimentos del Valle S.A.", "900333444-3", "Cali"),
    ("Metalúrgica Central S.A.S.", "900444555-4", "Barranquilla"),
    ("Química Industrial Ltda.", "900555666-5", "Cartagena"),
]

TIPOS_RESIDUO = [
    ("ACE-001", "Aceites usados", "litros", True),
    ("SOL-001", "Solventes", "litros", True),
    ("BAT-001", "Baterías", "unidad", True),
    ("MET-001", "Metales", "kg", False),
    ("PLA-001", "Plásticos", "kg", False),
]

PLANTAS = ["Veolia", "Tracol", "Ecoaxaca"]


def get_or_create(db: Session, model, defaults: dict | None = None, **filtros):
    instancia = db.query(model).filter_by(**filtros).first()
    if instancia:
        return instancia
    instancia = model(**filtros, **(defaults or {}))
    db.add(instancia)
    db.flush()
    return instancia


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        roles = {nombre: get_or_create(db, Rol, nombre=nombre) for nombre in ROLES}

        usuarios = {}
        for nombre, email, password, rol in USUARIOS:
            usuarios[rol] = get_or_create(
                db,
                Usuario,
                email=email,
                defaults={
                    "nombre": nombre,
                    "password_hash": hash_password(password),
                    "rol_id": roles[rol].id,
                },
            )

        clientes = [
            get_or_create(
                db,
                Cliente,
                nit=nit,
                defaults={"razon_social": nombre, "ciudad": ciudad, "creado_por": usuarios["comercial"].id},
            )
            for nombre, nit, ciudad in CLIENTES
        ]

        for codigo, nombre, unidad, peligroso in TIPOS_RESIDUO:
            get_or_create(
                db,
                TipoResiduo,
                codigo=codigo,
                defaults={"nombre": nombre, "unidad_medida": unidad, "peligroso": peligroso},
            )

        for nombre in PLANTAS:
            get_or_create(db, PlantaCertificadora, nombre=nombre)

        db.flush()

        servicios_demo = [
            (clientes[0], "cotizado"),
            (clientes[1], "programado"),
            (clientes[2], "completado"),
        ]
        for cliente, estado in servicios_demo:
            existe = db.query(Servicio).filter_by(cliente_id=cliente.id, estado=estado).first()
            if existe:
                continue
            db.add(
                Servicio(
                    numero=generar_numero(db, Servicio, "SRV"),
                    cliente_id=cliente.id,
                    fecha_programada=date.today() + timedelta(days=3),
                    descripcion=f"Servicio de recolección — {cliente.razon_social}",
                    direccion_servicio=cliente.direccion or "Dirección de la sede",
                    ciudad_servicio=cliente.ciudad,
                    estado=estado,
                    creado_por=usuarios["comercial"].id,
                )
            )
            db.flush()

        db.commit()
        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
