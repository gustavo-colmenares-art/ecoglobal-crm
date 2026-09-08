import { PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Descriptions, Drawer, Form, Input, Modal, Select, Space, Table, Tabs, Tag, message } from "antd";
import { useState } from "react";

import {
  SIGUIENTE_ESTADO_DECLARACION,
  cambiarEstadoDeclaracion,
  certificarDeclaracion,
  crearDeclaracion,
  listarDeclaraciones,
  type DeclaracionInput,
} from "@/api/declaraciones";
import { listarManifiestos } from "@/api/manifiestos";
import { listarPlantas } from "@/api/maestros";
import { useAuthStore } from "@/store/auth";
import type { Declaracion } from "@/types";

const ESTADO_COLOR: Record<string, string> = {
  pendiente: "default",
  enviada: "blue",
  certificada: "green",
  rechazada: "red",
};

export default function Declaraciones() {
  const [plantaTab, setPlantaTab] = useState<string>("todas");
  const [modalOpen, setModalOpen] = useState(false);
  const [declaracionId, setDeclaracionId] = useState<number | null>(null);
  const [nuevoEstado, setNuevoEstado] = useState<string | undefined>();
  const [certForm] = Form.useForm();
  const [form] = Form.useForm<DeclaracionInput>();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeEditar = rol === "superadmin" || rol === "operaciones";

  const { data: plantas } = useQuery({ queryKey: ["plantas"], queryFn: listarPlantas });
  const { data: manifiestos } = useQuery({
    queryKey: ["manifiestos", "select"],
    queryFn: () => listarManifiestos({ estado: "recibido", page: 1 }),
  });

  const plantaId = plantaTab === "todas" ? undefined : Number(plantaTab);
  const { data, isLoading } = useQuery({
    queryKey: ["declaraciones", plantaId],
    queryFn: () => listarDeclaraciones({ planta_id: plantaId, page: 1 }),
  });

  const declaracion = data?.items.find((d) => d.id === declaracionId) as Declaracion | undefined;

  const crear = useMutation({
    mutationFn: (values: DeclaracionInput) => crearDeclaracion(values),
    onSuccess: () => {
      message.success("Declaración creada");
      queryClient.invalidateQueries({ queryKey: ["declaraciones"] });
      setModalOpen(false);
      form.resetFields();
    },
    onError: () => message.error("No se pudo crear la declaración"),
  });

  const cambiarEstado = useMutation({
    mutationFn: () => cambiarEstadoDeclaracion(declaracionId!, nuevoEstado!),
    onSuccess: () => {
      message.success("Estado actualizado");
      queryClient.invalidateQueries({ queryKey: ["declaraciones"] });
      setNuevoEstado(undefined);
    },
    onError: (e: any) => message.error(e?.response?.data?.detail ?? "No se pudo cambiar el estado"),
  });

  const certificar = useMutation({
    mutationFn: (values: any) =>
      certificarDeclaracion(declaracionId!, values.numero_certificado, values.fecha_certificacion),
    onSuccess: () => {
      message.success("Declaración certificada");
      queryClient.invalidateQueries({ queryKey: ["declaraciones"] });
      certForm.resetFields();
    },
    onError: () => message.error("No se pudo certificar"),
  });

  return (
    <Card
      title="Declaraciones a plantas certificadoras"
      extra={
        puedeEditar && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Nueva declaración
          </Button>
        )
      }
    >
      <Tabs
        activeKey={plantaTab}
        onChange={setPlantaTab}
        items={[
          { key: "todas", label: "Todas" },
          ...(plantas?.map((p) => ({ key: String(p.id), label: p.nombre })) ?? []),
        ]}
      />

      <Table<Declaracion>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        onRow={(record) => ({ onClick: () => setDeclaracionId(record.id) })}
        columns={[
          { title: "Número", dataIndex: "numero" },
          { title: "Fecha envío", dataIndex: "fecha_envio" },
          { title: "N° certificado", dataIndex: "numero_certificado" },
          { title: "Estado", dataIndex: "estado", render: (e: string) => <Tag color={ESTADO_COLOR[e]}>{e}</Tag> },
        ]}
      />

      <Drawer title={declaracion?.numero} width={480} open={!!declaracionId} onClose={() => setDeclaracionId(null)}>
        {declaracion && (
          <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Estado">
                <Tag color={ESTADO_COLOR[declaracion.estado]}>{declaracion.estado}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Fecha envío">{declaracion.fecha_envio}</Descriptions.Item>
              <Descriptions.Item label="Certificado">
                {declaracion.numero_certificado || "—"} {declaracion.fecha_certificacion && `(${declaracion.fecha_certificacion})`}
              </Descriptions.Item>
            </Descriptions>

            {puedeEditar && SIGUIENTE_ESTADO_DECLARACION[declaracion.estado]?.length > 0 && (
              <Card size="small" title="Cambiar estado" style={{ marginTop: 16 }}>
                <Space>
                  <Select
                    style={{ width: 180 }}
                    placeholder="Nuevo estado"
                    value={nuevoEstado}
                    onChange={setNuevoEstado}
                    options={SIGUIENTE_ESTADO_DECLARACION[declaracion.estado].map((e) => ({ value: e, label: e }))}
                  />
                  <Button type="primary" disabled={!nuevoEstado} onClick={() => cambiarEstado.mutate()}>
                    Confirmar
                  </Button>
                </Space>
              </Card>
            )}

            {puedeEditar && declaracion.estado === "enviada" && (
              <Card size="small" title="Certificar" style={{ marginTop: 16 }}>
                <Form form={certForm} layout="vertical" onFinish={(v) => certificar.mutate(v)}>
                  <Form.Item name="numero_certificado" label="Número de certificado" rules={[{ required: true }]}>
                    <Input />
                  </Form.Item>
                  <Form.Item name="fecha_certificacion" label="Fecha de certificación" rules={[{ required: true }]}>
                    <Input type="date" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" loading={certificar.isPending}>
                    Certificar
                  </Button>
                </Form>
              </Card>
            )}
          </>
        )}
      </Drawer>

      <Modal open={modalOpen} title="Nueva declaración" onCancel={() => setModalOpen(false)} onOk={() => form.submit()} confirmLoading={crear.isPending}>
        <Form form={form} layout="vertical" onFinish={(values) => crear.mutate(values)}>
          <Form.Item name="manifiesto_id" label="Manifiesto (estado: recibido)" rules={[{ required: true }]}>
            <Select options={manifiestos?.items.map((m) => ({ value: m.id, label: m.numero }))} />
          </Form.Item>
          <Form.Item name="planta_id" label="Planta certificadora" rules={[{ required: true }]}>
            <Select options={plantas?.map((p) => ({ value: p.id, label: p.nombre }))} />
          </Form.Item>
          <Form.Item name="fecha_envio" label="Fecha de envío">
            <Input type="date" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
