# Guía: subir Ecoglobal a GitHub y Supabase

Este documento resume, paso a paso, cómo publicar el código en GitHub y migrar la base de datos a Supabase.

## Estado actual
- Repositorio Git local ya inicializado en `C:\Users\USER\Desktop\ecoglobal` (`git init` hecho).
- `.gitignore` ya excluye `.env`, `node_modules/`, `__pycache__/`, `whatsapp-bridge/auth-session/`, etc. — las claves no se suben.
- Aún NO hay commit, NO hay repo remoto en GitHub, y la base de datos sigue siendo el Postgres local de Docker (no Supabase).

---

## Parte A — Configurar tu identidad de Git (una sola vez, en tu PC)

Abre **PowerShell** y ejecuta (cambia el nombre y el correo por los tuyos):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
```

Esto le dice a Git quién eres para firmar los commits. Solo se hace una vez por computador.

---

## Parte B — Subir el código a GitHub

### 1. Crear el repositorio en GitHub (lo haces tú, en el navegador)
1. Entra a https://github.com y crea una cuenta si no tienes.
2. Click en **"New repository"** (botón verde, arriba a la derecha).
3. Nombre sugerido: `ecoglobal`. Puede ser **privado** (recomendado, porque el código incluye lógica de negocio).
4. **No marques** "Add a README" ni ".gitignore" (ya los tenemos localmente).
5. Click **"Create repository"**. GitHub te mostrará una URL como:
   `https://github.com/TU-USUARIO/ecoglobal.git`
   Copia esa URL.

### 2. Hacer el primer commit (dímelo y lo hago yo, o hazlo tú)
En PowerShell, dentro de la carpeta del proyecto:

```bash
cd "C:\Users\USER\Desktop\ecoglobal"
git add .
git commit -m "Primer commit: base del sistema Ecoglobal"
```

### 3. Conectar con GitHub y subir
Reemplaza la URL por la que copiaste en el paso 1:

```bash
git remote add origin https://github.com/TU-USUARIO/ecoglobal.git
git branch -M main
git push -u origin main
```

Al ejecutar `git push`, Windows abrirá una ventana del navegador para que inicies sesión en GitHub (Git Credential Manager). Solo la primera vez.

---

## Parte C — Migrar la base de datos a Supabase

### 1. Crear el proyecto (lo haces tú, en el navegador)
1. Entra a https://supabase.com y crea una cuenta / inicia sesión.
2. Click **"New project"**.
3. Elige nombre, contraseña de base de datos (guárdala bien) y región (la más cercana, ej. `South America (São Paulo)`).
4. Espera 1-2 minutos a que se aprovisione.

### 2. Obtener la cadena de conexión
1. Dentro del proyecto: **Project Settings → Database → Connection string**.
2. Copia la que dice **"URI"** (modo *Session pooler* o *Direct connection*, ambas sirven para empezar). Se ve así:
   `postgresql://postgres:[TU-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres`

### 3. Actualizar el `.env` del backend
Edita `C:\Users\USER\Desktop\ecoglobal\.env` y cambia la línea `DATABASE_URL` por la de Supabase, ajustando el driver a `psycopg` (que ya usa el proyecto):

```
DATABASE_URL=postgresql+psycopg://postgres:[TU-PASSWORD]@db.xxxxxxxx.supabase.co:5432/postgres
```

Pásame la cadena (puedes ocultar la contraseña y dármela aparte) y te edito el archivo yo mismo si prefieres no tocarlo a mano.

### 4. Correr las migraciones contra Supabase
Con el `.env` ya apuntando a Supabase:

```bash
cd "C:\Users\USER\Desktop\ecoglobal\backend"
alembic upgrade head
```

Esto crea las 16 tablas del esquema en la base de datos de Supabase. Si usan `seed.py` para datos de prueba:

```bash
python seed.py
```

### 5. Verificar
Entra a Supabase → **Table Editor** y confirma que aparecen las tablas (users, servicios, manifiestos, etc.).

---

## Qué puedo hacer yo directamente vs. qué tienes que hacer tú

| Tarea | Quién la hace |
|---|---|
| `git init`, `git add`, `git commit` | Yo (ya hice `git init`) |
| Crear cuenta y repo en GitHub | Tú (necesita tu login) |
| `git push` (autenticación) | Se hace junto — yo corro el comando, tú inicias sesión en la ventana del navegador |
| Crear cuenta y proyecto en Supabase | Tú (necesita tu login) |
| Copiar la cadena de conexión | Tú |
| Editar `.env`, correr migraciones (`alembic upgrade head`) | Yo, si me confirmas que ya tienes la cadena |

---

## Notas de seguridad
- Nunca subas el archivo `.env` real a GitHub (ya está protegido por `.gitignore`, no lo elimines de ahí).
- Guarda la contraseña de la base de datos de Supabase en un lugar seguro (gestor de contraseñas), no en el chat de forma permanente.
- Si el repo de GitHub va a tener colaboradores, usa el repo **privado** y agrégalos desde **Settings → Collaborators**.
