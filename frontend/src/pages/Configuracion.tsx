import { PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Form, Input, Modal, Select, Switch, Table, Tabs, Tag, message } from "antd";
import { useState } from "react";

import {
  actualizarPlanta,
  actualizarResiduo,
  actualizarUsuario,
  crearPlanta,
  crearResiduo,
  crearUsuario,
  listarPlantas,
  listarResiduos,
  listarRoles,
  listarUsuarios,
  type UsuarioInput,
} from "@/api/maestros";
import type { Planta, TipoResiduo, Usuario } from "@/types";

function UsuariosTab() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({ queryKey: ["usuarios"], queryFn: () => listarUsuarios(1) });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: listarRoles });

  const guardar = useMutation({
    mutationFn: (values: UsuarioInput) =>
      editando ? actualizarUsuario(editando.id, values) : crearUsuario(values),
    onSuccess: () => {
      message.success("Usuario guardado");
      queryClient.invalidateQueries({ queryKey: ["usuarios"] });
      setModalOpen(false);
      setEditando(null);
      form.resetFields();
    },
    onError: () => message.error("No se pudo guardar el usuario"),
  });

  const toggleActivo = useMutation({
    mutationFn: (u: Usuario) => actualizarUsuario(u.id, { activo: !u.activo }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["usuarios"] }),
  });

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => {
          setEditando(null);
          form.resetFields();
          setModalOpen(true);
        }}
      >
        Nuevo usuario
      </Button>
      <Table<Usuario>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        columns={[
          { title: "Nombre", dataIndex: "nombre" },
          { title: "Email", dataIndex: "email" },
          { title: "Rol", dataIndex: ["rol", "nombre"], render: (r: string) => <Tag>{r}</Tag> },
          {
            title: "Activo",
            dataIndex: "activo",
            render: (activo: boolean, record) => (
              <Switch checked={activo} onChange={() => toggleActivo.mutate(record)} />
            ),
          },
          {
            title: "",
            render: (_: unknown, record: Usuario) => (
              <Button
                size="small"
                onClick={() => {
                  setEditando(record);
                  form.setFieldsValue({ nombre: record.nombre, email: record.email, rol_id: record.rol?.id });
                  setModalOpen(true);
                }}
              >
                Editar
              </Button>
            ),
          },
        ]}
      />
      <Modal
        open={modalOpen}
        title={editando ? "Editar usuario" : "Nuevo usuario"}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={guardar.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => guardar.mutate(values)}>
          <Form.Item name="nombre" label="Nombre" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: "email" }]}>
            <Input disabled={!!editando} />
          </Form.Item>
          {!editando && (
            <Form.Item name="password" label="Contraseña" rules={[{ required: true }]}>
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="rol_id" label="Rol" rules={[{ required: true }]}>
            <Select options={roles?.map((r) => ({ value: r.id, label: r.nombre }))} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}

function ResiduosTab() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<TipoResiduo | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["residuos"], queryFn: listarResiduos });

  const guardar = useMutation({
    mutationFn: (values: Partial<TipoResiduo>) =>
      editando ? actualizarResiduo(editando.id, values) : crearResiduo(values),
    onSuccess: () => {
      message.success("Tipo de residuo guardado");
      queryClient.invalidateQueries({ queryKey: ["residuos"] });
      setModalOpen(false);
      setEditando(null);
      form.resetFields();
    },
    onError: () => message.error("No se pudo guardar"),
  });

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => {
          setEditando(null);
          form.resetFields();
          setModalOpen(true);
        }}
      >
        Nuevo tipo de residuo
      </Button>
      <Table<TipoResiduo>
        rowKey="id"
        loading={isLoading}
        dataSource={data}
        columns={[
          { title: "Código", dataIndex: "codigo" },
          { title: "Nombre", dataIndex: "nombre" },
          { title: "Unidad", dataIndex: "unidad_medida" },
          { title: "Peligroso", dataIndex: "peligroso", render: (p: boolean) => (p ? <Tag color="red">Sí</Tag> : "No") },
          {
            title: "",
            render: (_: unknown, record: TipoResiduo) => (
              <Button
                size="small"
                onClick={() => {
                  setEditando(record);
                  form.setFieldsValue(record);
                  setModalOpen(true);
                }}
              >
                Editar
              </Button>
            ),
          },
        ]}
      />
      <Modal
        open={modalOpen}
        title={editando ? "Editar tipo de residuo" : "Nuevo tipo de residuo"}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={guardar.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => guardar.mutate(values)}>
          <Form.Item name="codigo" label="Código" rules={[{ required: true }]}>
            <Input disabled={!!editando} />
          </Form.Item>
          <Form.Item name="nombre" label="Nombre" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="unidad_medida" label="Unidad de medida" initialValue="kg">
            <Select options={["kg", "ton", "litros", "unidad"].map((u) => ({ value: u, label: u }))} />
          </Form.Item>
          <Form.Item name="peligroso" label="Peligroso" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}

function PlantasTab() {
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<Planta | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["plantas"], queryFn: listarPlantas });

  const guardar = useMutation({
    mutationFn: (values: Partial<Planta>) =>
      editando ? actualizarPlanta(editando.id, values) : crearPlanta(values),
    onSuccess: () => {
      message.success("Planta guardada");
      queryClient.invalidateQueries({ queryKey: ["plantas"] });
      setModalOpen(false);
      setEditando(null);
      form.resetFields();
    },
    onError: () => message.error("No se pudo guardar"),
  });

  return (
    <>
      <Button
        type="primary"
        icon={<PlusOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => {
          setEditando(null);
          form.resetFields();
          setModalOpen(true);
        }}
      >
        Nueva planta
      </Button>
      <Table<Planta>
        rowKey="id"
        loading={isLoading}
        dataSource={data}
        columns={[
          { title: "Nombre", dataIndex: "nombre" },
          { title: "NIT", dataIndex: "nit" },
          { title: "Ciudad", dataIndex: "ciudad" },
          { title: "Contacto", dataIndex: "contacto" },
          {
            title: "",
            render: (_: unknown, record: Planta) => (
              <Button
                size="small"
                onClick={() => {
                  setEditando(record);
                  form.setFieldsValue(record);
                  setModalOpen(true);
                }}
              >
                Editar
              </Button>
            ),
          },
        ]}
      />
      <Modal
        open={modalOpen}
        title={editando ? "Editar planta" : "Nueva planta"}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={guardar.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => guardar.mutate(values)}>
          <Form.Item name="nombre" label="Nombre" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="nit" label="NIT">
            <Input />
          </Form.Item>
          <Form.Item name="direccion" label="Dirección">
            <Input />
          </Form.Item>
          <Form.Item name="ciudad" label="Ciudad">
            <Input />
          </Form.Item>
          <Form.Item name="contacto" label="Contacto">
            <Input />
          </Form.Item>
          <Form.Item name="telefono" label="Teléfono">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}

export default function Configuracion() {
  return (
    <Card title="Configuración">
      <Tabs
        items={[
          { key: "usuarios", label: "Usuarios y roles", children: <UsuariosTab /> },
          { key: "residuos", label: "Tipos de residuo", children: <ResiduosTab /> },
          { key: "plantas", label: "Plantas certificadoras", children: <PlantasTab /> },
        ]}
      />
    </Card>
  );
}
