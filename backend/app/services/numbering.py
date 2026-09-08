from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def generar_numero(db: Session, model, prefix: str, campo: str = "numero") -> str:
    year = datetime.now().year
    columna = getattr(model, campo)
    count = db.scalar(
        select(func.count()).select_from(model).where(columna.like(f"{prefix}-{year}-%"))
    ) or 0
    return f"{prefix}-{year}-{count + 1:05d}"
