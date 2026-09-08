// Puente WhatsApp Web -> backend EcoGlobal (Leads).
// Escucha mensajes entrantes de WhatsApp y los reenvia al endpoint
// /api/v1/leads/whatsapp-webhook del backend FastAPI.

const {
  default: makeWASocket,
  DisconnectReason,
  useMultiFileAuthState,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");
const qrcode = require("qrcode-terminal");
const pino = require("pino");
const path = require("path");

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
const WEBHOOK_TOKEN = process.env.WHATSAPP_WEBHOOK_TOKEN || "";
const AUTH_DIR = path.join(__dirname, "auth-session");

if (!WEBHOOK_TOKEN) {
  console.error("[whatsapp-bridge] Falta WHATSAPP_WEBHOOK_TOKEN en el entorno.");
  process.exit(1);
}

async function enviarLead(telefono, nombre, texto) {
  const url = `${BACKEND_URL}/api/v1/leads/whatsapp-webhook`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Webhook-Token": WEBHOOK_TOKEN,
      },
      body: JSON.stringify({ telefono, nombre_contacto: nombre, texto }),
    });
    if (!res.ok) {
      const body = await res.text();
      console.error(`[whatsapp-bridge] backend respondio ${res.status}: ${body}`);
    } else {
      console.log(`[whatsapp-bridge] lead registrado: ${telefono}`);
    }
  } catch (err) {
    console.error(`[whatsapp-bridge] error llamando al backend: ${err.message}`);
  }
}

async function iniciar() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }),
    printQRInTerminal: false,
  });

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("\n[whatsapp-bridge] Escanea este codigo QR desde WhatsApp (Dispositivos vinculados > Vincular un dispositivo):\n");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "close") {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const debeReconectar = statusCode !== DisconnectReason.loggedOut;
      console.log(`[whatsapp-bridge] conexion cerrada (codigo ${statusCode}). Reconectar: ${debeReconectar}`);
      if (debeReconectar) {
        setTimeout(iniciar, 3000);
      } else {
        console.error("[whatsapp-bridge] sesion cerrada (logout). Borra auth-session/ y vuelve a escanear el QR.");
      }
    } else if (connection === "open") {
      console.log("[whatsapp-bridge] conectado a WhatsApp correctamente.");
    }
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;
    for (const msg of messages) {
      if (!msg.message || msg.key.fromMe) continue;
      const jid = msg.key.remoteJid || "";
      if (jid.endsWith("@g.us") || jid === "status@broadcast") continue; // ignorar grupos y estados

      const texto =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text ||
        msg.message.imageMessage?.caption ||
        msg.message.videoMessage?.caption ||
        null;
      if (!texto) continue; // ignorar audios/stickers/etc sin texto por ahora

      const telefono = jid.replace("@s.whatsapp.net", "");
      const nombre = msg.pushName || null;
      await enviarLead(telefono, nombre, texto);
    }
  });
}

iniciar().catch((err) => {
  console.error("[whatsapp-bridge] error fatal al iniciar:", err);
  process.exit(1);
});
