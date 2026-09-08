import {
  DollarCircleOutlined,
  ExclamationCircleOutlined,
  FileDoneOutlined,
  TeamOutlined,
  TruckOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Alert, Card, Col, Empty, List, Row, Skeleton, Statistic, Tag } from "antd";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { getDashboardAlertas, getDashboardFlujo, getDashboardGeneral, getServiciosDashboard } from "@/api/dashboard";

const ETAPA_LABELS: Record<string, string> = {
  cotizado: "Cotizado",
  confirmado: "Confirmado",
  programado: "Programado",
  en_ruta: "En ruta",
  atendido: "Atendido",
  manifiesto_pendiente: "Manif. pendiente",
  manifiesto_recibido: "Manif. recibido",
  completado: "Completado",
  cancelado: "Cancelado",
};

const MES_LABELS = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

const formatCOP = (valor: number) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(valor);

export default function Dashboard() {
  const { data: general, isLoading: loadingGeneral } = useQuery({
    queryKey: ["dashboard", "general"],
    queryFn: getDashboardGeneral,
  });
  const { data: flujo, isLoading: loadingFlujo } = useQuery({
    queryKey: ["dashboard", "flujo"],
    queryFn: getDashboardFlujo,
  });
  const { data: alertas, isLoading: loadingAlertas } = useQuery({
    queryKey: ["dashboard", "alertas-full"],
    queryFn: getDashboardAlertas,
    refetchInterval: 2 * 60 * 1000,
  });
  const { data: serviciosDash } = useQuery({
    queryKey: ["servicios", "dashboard"],
    queryFn: getServiciosDashboard,
  });

  const chartData = MES_LABELS.slice(1).map((label, idx) => ({
    mes: label,
    servicios: serviciosDash?.por_mes[String(idx + 1)] ?? 0,
  }));

  const alertasFlat = alertas
    ? [
        ...alertas.manifiestos_demorados.map((a) => ({ ...a, tipo: "Manifiesto demorado", color: "orange" })),
        ...alertas.declaraciones_sin_certificar.map((a) => ({ ...a, tipo: "Declaración sin certificar", color: "gold" })),
        ...alertas.facturas_por_vencer.map((a) => ({ ...a, tipo: "Factura por vencer", color: "blue" })),
        ...alertas.facturas_vencidas.map((a) => ({ ...a, tipo: "Factura vencida", color: "red" })),
      ]
    : [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <Row gutter={16}>
        <Col xs={24} sm={12} md={8} lg={5}>
          <Card>
            <Skeleton loading={loadingGeneral} active paragraph={false}>
              <Statistic title="Clientes activos" value={general?.total_clientes} prefix={<TeamOutlined />} />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={5}>
          <Card>
            <Skeleton loading={loadingGeneral} active paragraph={false}>
              <Statistic title="Servicios activos" value={general?.servicios_activos} prefix={<FileDoneOutlined />} />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={5}>
          <Card>
            <Skeleton loading={loadingGeneral} active paragraph={false}>
              <Statistic title="Manifiestos en campo" value={general?.manifiestos_en_campo} prefix={<TruckOutlined />} />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={5}>
          <Card>
            <Skeleton loading={loadingGeneral} active paragraph={false}>
              <Statistic
                title="Facturas vencidas"
                value={general?.facturas_vencidas}
                valueStyle={{ color: (general?.facturas_vencidas ?? 0) > 0 ? "#cf1322" : undefined }}
                prefix={<ExclamationCircleOutlined />}
              />
            </Skeleton>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={4}>
          <Card>
            <Skeleton loading={loadingGeneral} active paragraph={false}>
              <Statistic
                title="Cartera total"
                value={general ? formatCOP(general.cartera_total) : undefined}
                prefix={<DollarCircleOutlined />}
              />
            </Skeleton>
          </Card>
        </Col>
      </Row>

      <Card title="Pipeline de servicios">
        <Skeleton loading={loadingFlujo} active>
          <Row gutter={[12, 12]}>
            {flujo?.map((etapa) => (
              <Col key={etapa.estado} xs={12} sm={8} md={6} lg={3}>
                <Card size="small" style={{ textAlign: "center" }}>
                  <Statistic title={ETAPA_LABELS[etapa.estado] ?? etapa.estado} value={etapa.cantidad} />
                </Card>
              </Col>
            ))}
          </Row>
        </Skeleton>
      </Card>

      <Card title="Servicios por mes">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mes" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="servicios" fill="#2e7d32" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card title="Alertas">
        <Skeleton loading={loadingAlertas} active>
          {alertasFlat.length === 0 ? (
            <Empty description="Sin alertas activas" />
          ) : (
            <List
              dataSource={alertasFlat}
              renderItem={(item) => (
                <List.Item>
                  <Tag color={item.color}>{item.tipo}</Tag>
                  <span>{item.numero}</span>
                  {item.total != null && <span style={{ marginLeft: "auto" }}>{formatCOP(item.total)}</span>}
                </List.Item>
              )}
            />
          )}
          {(alertas?.facturas_vencidas.length ?? 0) > 0 && (
            <Alert
              style={{ marginTop: 12 }}
              type="error"
              showIcon
              message={`${alertas?.facturas_vencidas.length} factura(s) vencida(s) requieren gestión de cobro`}
            />
          )}
        </Skeleton>
      </Card>
    </div>
  );
}
