LEAD_TRANSICIONES = {
    "nuevo": ["en_conversacion", "no_atendido"],
    "en_conversacion": ["cotizacion", "servicio_directo", "no_atendido"],
    "cotizacion": ["convertido", "no_atendido"],
    "servicio_directo": ["convertido", "no_atendido"],
    "convertido": [],
    "no_atendido": [],
}

SERVICIO_TRANSICIONES = {
    "cotizado": ["confirmado"],
    "confirmado": ["programado"],
    "programado": ["en_ruta"],
    "en_ruta": ["atendido"],
    "atendido": ["manifiesto_pendiente"],
    "manifiesto_pendiente": ["manifiesto_recibido"],
    "manifiesto_recibido": ["completado"],
    "completado": [],
    "cancelado": [],
}

MANIFIESTO_TRANSICIONES = {
    "generado": ["en_campo"],
    "en_campo": ["recibido"],
    "recibido": ["declarado"],
    "declarado": ["cerrado"],
    "cerrado": [],
}

DECLARACION_TRANSICIONES = {
    "pendiente": ["enviada"],
    "enviada": ["certificada", "rechazada"],
    "certificada": [],
    "rechazada": ["pendiente"],
}

FACTURA_TRANSICIONES = {
    "borrador": ["emitida"],
    "emitida": ["enviada"],
    "enviada": ["parcialmente_pagada", "pagada", "vencida"],
    "parcialmente_pagada": ["pagada", "vencida"],
    "vencida": ["pagada", "parcialmente_pagada"],
    "pagada": [],
    "anulada": [],
}


def validar_transicion(mapa: dict[str, list[str]], estado_actual: str, estado_nuevo: str) -> bool:
    return estado_nuevo in mapa.get(estado_actual, [])
