import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, Typography, message } from "antd";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "@/api/auth";
import { useAuthStore } from "@/store/auth";

export default function Login() {
  const [loading, setLoading] = useState(false);
  const setSession = useAuthStore((s) => s.setSession);
  const navigate = useNavigate();

  async function onFinish(values: { email: string; password: string }) {
    setLoading(true);
    try {
      const data = await login(values.email, values.password);
      setSession(data.access_token, data.user);
      navigate("/");
    } catch {
      message.error("Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center", background: "#f0f5f0" }}>
      <Card style={{ width: 380 }}>
        <Typography.Title level={3} style={{ textAlign: "center", color: "#2e7d32" }}>
          Eco Global
        </Typography.Title>
        <Typography.Text type="secondary" style={{ display: "block", textAlign: "center", marginBottom: 24 }}>
          Sistema de Gestión Operativa
        </Typography.Text>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: "email" }]}>
            <Input prefix={<UserOutlined />} placeholder="usuario@ecoglobal.com" />
          </Form.Item>
          <Form.Item name="password" label="Contraseña" rules={[{ required: true }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="••••••••" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            Ingresar
          </Button>
        </Form>
      </Card>
    </div>
  );
}
