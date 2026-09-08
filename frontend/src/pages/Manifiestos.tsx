import { DownloadOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Card,
  Checkbox,
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

import { listarResiduos } from "@/api/maestros";
import {
  SIGUIENTE_ESTADO_MANIFIESTO,
  actualizarManifiesto,
  cambiarEstadoManifiesto,
  crearManifiesto,
  listarManifiestos,
  obtenerManifiesto,
  rutaPdfManifiesto,
  type ManifiestoInput,
} from "@/api/manifiestos";
import { listarServicios } from "@/api/servicios";
import { useAuthStore } from "@/store/auth";
import type { Manifiesto } from "@/types";
import { abrirPdf } from "@/utils/pdf";

const ESTADO_COLOR: Record<string, string> = {
  generado: "default",
  en_campo: "blue",
  recibido: "gold",
  declarado: "purple",
  cerrado: "green",
};

export default function Manifiestos() {
  const [filtroEstado, setFiltroEstado] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [manifiestoId, setManifiestoId] = useState<number | null>(null);
  const [nuevoEstado, setNuevoEstado] = useState<string | undefined>();
  const [form] = Form.useForm<ManifiestoInput>();
  const [retornoForm] = Form.useForm();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeEditar = rol === "superadmin" || rol === "operaciones";

  const { data, isLoading } = useQuery({
    queryKey: ["manifiestos", filtroEstado],
    queryFn: () => listarManifiestos({ estado: filtroEstado, page: 1 }),
  });

  const { data: servicios } = useQuery({
    queryKey: ["servicios", "select"],
    queryFn: () => listarServicios({ page: 1 }),
  });

  const { data: residuos } = useQuery({ queryKey: ["residuos"], queryFn: listarResiduos });

  const { data: detalle } = useQuery({
    queryKey: ["manifiestos", manifiestoId],
    queryFn: () => obtenerManifiesto(manifiestoId!),
    enabled: !!manifiestoId,
  });

  const crear = useMutation({
    mutationFn: (values: ManifiestoInput) => crearManifiesto(values),
    onSuccess: () => {
      message.success("Manifiesto generado");
      queryClient.invalidateQueries({ queryKey: ["manifiestos"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("No se pudo generar el manifiesto"),
  });

  const cambiarEstado = useMutation({
    mutationFn: () => cambiarEstadoManifiesto(manifiestoId!, nuevoEstado!, "Cambio de estado"),
    onSuccess: () => {
      message.success("Estado actualizado");
      queryClient.invalidateQueries({ queryKey: ["manifiestos"] });
      setNuevoEstado(undefined);
    },
    onError: (e: any) => message.error(e?.response?.data?.detail ?? "No se pudo cambiar el estado"),
  });

  const guardarRetorno = useMutation({
    mutationFn: (values: any) =>
      actualizarManifiesto(manifiestoId!, {
        fecha_retorno: values.fecha_retorno,
        firma_cliente: values.firma_cliente,
        nombre_receptor: values.nombre_receptor,
        cargo_receptor: values.cargo_receptor,
        observaciones_retorno: values.observaciones_retorno,
      } as any),
    onSuccess: () => {
      message.success("Registro de retorno guardado");
      queryClient.invalidateQueries({ queryKey: ["manifiestos", manifiestoId] });
    },
    onError: () => message.error("No se pudo guardar"),
  });

  return (
    <Card
      title="Manifiestos"
      extra={
        puedeEditar && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Generar manifiesto
          </Button>
        )
      }
    >
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Estado"
          allowClear
          style={{ width: 200 }}
          options={Object.keys(ESTADO_COLOR).map((e) => ({ value: e, label: e }))}
          onChange={setFiltroEstado}
        />
      </Space>

      <Table<Manifiesto>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        onRow={(record) => ({ onClick: () => setManifiestoId(record.id) })}
        columns={[
          { title: "Número", dataIndex: "numero" },
          { title: "Fecha generación", dataIndex: "fecha_generacion" },
          { title: "Fecha recolección", dataIndex: "fecha_recoleccion" },
          { title: "Fecha retorno", dataIndex: "fecha_retorno" },
          { title: "Estado", dataIndex: "estado", render: (e: string) => <Tag color={ESTADO_COLOR[e]}>{e}</Tag> },
          {
            title: "PDF",
            render: (_: unknown, r: Manifiesto) => (
              <Button
                type="link"
                icon={<DownloadOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  abrirPdf(rutaPdfManifiesto(r.id));
                }}
              />
            ),
          },
        ]}
      />

      <Drawer title={detalle?.numero} width={520} open={!!manifiestoId} onClose={() => setManifiestoId(null)}>
        {detalle && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Estado">
                <Tag color={ESTADO_COLOR[detalle.estado]}>{detalle.estado}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Firma cliente">{detalle.firma_cliente ? "Sí" : "No"}</Descriptions.Item>
              <Descriptions.Item label="Receptor">
                {detalle.nombre_receptor} {detalle.cargo_receptor && `(${detalle.cargo_receptor})`}
              </Descriptions.Item>
            </Descriptions>

            <h4 style={{ marginTop: 16 }}>Residuos</h4>
            <Table
              size="small"
              rowKey="id"
              pagination={false}
              dataSource={detalle.items}
              columns={[
                {
                  title: "Tipo",
                  dataIndex: "tipo_residuo_id",
                  render: (id: number) => residuos?.find((r) => r.id === id)?.nombre ?? id,
                },
                { title: "Declarada", dataIndex: "cantidad_declarada" },
                { title: "Real", dataIndex: "cantidad_real" },
                { title: "Unidad", dataIndex: "unidad_medida" },
              ]}
            />

            {puedeEditar && SIGUIENTE_ESTADO_MANIFIESTO[detalle.estado]?.length > 0 && (
              <Card size="small" title="Cambiar estado" style={{ marginTop: 16 }}>
                <Space>
                  <Select
                    style={{ width: 180 }}
                    placeholder="Nuevo estado"
                    value={nuevoEstado}
                    onChange={setNuevoEstado}
                    options={SIGUIENTE_ESTADO_MANIFIESTO[detalle.estado].map((e) => ({ value: e, label: e }))}
                  />
                  <Button type="primary" disabled={!nuevoEstado} onClick={() => cambiarEstado.mutate()}>
                    Confirmar
                  </Button>
                </Space>
              </Card>
            )}

            {puedeEditar && (
              <Card size="small" title="Registro de retorno" style={{ marginTop: 16 }}>
                <Form
                  form={retornoForm}
                  layout="vertical"
                  initialValues={detalle}
                  onFinish={(values) => guardarRetorno.mutate(values)}
                >
                  <Form.Item name="fecha_retorno" label="Fecha de retorno">
                    <Input type="date" />
                  </Form.Item>
                  <Form.Item name="nombre_receptor" label="Nombre del receptor">
                    <Input />
                  </Form.Item>
                  <Form.Item name="cargo_receptor" label="Cargo del receptor">
                    <Input />
                  </Form.Item>
                  <Form.Item name="firma_cliente" valuePropName="checked">
                    <Checkbox>Firma del cliente registrada</Checkbox>
                  </Form.Item>
                  <Form.Item name="observaciones_retorno" label="Observaciones">
                    <Input.TextArea />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" loading={guardarRetorno.isPending}>
                    Guardar
                  </Button>
                </Form>
              </Card>
            )}
          </>
        )}
      </Drawer>

      <Modal open={modalOpen} title="Generar manifiesto" onCancel={() => setModalOpen(false)} onOk={() => form.submit()} confirmLoading={crear.isPending} width={600}>
        <Form form={form} layout="vertical" onFinish={(values) => crear.mutate(values)}>
          <Form.Item name="servicio_id" label="Servicio" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={servicios?.items.map((s) => ({ value: s.id, label: `${s.numero} — ${s.estado}` }))}
            />
          </Form.Item>
          <Form.Item name="fecha_recoleccion" label="Fecha de recolección">
            <Input type="date" />
          </Form.Item>
          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="baseline" style={{ display: "flex", marginBottom: 8 }}>
                    <Form.Item name={[field.name, "tipo_residuo_id"]} rules={[{ required: true }]} style={{ marginBottom: 0, width: 200 }}>
                      <Select placeholder="Residuo" options={residuos?.map((r) => ({ value: r.id, label: r.nombre }))} />
                    </Form.Item>
                    <Form.Item name={[field.name, "cantidad_declarada"]} style={{ marginBottom: 0, width: 130 }}>
                      <InputNumber placeholder="Cantidad" />
                    </Form.Item>
                    <Form.Item name={[field.name, "unidad_medida"]} style={{ marginBottom: 0, width: 100 }}>
                      <Input placeholder="Unidad" />
                    </Form.Item>
                    <Button danger onClick={() => remove(field.name)}>
                      Quitar
                    </Button>
                  </Space>
                ))}
                <Button onClick={() => add()} block>
                  + Agregar residuo
                </Button>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </Card>
  );
}
