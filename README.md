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
Instala dependencias:

bash
Copiar código
pip install -r requirements.txt
Configura el archivo .env (ver sección siguiente).

Inicializa la base de datos (se crea automáticamente al correr).

Variables de Entorno
Crea un archivo .env en la raíz del proyecto:

env
Copiar código
MYSQL_URI=mysql+pymysql://usuario:contraseña@localhost/nombre_db  # Opcional; fallback a SQLite
JWT_SECRET_KEY=tu-clave-super-secreta-y-larga-minimo-32-caracteres-1234567890abcdef
MYSQL_URI: Conexión MySQL (si no, usa SQLite local: horarios_local.db).

JWT_SECRET_KEY: Clave secreta para JWT (genera una fuerte; expira tokens en 1h).

Cómo Correr en Dev
Asegúrate de que .env esté configurado.

Ejecuta el servidor:

bash
Copiar código
python app.py
Abre en el navegador: http://127.0.0.1:5000/

Login pre-rellenado: Email admin1234@ejemplo.com / Password 1234 (regístralo si no existe).

Dashboard: CRUD de horarios (admin: full; user: solo lectura).

Para producción: Usa Gunicorn/WSGI, configura HTTPS y mueve a un servidor real.

Cómo Ejecutar Pruebas
Instala pytest (ya en requirements.txt):

bash
Copiar código
pip install pytest
Ejecuta las pruebas mínimas (login válido/inválido, rutas protegidas):

bash
Copiar código
pytest tests/test_auth.py -v
Cubre: Registro/login, acceso con/sin token, roles.

Para pruebas manuales con curl, usa test_curls.txt (incluido en repo).

Roles
user (default): Puede listar horarios (GET /api/horarios y GET /api/horarios/<id>). No puede crear/actualizar/eliminar.

admin: Acceso completo (GET/POST/PUT/DELETE en horarios; gestión de users). Solo uno permitido (bloqueo en registro).

Asigna rol en registro (solo manual o vía checkbox en frontend).

Ejemplo de Tokens
Tokens JWT incluyen role en claims. Decodifícalos en jwt.io (pega el access_token).

Ejemplo Access Token (Admin):

Copiar código
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4iLCJzdWIiOiIxIiwiZXhwIjoxNzYwMjUwMTY1fQ.BisXJ4n7Sn_uHJTlLzCQREj_j53QE8kpKGJo09gkSNI
Decodificado: {"sub": "1", "role": "admin", "exp": 1760250165} (expira en 1h).

Ejemplo Refresh Token:

Copiar código
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzYyODM4NTY1fQ.tH2CGtPMAHtYIvUEQVM6bw4ub8yneOTwoV6s9FaeUtM
POST /api/refresh con Authorization: Bearer <refresh_token> → Nuevo access_token.

Flujo de Autenticación
Registro: POST /api/registry con {email, password, role?} (default 'user'). Hash de password y chequeo de admin único.

Login: POST /api/login con {email, password} → Devuelve access_token (1h) y refresh_token (14 días). Rol en claims.

Uso: Headers Authorization: Bearer <access_token> en rutas protegidas. @jwt_required() verifica token; role_required() chequea rol.

Refresh: POST /api/refresh con refresh_token → Nuevo access_token.

Logout: POST /api/logout → Invalida token en blacklist (memoria; prod: Redis).

Expiración: Access 1h; refresh 14d. Frontend guarda en localStorage y redirige post-login.

Tabla de Endpoints
Método	Endpoint	Descripción	Autenticación	Rol Requerido	Ejemplo de Body
POST	/api/registry	Registro de usuario	No	-	{"email": "test@test.com", "password": "pass", "role": "admin"}
POST	/api/login	Login y tokens JWT	No	-	{"email": "test@test.com", "password": "pass"}
POST	/api/refresh	Renovar access_token	Refresh Token	-	(Usa refresh en header)
POST	/api/logout	Cierre de sesión (invalida token)	Sí (JWT)	-	-
GET	/api/horarios	Lista todos los horarios	Sí (JWT)	user	-
GET	/api/horarios/<id>	Detalle de un horario	Sí (JWT)	user	-
POST	/api/horarios	Crear horario	Sí (JWT)	admin	{"dia": "Lunes", "hora_inicio": "08:00", "hora_fin": "10:00", "actividad": "Clase de Matemáticas"}
PUT	/api/horarios/<id>	Actualizar horario	Sí (JWT)	admin	Igual que POST
DELETE	/api/horarios/<id>	Eliminar horario	Sí (JWT)	admin	-
GET	/api/users	Lista usuarios (admin only)	Sí (JWT)	admin	-
GET	/api/users/<id>	Detalle usuario	Sí (JWT)	-	-
PUT	/api/users/<id>	Actualizar usuario	Sí (JWT)	admin	{"email": "new@test.com", "password": "newpass"}
DELETE	/api/users/<id>	Eliminar usuario	Sí (JWT)	admin	-

Notas: Todos los cuerpos son JSON. Errores comunes: 400 (datos inválidos), 401 (no autenticado), 403 (rol insuficiente), 404 (no encontrado).