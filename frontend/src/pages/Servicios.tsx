import { PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Card,
  DatePicker,
  Descriptions,
  Drawer,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Timeline,
  message,
} from "antd";
import dayjs from "dayjs";
import { useState } from "react";

import { listarClientes } from "@/api/clientes";
import {
  ETAPAS_SERVICIO,
  SIGUIENTE_ESTADO,
  cambiarEstadoServicio,
  crearServicio,
  historialServicio,
  listarServicios,
  obtenerServicio,
  type ServicioInput,
} from "@/api/servicios";
import { useAuthStore } from "@/store/auth";
import type { Servicio } from "@/types";

const ESTADO_COLOR: Record<string, string> = {
  cotizado: "default",
  confirmado: "blue",
  programado: "cyan",
  en_ruta: "geekblue",
  atendido: "purple",
  manifiesto_pendiente: "orange",
  manifiesto_recibido: "gold",
  completado: "green",
  cancelado: "red",
};

export default function Servicios() {
  const [filtros, setFiltros] = useState<{ estado?: string; prioridad?: string }>({});
  const [modalOpen, setModalOpen] = useState(false);
  const [servicioId, setServicioId] = useState<number | null>(null);
  const [nuevoEstado, setNuevoEstado] = useState<string | undefined>();
  const [nota, setNota] = useState("");
  const [form] = Form.useForm<ServicioInput>();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeCrear = rol === "superadmin" || rol === "comercial";
  const puedeCambiarEstado = puedeCrear || rol === "operaciones";

  const { data, isLoading } = useQuery({
    queryKey: ["servicios", filtros],
    queryFn: () => listarServicios({ ...filtros, page: 1 }),
  });

  const { data: clientes } = useQuery({
    queryKey: ["clientes", "select"],
    queryFn: () => listarClientes({ page: 1, size: 500 }),
  });

  const nombreCliente = (clienteId: number) =>
    clientes?.items.find((c) => c.id === clienteId)?.razon_social ?? `Cliente #${clienteId}`;

  const { data: detalle } = useQuery({
    queryKey: ["servicios", servicioId],
    queryFn: () => obtenerServicio(servicioId!),
    enabled: !!servicioId,
  });

  const { data: historial } = useQuery({
    queryKey: ["servicios", servicioId, "historial"],
    queryFn: () => historialServicio(servicioId!),
    enabled: !!servicioId,
  });

  const crear = useMutation({
    mutationFn: (values: ServicioInput) =>
      crearServicio({
        ...values,
        fecha_programada: values.fecha_programada
          ? dayjs(values.fecha_programada as unknown as string).format("YYYY-MM-DD")
          : undefined,
      }),
    onSuccess: () => {
      message.success("Servicio creado");
      queryClient.invalidateQueries({ queryKey: ["servicios"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("No se pudo crear el servicio"),
  });

  const cambiarEstado = useMutation({
    mutationFn: () => cambiarEstadoServicio(servicioId!, nuevoEstado!, nota),
    onSuccess: () => {
      message.success("Estado actualizado");
      queryClient.invalidateQueries({ queryKey: ["servicios"] });
      setNuevoEstado(undefined);
      setNota("");
    },
    onError: (e: any) => message.error(e?.response?.data?.detail ?? "No se pudo cambiar el estado"),
  });

  return (
    <Card
      title="Servicios"
      extra={
        puedeCrear && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Nuevo servicio
          </Button>
        )
      }
    >
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="Estado"
          allowClear
          style={{ width: 200 }}
          options={ETAPAS_SERVICIO.map((e) => ({ value: e, label: e }))}
          onChange={(v) => setFiltros((f) => ({ ...f, estado: v }))}
        />
        <Select
          placeholder="Prioridad"
          allowClear
          style={{ width: 160 }}
          options={["baja", "normal", "alta", "urgente"].map((p) => ({ value: p, label: p }))}
          onChange={(v) => setFiltros((f) => ({ ...f, prioridad: v }))}
        />
      </Space>

      <Table<Servicio>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        onRow={(record) => ({ onClick: () => setServicioId(record.id) })}
        columns={[
          { title: "Número", dataIndex: "numero" },
          {
            title: "Cliente",
            dataIndex: "cliente_id",
            render: (clienteId: number) => nombreCliente(clienteId),
          },
          { title: "Fecha solicitud", dataIndex: "fecha_solicitud" },
          { title: "Fecha programada", dataIndex: "fecha_programada" },
          { title: "Prioridad", dataIndex: "prioridad" },
          {
            title: "Estado",
            dataIndex: "estado",
            render: (estado: string) => <Tag color={ESTADO_COLOR[estado]}>{estado}</Tag>,
          },
        ]}
      />

      <Drawer title={detalle?.numero} width={480} open={!!servicioId} onClose={() => setServicioId(null)}>
        {detalle && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Cliente">{detalle.cliente?.razon_social}</Descriptions.Item>
              <Descriptions.Item label="Estado">
                <Tag color={ESTADO_COLOR[detalle.estado]}>{detalle.estado}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Dirección">{detalle.direccion_servicio}</Descriptions.Item>
              <Descriptions.Item label="Manifiesto">
                {detalle.manifiesto ? `${detalle.manifiesto.numero} (${detalle.manifiesto.estado})` : "—"}
              </Descriptions.Item>
              <Descriptions.Item label="Factura">
                {detalle.factura ? `${detalle.factura.numero} (${detalle.factura.estado})` : "—"}
              </Descriptions.Item>
              <Descriptions.Item label="Observaciones">{detalle.observaciones || "—"}</Descriptions.Item>
            </Descriptions>

            {puedeCambiarEstado && SIGUIENTE_ESTADO[detalle.estado]?.length > 0 && (
              <Card size="small" title="Cambiar estado" style={{ marginTop: 16 }}>
                <Space direction="vertical" style={{ width: "100%" }}>
                  <Select
                    style={{ width: "100%" }}
                    placeholder="Nuevo estado"
                    value={nuevoEstado}
                    onChange={setNuevoEstado}
                    options={SIGUIENTE_ESTADO[detalle.estado].map((e) => ({ value: e, label: e }))}
                  />
                  <Input.TextArea
                    placeholder="Nota (obligatoria)"
                    value={nota}
                    onChange={(e) => setNota(e.target.value)}
                  />
                  <Button
                    type="primary"
                    loading={cambiarEstado.isPending}
                    onClick={() => {
                      if (!nuevoEstado) {
                        message.warning("Selecciona el nuevo estado");
                        return;
                      }
                      if (!nota.trim()) {
                        message.warning("Escribe una nota antes de confirmar");
                        return;
                      }
                      cambiarEstado.mutate();
                    }}
                  >
                    Confirmar cambio
                  </Button>
                </Space>
              </Card>
            )}

            <h4 style={{ marginTop: 16 }}>Línea de tiempo</h4>
            <Timeline
              items={historial?.map((h) => ({
                children: (
                  <>
                    <div>
                      {h.estado_antes ?? "—"} → <strong>{h.estado_nuevo}</strong>
                    </div>
                    <div style={{ color: "#888", fontSize: 12 }}>{h.cambiado_en}</div>
                    {h.nota && <div>{h.nota}</div>}
                  </>
                ),
              }))}
            />
          </>
        )}
      </Drawer>

      <Modal
        title="Nuevo servicio"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={crear.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => crear.mutate(values)}>
          <Form.Item name="cliente_id" label="Cliente" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={clientes?.items.map((c) => ({ value: c.id, label: c.razon_social }))}
            />
          </Form.Item>
          <Form.Item name="fecha_programada" label="Fecha programada">
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="direccion_servicio" label="Dirección del servicio">
            <Input />
          </Form.Item>
          <Form.Item name="ciudad_servicio" label="Ciudad">
            <Input />
          </Form.Item>
          <Form.Item name="prioridad" label="Prioridad" initialValue="normal">
            <Select options={["baja", "normal", "alta", "urgente"].map((p) => ({ value: p, label: p }))} />
          </Form.Item>
          <Form.Item name="descripcion" label="Descripción">
            <Input.TextArea />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
