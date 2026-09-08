import { api } from "@/api/client";

export async function abrirPdf(path: string) {
  const nuevaVentana = window.open("", "_blank");
  try {
    const { data } = await api.get(path, { responseType: "blob" });
    const url = URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
    if (nuevaVentana) {
      nuevaVentana.location.href = url;
    }
  } catch (e) {
    nuevaVentana?.close();
    throw e;
  }
}
