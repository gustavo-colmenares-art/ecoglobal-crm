import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Col, DatePicker, Descriptions, Drawer, Form, Input, InputNumber, List, Modal, Row, Select, Statistic, Table, Tag, message } from "antd";
import dayjs from "dayjs";
import { useState } from "react";

import { dashboardCartera, gestionesDeFactura, listarCartera, registrarGestion, registrarPago, reporteCartera } from "@/api/cartera";
import { useAuthStore } from "@/store/auth";
import type { CarteraFactura } from "@/types";

const formatCOP = (v: number) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v);

function semaforo(dias: number) {
  if (dias <= 0) return "green";
  if (dias <= 15) return "gold";
  return "red";
}

export default function Cartera() {
  const [facturaSel, setFacturaSel] = useState<CarteraFactura | null>(null);
  const [modalPago, setModalPago] = useState(false);
  const [modalGestion, setModalGestion] = useState(false);
  const [pagoForm] = Form.useForm();
  const [gestionForm] = Form.useForm();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeEditar = rol === "superadmin" || rol === "cartera";

  const { data, isLoading } = useQuery({ queryKey: ["cartera"], queryFn: listarCartera });
  const { data: dashboard } = useQuery({ queryKey: ["cartera", "dashboard"], queryFn: dashboardCartera });
  const { data: reporte } = useQuery({ queryKey: ["cartera", "reporte"], queryFn: reporteCartera });
  const { data: gestiones } = useQuery({
    queryKey: ["cartera", "gestiones", facturaSel?.id],
    queryFn: () => gestionesDeFactura(facturaSel!.id),
    enabled: !!facturaSel,
  });

  const pagar = useMutation({
    mutationFn: (values: any) =>
      registrarPago({
        ...values,
        factura_id: facturaSel!.id,
        fecha_pago: dayjs(values.fecha_pago).format("YYYY-MM-DD"),
      }),
    onSuccess: () => {
      message.success("Pago registrado");
      queryClient.invalidateQueries({ queryKey: ["cartera"] });
      setModalPago(false);
      pagoForm.resetFields();
    },
    onError: () => message.error("No se pudo registrar el pago"),
  });

  const gestionar = useMutation({
    mutationFn: (values: any) =>
      registrarGestion({
        ...values,
        factura_id: facturaSel!.id,
        fecha_proxima: values.fecha_proxima ? dayjs(values.fecha_proxima).format("YYYY-MM-DD") : undefined,
      }),
    onSuccess: () => {
      message.success("Gestión registrada");
      queryClient.invalidateQueries({ queryKey: ["cartera", "gestiones", facturaSel?.id] });
      setModalGestion(false);
      gestionForm.resetFields();
    },
    onError: () => message.error("No se pudo registrar la gestión"),
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="Cartera total" value={dashboard ? formatCOP(dashboard.cartera_total) : "—"} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Facturas vencidas" value={dashboard?.facturas_vencidas} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Monto vencido" value={dashboard ? formatCOP(dashboard.monto_vencido) : "—"} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Días promedio de recaudo" value={dashboard?.dias_promedio_recaudo} suffix="días" />
          </Card>
        </Col>
      </Row>

      <Card title="Edades de cartera">
        <Row gutter={16}>
          <Col span={6}>
            <Statistic title="0-30 días" value={reporte ? formatCOP(reporte.rango_0_30) : "—"} />
          </Col>
          <Col span={6}>
            <Statistic title="31-60 días" value={reporte ? formatCOP(reporte.rango_31_60) : "—"} />
          </Col>
          <Col span={6}>
            <Statistic title="61-90 días" value={reporte ? formatCOP(reporte.rango_61_90) : "—"} />
          </Col>
          <Col span={6}>
            <Statistic title="Más de 90 días" value={reporte ? formatCOP(reporte.rango_mas_90) : "—"} />
          </Col>
        </Row>
      </Card>

      <Card title="Cuentas por cobrar">
        <Table<CarteraFactura>
          rowKey="id"
          loading={isLoading}
          dataSource={data}
          onRow={(record) => ({ onClick: () => setFacturaSel(record) })}
          columns={[
            { title: "Número", dataIndex: "numero" },
            { title: "Vencimiento", dataIndex: "fecha_vencimiento" },
            { title: "Total", dataIndex: "total", render: formatCOP },
            { title: "Saldo", dataIndex: "saldo", render: formatCOP },
            {
              title: "Días vencida",
              dataIndex: "dias_vencida",
              render: (dias: number) => <Tag color={semaforo(dias)}>{dias}</Tag>,
            },
            { title: "Estado", dataIndex: "estado" },
          ]}
        />
      </Card>

      <Drawer title={facturaSel?.numero} width={480} open={!!facturaSel} onClose={() => setFacturaSel(null)}>
        {facturaSel && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Saldo">{formatCOP(facturaSel.saldo)}</Descriptions.Item>
              <Descriptions.Item label="Días vencida">
                <Tag color={semaforo(facturaSel.dias_vencida)}>{facturaSel.dias_vencida}</Tag>
              </Descriptions.Item>
            </Descriptions>

            {puedeEditar && (
              <>
                <div style={{ display: "flex", gap: 8, margin: "16px 0" }}>
                  <Button onClick={() => setModalPago(true)}>Registrar pago</Button>
                  <Button onClick={() => setModalGestion(true)}>Registrar gestión</Button>
                </div>
              </>
            )}

            <h4>Historial de gestiones</h4>
            <List
              dataSource={gestiones}
              renderItem={(g) => (
                <List.Item>
                  <div>
                    <div>
                      <Tag>{g.tipo_gestion}</Tag> {g.fecha_gestion}
                    </div>
                    <div>{g.resultado}</div>
                    {g.proxima_accion && <div style={{ color: "#888" }}>Próxima acción: {g.proxima_accion}</div>}
                  </div>
                </List.Item>
              )}
            />
          </>
        )}
      </Drawer>

      <Modal open={modalPago} title="Registrar pago" onCancel={() => setModalPago(false)} onOk={() => pagoForm.submit()} confirmLoading={pagar.isPending}>
        <Form form={pagoForm} layout="vertical" onFinish={(v) => pagar.mutate(v)}>
          <Form.Item name="fecha_pago" label="Fecha de pago" rules={[{ required: true }]}>
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="monto" label="Monto" rules={[{ required: true }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="medio_pago" label="Medio de pago">
            <Select options={["transferencia", "cheque", "efectivo", "otro"].map((m) => ({ value: m, label: m }))} />
          </Form.Item>
          <Form.Item name="banco" label="Banco">
            <Input />
          </Form.Item>
          <Form.Item name="referencia" label="Referencia">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      <Modal open={modalGestion} title="Registrar gestión de cobro" onCancel={() => setModalGestion(false)} onOk={() => gestionForm.submit()} confirmLoading={gestionar.isPending}>
        <Form form={gestionForm} layout="vertical" onFinish={(v) => gestionar.mutate(v)}>
          <Form.Item name="tipo_gestion" label="Tipo" rules={[{ required: true }]}>
            <Select options={["llamada", "email", "visita", "acuerdo_pago"].map((t) => ({ value: t, label: t }))} />
          </Form.Item>
          <Form.Item name="resultado" label="Resultado">
            <Input.TextArea />
          </Form.Item>
          <Form.Item name="proxima_accion" label="Próxima acción">
            <Input />
          </Form.Item>
          <Form.Item name="fecha_proxima" label="Fecha próxima acción">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
