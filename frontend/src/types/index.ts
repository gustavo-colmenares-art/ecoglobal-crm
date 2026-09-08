export type Rol =
  | "superadmin"
  | "comercial"
  | "operaciones"
  | "contabilidad"
  | "cartera"
  | "visualizador";

export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  rol: { id: number; nombre: Rol; descripcion?: string | null } | null;
  activo: boolean;
  creado_en: string;
  ultimo_acceso: string | null;
}

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

export interface Cliente {
  id: number;
  razon_social: string;
  nit: string;
  direccion: string | null;
  ciudad: string | null;
  departamento: string | null;
  telefono: string | null;
  email: string | null;
  contacto_nombre: string | null;
  contacto_cargo: string | null;
  activo: boolean;
  creado_en: string;
}

export interface TipoResiduo {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
  unidad_medida: string;
  peligroso: boolean;
  activo: boolean;
}

export interface Planta {
  id: number;
  nombre: string;
  nit: string | null;
  direccion: string | null;
  ciudad: string | null;
  telefono: string | null;
  email: string | null;
  contacto: string | null;
  activo: boolean;
}

export interface Servicio {
  id: number;
  numero: string;
  cliente_id: number;
  fecha_solicitud: string;
  fecha_programada: string | null;
  descripcion: string | null;
  direccion_servicio: string | null;
  ciudad_servicio: string | null;
  estado: string;
  prioridad: string;
  observaciones: string | null;
  creado_en: string;
  actualizado_en: string;
}

export interface ServicioDetalle extends Servicio {
  cliente: Cliente | null;
  manifiesto: { id: number; numero: string; estado: string } | null;
  factura: { id: number; numero: string; estado: string; total: number } | null;
}

export interface ServicioHistorial {
  id: number;
  estado_antes: string | null;
  estado_nuevo: string | null;
  cambiado_por: number | null;
  nota: string | null;
  cambiado_en: string;
}

export interface ManifiestoItem {
  id: number;
  manifiesto_id: number;
  tipo_residuo_id: number;
  cantidad_declarada: number | null;
  cantidad_real: number | null;
  unidad_medida: string | null;
  descripcion_adicional: string | null;
  numero_contenedor: string | null;
  observaciones: string | null;
}

export interface Manifiesto {
  id: number;
  numero: string;
  servicio_id: number;
  operario_id: number | null;
  fecha_generacion: string;
  fecha_recoleccion: string | null;
  fecha_retorno: string | null;
  estado: string;
  firma_cliente: boolean;
  nombre_receptor: string | null;
  cargo_receptor: string | null;
  observaciones_campo: string | null;
  observaciones_retorno: string | null;
  creado_en: string;
  items: ManifiestoItem[];
}

export interface DeclaracionItem {
  id: number;
  declaracion_id: number;
  manifiesto_item_id: number | null;
  tipo_residuo_id: number;
  cantidad: number | null;
  unidad_medida: string | null;
  observaciones: string | null;
}

export interface Declaracion {
  id: number;
  numero: string;
  manifiesto_id: number;
  planta_id: number;
  fecha_envio: string | null;
  fecha_certificacion: string | null;
  numero_certificado: string | null;
  estado: string;
  observaciones: string | null;
  creado_en: string;
  items: DeclaracionItem[];
}

export interface FacturaItem {
  id: number;
  factura_id: number;
  descripcion: string;
  cantidad: number;
  precio_unitario: number | null;
  descuento_pct: number;
  subtotal: number | null;
  tipo_residuo_id: number | null;
}

export interface Factura {
  id: number;
  numero: string;
  servicio_id: number;
  cliente_id: number;
  fecha_emision: string;
  fecha_vencimiento: string | null;
  subtotal: number;
  iva: number;
  descuento: number;
  total: number;
  estado: string;
  observaciones: string | null;
  condiciones_pago: string | null;
  creado_en: string;
  items: FacturaItem[];
}

export interface CarteraFactura {
  id: number;
  numero: string;
  cliente_id: number;
  fecha_emision: string;
  fecha_vencimiento: string | null;
  total: number;
  saldo: number;
  estado: string;
  dias_vencida: number;
}

export interface Pago {
  id: number;
  factura_id: number;
  fecha_pago: string;
  monto: number;
  medio_pago: string | null;
  referencia: string | null;
  banco: string | null;
  observaciones: string | null;
  registrado_en: string;
}

export interface Gestion {
  id: number;
  factura_id: number;
  tipo_gestion: string | null;
  fecha_gestion: string;
  resultado: string | null;
  proxima_accion: string | null;
  fecha_proxima: string | null;
  gestionado_por: number | null;
  creado_en: string;
}

export interface CarteraReporte {
  rango_0_30: number;
  rango_31_60: number;
  rango_61_90: number;
  rango_mas_90: number;
  total: number;
}
