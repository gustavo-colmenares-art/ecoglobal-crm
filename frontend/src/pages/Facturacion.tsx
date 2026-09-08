import { DownloadOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Card,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  message,
} from "antd";
import { useState } from "react";

import {
  SIGUIENTE_ESTADO_FACTURA,
  cambiarEstadoFactura,
  crearFactura,
  listarFacturas,
  obtenerFactura,
  rutaPdfFactura,
  type FacturaInput,
} from "@/api/facturas";
import { listarServicios } from "@/api/servicios";
import { useAuthStore } from "@/store/auth";
import type { Factura } from "@/types";
import { abrirPdf } from "@/utils/pdf";

const ESTADO_COLOR: Record<string, string> = {
  borrador: "default",
  emitida: "blue",
  enviada: "cyan",
  parcialmente_pagada: "gold",
  pagada: "green",
  vencida: "red",
  anulada: "default",
};

const formatCOP = (v: number) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v);

export default function Facturacion() {
  const [filtroEstado, setFiltroEstado] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [facturaId, setFacturaId] = useState<number | null>(null);
  const [nuevoEstado, setNuevoEstado] = useState<string | undefined>();
  const [form] = Form.useForm<FacturaInput>();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeEditar = rol === "superadmin" || rol === "contabilidad";

  const { data, isLoading } = useQuery({
    queryKey: ["facturas", filtroEstado],
    queryFn: () => listarFacturas({ estado: filtroEstado, page: 1 }),
  });

  const { data: servicios } = useQuery({
    queryKey: ["servicios", "select-fact"],
    queryFn: () => listarServicios({ page: 1 }),
  });

  const { data: detalle } = useQuery({
    queryKey: ["facturas", facturaId],
    queryFn: () => obtenerFactura(facturaId!),
    enabled: !!facturaId,
  });

  const crear = useMutation({
    mutationFn: (values: FacturaInput) => crearFactura(values),
    onSuccess: () => {
      message.success("Factura creada");
      queryClient.invalidateQueries({ queryKey: ["facturas"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("No se pudo crear la factura"),
  });

  const cambiarEstado = useMutation({
    mutationFn: () => cambiarEstadoFactura(facturaId!, nuevoEstado!),
    onSuccess: () => {
      message.success("Estado actualizado");
      queryClient.invalidateQueries({ queryKey: ["facturas"] });
      setNuevoEstado(undefined);
    },
    onError: (e: any) => message.error(e?.response?.data?.detail ?? "No se pudo cambiar el estado"),
  });

  return (
    <Card
      title="Facturación"
      extra={
        puedeEditar && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Nueva factura
          </Button>
        )
      }
    >
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Estado"
          allowClear
          style={{ width: 220 }}
          options={Object.keys(ESTADO_COLOR).map((e) => ({ value: e, label: e }))}
          onChange={setFiltroEstado}
        />
      </Space>

      <Table<Factura>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        onRow={(record) => ({ onClick: () => setFacturaId(record.id) })}
        columns={[
          { title: "Número", dataIndex: "numero" },
          { title: "Emisión", dataIndex: "fecha_emision" },
          { title: "Vencimiento", dataIndex: "fecha_vencimiento" },
          { title: "Total", dataIndex: "total", render: formatCOP },
          { title: "Estado", dataIndex: "estado", render: (e: string) => <Tag color={ESTADO_COLOR[e]}>{e}</Tag> },
          {
            title: "PDF",
            render: (_: unknown, r: Factura) => (
              <Button
                type="link"
                icon={<DownloadOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  abrirPdf(rutaPdfFactura(r.id));
                }}
              />
            ),
          },
        ]}
      />

      <Drawer title={detalle?.numero} width={520} open={!!facturaId} onClose={() => setFacturaId(null)}>
        {detalle && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Estado">
                <Tag color={ESTADO_COLOR[detalle.estado]}>{detalle.estado}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Subtotal">{formatCOP(detalle.subtotal)}</Descriptions.Item>
              <Descriptions.Item label="IVA">{formatCOP(detalle.iva)}</Descriptions.Item>
              <Descriptions.Item label="Descuento">{formatCOP(detalle.descuento)}</Descriptions.Item>
              <Descriptions.Item label="Total">
                <strong>{formatCOP(detalle.total)}</strong>
              </Descriptions.Item>
              <Descriptions.Item label="Condiciones de pago">{detalle.condiciones_pago || "—"}</Descriptions.Item>
            </Descriptions>

            <h4 style={{ marginTop: 16 }}>Ítems</h4>
            <Table
              size="small"
              rowKey="id"
              pagination={false}
              dataSource={detalle.items}
              columns={[
                { title: "Descripción", dataIndex: "descripcion" },
                { title: "Cant.", dataIndex: "cantidad" },
                { title: "Precio", dataIndex: "precio_unitario", render: formatCOP },
                { title: "Subtotal", dataIndex: "subtotal", render: formatCOP },
              ]}
            />

            {puedeEditar && SIGUIENTE_ESTADO_FACTURA[detalle.estado]?.length > 0 && (
              <Card size="small" title="Cambiar estado" style={{ marginTop: 16 }}>
                <Space>
                  <Select
                    style={{ width: 200 }}
                    placeholder="Nuevo estado"
                    value={nuevoEstado}
                    onChange={setNuevoEstado}
                    options={SIGUIENTE_ESTADO_FACTURA[detalle.estado].map((e) => ({ value: e, label: e }))}
                  />
                  <Button type="primary" disabled={!nuevoEstado} onClick={() => cambiarEstado.mutate()}>
                    Confirmar
                  </Button>
                </Space>
              </Card>
            )}
          </>
        )}
      </Drawer>

      <Modal open={modalOpen} title="Nueva factura" onCancel={() => setModalOpen(false)} onOk={() => form.submit()} confirmLoading={crear.isPending} width={640}>
        <Form form={form} layout="vertical" onFinish={(values) => crear.mutate(values)}>
          <Form.Item name="servicio_id" label="Servicio" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={servicios?.items.map((s) => ({ value: s.id, label: `${s.numero} — ${s.estado}` }))}
            />
          </Form.Item>
          <Form.Item name="fecha_vencimiento" label="Fecha de vencimiento">
            <Input type="date" />
          </Form.Item>
          <Form.Item name="condiciones_pago" label="Condiciones de pago" initialValue="30 días">
            <Input />
          </Form.Item>
          <Form.Item name="descuento" label="Descuento general" initialValue={0}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="baseline" style={{ display: "flex", marginBottom: 8 }}>
                    <Form.Item name={[field.name, "descripcion"]} rules={[{ required: true }]} style={{ marginBottom: 0, width: 200 }}>
                      <Input placeholder="Descripción" />
                    </Form.Item>
                    <Form.Item name={[field.name, "cantidad"]} initialValue={1} style={{ marginBottom: 0, width: 90 }}>
                      <InputNumber placeholder="Cant." />
                    </Form.Item>
                    <Form.Item name={[field.name, "precio_unitario"]} rules={[{ required: true }]} style={{ marginBottom: 0, width: 130 }}>
                      <InputNumber placeholder="Precio unit." />
                    </Form.Item>
                    <Form.Item name={[field.name, "descuento_pct"]} initialValue={0} style={{ marginBottom: 0, width: 90 }}>
                      <InputNumber placeholder="Desc. %" />
                    </Form.Item>
                    <Button danger onClick={() => remove(field.name)}>
                      Quitar
                    </Button>
                  </Space>
                ))}
                <Button onClick={() => add()} block>
                  + Agregar ítem
                </Button>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </Card>
  );
}
