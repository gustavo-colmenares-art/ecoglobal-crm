import {
  BankOutlined,
  BellOutlined,
  DashboardOutlined,
  DeleteOutlined,
  DollarOutlined,
  FileTextOutlined,
  LogoutOutlined,
  SettingOutlined,
  TeamOutlined,
  WalletOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Avatar, Badge, Breadcrumb, Dropdown, Layout, Menu, Popover, Tag, Typography } from "antd";
import { useMemo } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

import { api } from "@/api/client";
import { useAuthStore } from "@/store/auth";
import type { APIResponse } from "@/types";

const { Header, Sider, Content } = Layout;

const MENU_ITEMS = [
  { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "/clientes", icon: <TeamOutlined />, label: "Clientes" },
  { key: "/servicios", icon: <FileTextOutlined />, label: "Servicios" },
  { key: "/manifiestos", icon: <DeleteOutlined />, label: "Manifiestos" },
  { key: "/declaraciones", icon: <BankOutlined />, label: "Declaraciones" },
  { key: "/facturacion", icon: <DollarOutlined />, label: "Facturación" },
  { key: "/cartera", icon: <WalletOutlined />, label: "Cartera" },
];

interface AlertasResumen {
  manifiestos_demorados: unknown[];
  declaraciones_sin_certificar: unknown[];
  facturas_por_vencer: unknown[];
  facturas_vencidas: unknown[];
}

export default function AppLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = useMemo(() => {
    const items = [...MENU_ITEMS];
    if (user?.rol?.nombre === "superadmin") {
      items.push({ key: "/configuracion", icon: <SettingOutlined />, label: "Configuración" });
    }
    return items;
  }, [user]);

  const { data: alertas } = useQuery({
    queryKey: ["dashboard", "alertas"],
    queryFn: async () => {
      const { data } = await api.get<APIResponse<AlertasResumen>>("/dashboard/alertas");
      return data.data;
    },
    refetchInterval: 2 * 60 * 1000,
  });

  const totalAlertas = alertas
    ? alertas.manifiestos_demorados.length +
      alertas.declaraciones_sin_certificar.length +
      alertas.facturas_por_vencer.length +
      alertas.facturas_vencidas.length
    : 0;

  const breadcrumbLabel = MENU_ITEMS.find((i) => i.key === location.pathname)?.label ?? "Configuración";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ color: "#fff", textAlign: "center", padding: 16, fontWeight: 700, fontSize: 18 }}>
          Eco Global
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 16, padding: "0 24px" }}>
          <Popover
            title="Alertas"
            content={
              <div style={{ maxWidth: 260 }}>
                <div>Manifiestos demorados: {alertas?.manifiestos_demorados.length ?? 0}</div>
                <div>Declaraciones sin certificar: {alertas?.declaraciones_sin_certificar.length ?? 0}</div>
                <div>Facturas por vencer: {alertas?.facturas_por_vencer.length ?? 0}</div>
                <div>Facturas vencidas: {alertas?.facturas_vencidas.length ?? 0}</div>
              </div>
            }
          >
            <Badge count={totalAlertas} size="small">
              <BellOutlined style={{ fontSize: 18, cursor: "pointer" }} />
            </Badge>
          </Popover>
          <Dropdown
            menu={{
              items: [{ key: "logout", icon: <LogoutOutlined />, label: "Cerrar sesión" }],
              onClick: () => {
                logout();
                navigate("/login");
              },
            }}
          >
            <span style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
              <Avatar size="small">{user?.nombre?.[0]?.toUpperCase()}</Avatar>
              <Typography.Text>{user?.nombre}</Typography.Text>
              {user?.rol && <Tag color="green">{user.rol.nombre}</Tag>}
            </span>
          </Dropdown>
        </Header>
        <Content style={{ margin: "16px" }}>
          <Breadcrumb items={[{ title: "EcoGlobal" }, { title: breadcrumbLabel }]} style={{ marginBottom: 16 }} />
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
