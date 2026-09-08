import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.services import alertas
from app.utils.notifications import enviar_email

logger = logging.getLogger("ecoglobal.scheduler")

scheduler = AsyncIOScheduler()


async def revisar_alertas_diarias() -> None:
    db = SessionLocal()
    try:
        from app.models.rol import Rol

        def emails_por_rol(*roles: str) -> list[str]:
            return [
                u.email
                for u in db.scalars(
                    select(Usuario).join(Rol).where(Rol.nombre.in_(roles), Usuario.activo.is_(True))
                ).all()
            ]

        operaciones = emails_por_rol("superadmin", "operaciones")
        cartera = emails_por_rol("superadmin", "cartera")
        comercial = emails_por_rol("superadmin", "comercial")

        demorados = alertas.manifiestos_demorados(db)
        if demorados:
            lista = "".join(f"<li>{m.numero} — recolectado {m.fecha_recoleccion}</li>" for m in demorados)
            await enviar_email(operaciones, "Manifiestos demorados en campo", f"<ul>{lista}</ul>")

        sin_certificar = alertas.declaraciones_sin_certificar(db)
        if sin_certificar:
            lista = "".join(f"<li>{d.numero} — enviada {d.fecha_envio}</li>" for d in sin_certificar)
            await enviar_email(operaciones, "Declaraciones sin certificar", f"<ul>{lista}</ul>")

        por_vencer = alertas.facturas_por_vencer(db)
        if por_vencer:
            lista = "".join(f"<li>{f.numero} — vence {f.fecha_vencimiento} — ${f.total}</li>" for f in por_vencer)
            await enviar_email(cartera, "Facturas próximas a vencer", f"<ul>{lista}</ul>")

        vencidas = alertas.facturas_vencidas(db)
        if vencidas:
            lista = "".join(f"<li>{f.numero} — cliente {f.cliente_id} — ${f.total}</li>" for f in vencidas)
            await enviar_email(cartera, "Facturas vencidas", f"<ul>{lista}</ul>")

        cotizaciones_frias = alertas.servicios_cotizados_sin_seguimiento(db)
        if cotizaciones_frias:
            lista = "".join(
                f"<li>{s.numero} — cotizado el {s.creado_en.date()}, sin novedad desde {s.actualizado_en.date()}</li>"
                for s in cotizaciones_frias
            )
            await enviar_email(
                comercial, "Cotizaciones sin seguimiento (8+ días)", f"<ul>{lista}</ul>"
            )

        leads_frios = alertas.leads_sin_atender(db)
        if leads_frios:
            lista = "".join(
                f"<li>{lead.telefono} ({lead.nombre_contacto or 'sin nombre'}) — llegó el {lead.creado_en.date()}</li>"
                for lead in leads_frios
            )
            await enviar_email(comercial, "Leads de WhatsApp sin atender", f"<ul>{lista}</ul>")
    except Exception:
        logger.exception("Error ejecutando la revisión diaria de alertas")
    finally:
        db.close()


def iniciar_scheduler() -> None:
    scheduler.add_job(
        revisar_alertas_diarias,
        CronTrigger(hour=8, minute=0),
        id="alertas_diarias",
        replace_existing=True,
    )
    scheduler.start()


def detener_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
