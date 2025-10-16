# API Horarios con Autenticación JWT

## Descripción
Esta API Flask gestiona un CRUD completo para horarios, con autenticación segura vía JWT, hashing de contraseñas (bcrypt) y autorización por roles (user/admin). Incluye un frontend simple en HTML/JS para login, registro y gestión condicional por rol. El login redirige automáticamente al dashboard, donde users solo pueden listar horarios y admins gestionan todo.

Tecnologías: Flask, SQLAlchemy, Flask-JWT-Extended, bcrypt, SQLite/MySQL fallback.

## Instalación
1. Haz un fork del repositorio en GitHub: Ve a tu repo y cópialo a tu cuenta.

2. Crea un entorno virtual (opcional, recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate
   # En Windows: venv\Scripts\activate
3.Instala dependencias:
pip install -r requirements.txt
4.Configura el archivo .env (ver sección siguiente).

5. Inicializa la base de datos (se crea automáticamente al correr).
## Variables de Entorno

Crea un archivo .env en la raíz del proyecto:

MYSQL_URI=mysql+pymysql://usuario:contraseña@localhost/nombre_db  # Opcional; fallback a SQLite
JWT_SECRET_KEY=tu-clave-super-secreta-y-larga-minimo-32-caracteres-1234567890abcdef

MYSQL_URI: Conexión MySQL (si no, usa SQLite local: horarios_local.db).
JWT_SECRET_KEY: Clave secreta para JWT (genera una fuerte; expira tokens en 1h

## Cómo Correr en Dev

1. Asegúrate de que .env esté configurado.
2. Ejecuta el servidor:

python app.py
3. Abre en el navegador: http://127.0.0.1:5000/

Login pre-rellenado: Email admin1234@ejemplo.com / Password 1234 (regístralo si no existe).

Dashboard: CRUD de horarios (admin: full; user: solo lectura).

Para producción: Usa Gunicorn/WSGI, configura HTTPS y mueve a un servidor real.

## Cómo Ejecutar Pruebas
1. Cómo Ejecutar Pruebas

 pip install pytest

2. Ejecuta las pruebas mínimas (login válido/inválido, rutas protegidas):
Cubre: Registro/login, acceso con/sin token, roles.

3. Para pruebas manuales con curl, usa test_curls.txt (incluido en repo).

## Roles

user (default): Puede listar horarios (GET /api/horarios y GET /api/horarios/<id>). No puede crear/actualizar/eliminar.

admin: Acceso completo (GET/POST/PUT/DELETE en horarios; gestión de users). Solo uno permitido (bloqueo en registro).

Asigna rol en registro (solo manual o vía checkbox en frontend).

## Ejemplo de Tokens

Tokens JWT incluyen role en claims. Decodifícalos en jwt.io (pega el access_token).

## Ejemplo Access Token (Admin):

Decodificado: {"sub": "1", "role": "admin", "exp": 1760250165} (expira en 1h).

Ejemplo Refresh Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzYyODM4NTY1fQ.tH2CGtPMAHtYIvUEQVM6bw4ub8yneOTwoV6s9FaeUtM


