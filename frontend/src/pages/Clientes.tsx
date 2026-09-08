import { PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Drawer, Form, Input, List, Modal, Space, Switch, Table, Tag, message } from "antd";
import { useState } from "react";

import { actualizarCliente, crearCliente, listarClientes, serviciosDeCliente, type ClienteInput } from "@/api/clientes";
import { useAuthStore } from "@/store/auth";
import type { Cliente } from "@/types";

export default function Clientes() {
  const [filtros, setFiltros] = useState<{ nombre?: string; nit?: string; ciudad?: string }>({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<Cliente | null>(null);
  const [drawerCliente, setDrawerCliente] = useState<Cliente | null>(null);
  const [form] = Form.useForm<ClienteInput>();
  const queryClient = useQueryClient();
  const rol = useAuthStore((s) => s.user?.rol?.nombre);
  const puedeEditar = rol === "superadmin" || rol === "comercial";

  const { data, isLoading } = useQuery({
    queryKey: ["clientes", filtros],
    queryFn: () => listarClientes({ ...filtros, page: 1 }),
  });

  const { data: serviciosCliente } = useQuery({
    queryKey: ["clientes", drawerCliente?.id, "servicios"],
    queryFn: () => serviciosDeCliente(drawerCliente!.id),
    enabled: !!drawerCliente,
  });

  const guardar = useMutation({
    mutationFn: (values: ClienteInput) =>
      editando ? actualizarCliente(editando.id, values) : crearCliente(values),
    onSuccess: () => {
      message.success(editando ? "Cliente actualizado" : "Cliente creado");
      queryClient.invalidateQueries({ queryKey: ["clientes"] });
      setModalOpen(false);
      setEditando(null);
      form.resetFields();
    },
    onError: () => message.error("No se pudo guardar el cliente"),
  });

  const toggleActivo = useMutation({
    mutationFn: (cliente: Cliente) => actualizarCliente(cliente.id, { activo: !cliente.activo }),
    onSuccess: () => {
      message.success("Estado del cliente actualizado");
      queryClient.invalidateQueries({ queryKey: ["clientes"] });
    },
    onError: () => message.error("No se pudo actualizar el estado"),
  });

  function abrirCrear() {
    setEditando(null);
    form.resetFields();
    setModalOpen(true);
  }

  function abrirEditar(cliente: Cliente) {
    setEditando(cliente);
    form.setFieldsValue(cliente);
    setModalOpen(true);
  }

  return (
    <Card
      title="Clientes"
      extra={
        puedeEditar && (
          <Button type="primary" icon={<PlusOutlined />} onClick={abrirCrear}>
            Nuevo cliente
          </Button>
        )
      }
    >
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search
          placeholder="Buscar por razón social"
          allowClear
          style={{ width: 220 }}
          onSearch={(v) => setFiltros((f) => ({ ...f, nombre: v || undefined }))}
        />
        <Input.Search
          placeholder="NIT"
          allowClear
          style={{ width: 160 }}
          onSearch={(v) => setFiltros((f) => ({ ...f, nit: v || undefined }))}
        />
        <Input.Search
          placeholder="Ciudad"
          allowClear
          style={{ width: 160 }}
          onSearch={(v) => setFiltros((f) => ({ ...f, ciudad: v || undefined }))}
        />
      </Space>

      <Table<Cliente>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items}
        pagination={{ total: data?.total, pageSize: 20 }}
        onRow={(record) => ({ onClick: () => setDrawerCliente(record) })}
        columns={[
          { title: "Razón social", dataIndex: "razon_social" },
          { title: "NIT", dataIndex: "nit" },
          { title: "Ciudad", dataIndex: "ciudad" },
          { title: "Contacto", dataIndex: "contacto_nombre" },
          { title: "Teléfono", dataIndex: "telefono" },
          puedeEditar
            ? {
                title: "Estado",
                dataIndex: "activo",
                render: (activo: boolean, record: Cliente) => (
                  <Switch
                    checked={activo}
                    checkedChildren="Activo"
                    unCheckedChildren="Inactivo"
                    loading={toggleActivo.isPending}
                    onClick={(_, e) => e.stopPropagation()}
                    onChange={() => toggleActivo.mutate(record)}
                  />
                ),
              }
            : {
                title: "Estado",
                dataIndex: "activo",
                render: (activo: boolean) => <Tag color={activo ? "green" : "red"}>{activo ? "Activo" : "Inactivo"}</Tag>,
              },
          ...(puedeEditar
            ? [
                {
                  title: "",
                  render: (_: unknown, record: Cliente) => (
                    <Button
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        abrirEditar(record);
                      }}
                    >
                      Editar
                    </Button>
                  ),
                },
              ]
            : []),
        ]}
      />

      <Modal
        title={editando ? "Editar cliente" : "Nuevo cliente"}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={guardar.isPending}
      >
        <Form form={form} layout="vertical" onFinish={(values) => guardar.mutate(values)}>
          <Form.Item name="razon_social" label="Razón social" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="nit" label="NIT" rules={[{ required: true }]}>
            <Input disabled={!!editando} />
          </Form.Item>
          <Form.Item name="direccion" label="Dirección">
            <Input />
          </Form.Item>
          <Space>
            <Form.Item name="ciudad" label="Ciudad">
              <Input />
            </Form.Item>
            <Form.Item name="departamento" label="Departamento">
              <Input />
            </Form.Item>
          </Space>
          <Space>
            <Form.Item name="telefono" label="Teléfono">
              <Input />
            </Form.Item>
            <Form.Item name="email" label="Email">
              <Input />
            </Form.Item>
          </Space>
          <Space>
            <Form.Item name="contacto_nombre" label="Contacto">
              <Input />
            </Form.Item>
            <Form.Item name="contacto_cargo" label="Cargo">
              <Input />
            </Form.Item>
          </Space>
        </Form>
      </Modal>

      <Drawer title={drawerCliente?.razon_social} open={!!drawerCliente} onClose={() => setDrawerCliente(null)} width={420}>
        <p>NIT: {drawerCliente?.nit}</p>
        <p>
          {drawerCliente?.direccion} — {drawerCliente?.ciudad}
        </p>
        <h4>Historial de servicios</h4>
        <List
          dataSource={serviciosCliente}
          renderItem={(s) => (
            <List.Item>
              <span>{s.numero}</span>
              <Tag style={{ marginLeft: "auto" }}>{s.estado}</Tag>
            </List.Item>
          )}
        />
      </Drawer>
    </Card>
  );
}
