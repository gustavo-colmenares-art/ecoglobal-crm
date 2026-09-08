import base64
from io import BytesIO
from typing import Any

import qrcode
from weasyprint import HTML

from app.utils import company

_BASE_CSS = """
<style>
  body { font-family: Helvetica, Arial, sans-serif; font-size: 11px; color: #222; }
  h1 { font-size: 18px; margin-bottom: 0; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #2e7d32; padding-bottom: 8px; }
  .empresa { color: #2e7d32; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  th, td { border: 1px solid #ccc; padding: 6px; text-align: left; font-size: 10px; }
  th { background: #f0f5f0; }
  .totales { margin-top: 10px; text-align: right; }
  .firma { margin-top: 40px; display: flex; justify-content: space-between; }
  .firma div { width: 45%; border-top: 1px solid #333; text-align: center; padding-top: 4px; }
  .qr { text-align: right; }
  .seccion { margin-top: 14px; }
</style>
"""


def _qr_data_uri(texto: str) -> str:
    img = qrcode.make(texto)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def generar_pdf_manifiesto(data: dict[str, Any]) -> bytes:
    qr = _qr_data_uri(data["numero"])
    filas = "".join(
        f"""<tr>
            <td>{it['codigo']}</td>
            <td>{it['nombre']}</td>
            <td>{it.get('cantidad_declarada') or '-'}</td>
            <td>{it.get('cantidad_real') or '-'}</td>
            <td>{it.get('unidad_medida') or '-'}</td>
        </tr>"""
        for it in data["items"]
    )
    html = f"""
    <html><head>{_BASE_CSS}</head><body>
      <div class="header">
        <div class="empresa">
          <h1>{company.EMPRESA_NOMBRE}</h1>
          <div>NIT: {company.EMPRESA_NIT}</div>
          <div>{company.EMPRESA_DIRECCION} — {company.EMPRESA_CIUDAD}</div>
        </div>
        <div class="qr"><img src="{qr}" width="90" height="90" /></div>
      </div>

      <h2>Manifiesto de Carga {data['numero']}</h2>
      <div>Fecha de generación: {data['fecha_generacion']}</div>
      <div>Servicio: {data['servicio_numero']}</div>

      <div class="seccion">
        <strong>Cliente:</strong> {data['cliente']['razon_social']} — NIT {data['cliente']['nit']}<br/>
        {data['cliente'].get('direccion') or ''} — {data['cliente'].get('ciudad') or ''}<br/>
        Contacto: {data['cliente'].get('contacto_nombre') or '-'}
      </div>

      <div class="seccion">
        <strong>Operario / conductor:</strong> {data.get('operario_nombre') or '-'}
      </div>

      <table>
        <thead>
          <tr><th>Código</th><th>Descripción</th><th>Cant. declarada</th><th>Cant. real</th><th>Unidad</th></tr>
        </thead>
        <tbody>{filas}</tbody>
      </table>

      <div class="firma">
        <div>Firma del cliente<br/>{data.get('nombre_receptor') or ''}<br/>{data.get('cargo_receptor') or ''}</div>
        <div>Firma {company.EMPRESA_NOMBRE}</div>
      </div>
    </body></html>
    """
    return HTML(string=html).write_pdf()


def generar_pdf_factura(data: dict[str, Any]) -> bytes:
    filas = "".join(
        f"""<tr>
            <td>{it['descripcion']}</td>
            <td>{it['cantidad']}</td>
            <td>{it['precio_unitario']:,.2f}</td>
            <td>{it['descuento_pct']}%</td>
            <td>{it['subtotal']:,.2f}</td>
        </tr>"""
        for it in data["items"]
    )
    html = f"""
    <html><head>{_BASE_CSS}</head><body>
      <div class="header">
        <div class="empresa">
          <h1>{company.EMPRESA_NOMBRE}</h1>
          <div>NIT: {company.EMPRESA_NIT}</div>
          <div>{company.EMPRESA_DIRECCION} — {company.EMPRESA_CIUDAD}</div>
          <div>{company.EMPRESA_REGIMEN}</div>
        </div>
        <div>
          <h2>Factura {data['numero']}</h2>
          <div>Emisión: {data['fecha_emision']}</div>
          <div>Vencimiento: {data.get('fecha_vencimiento') or '-'}</div>
        </div>
      </div>

      <div class="seccion">
        <strong>Cliente:</strong> {data['cliente']['razon_social']} — NIT {data['cliente']['nit']}<br/>
        {data['cliente'].get('direccion') or ''} — {data['cliente'].get('ciudad') or ''}
      </div>

      <table>
        <thead>
          <tr><th>Descripción</th><th>Cantidad</th><th>Precio unitario</th><th>Descuento</th><th>Subtotal</th></tr>
        </thead>
        <tbody>{filas}</tbody>
      </table>

      <div class="totales">
        <div>Subtotal: {data['subtotal']:,.2f}</div>
        <div>IVA: {data['iva']:,.2f}</div>
        <div>Descuento: {data['descuento']:,.2f}</div>
        <div><strong>TOTAL: {data['total']:,.2f}</strong></div>
      </div>

      <div class="seccion">
        <strong>Condiciones de pago:</strong> {data.get('condiciones_pago') or '-'}<br/>
        <strong>Datos bancarios:</strong> {company.EMPRESA_BANCO_INFO}
      </div>
    </body></html>
    """
    return HTML(string=html).write_pdf()
