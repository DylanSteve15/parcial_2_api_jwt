# 🕒 API Horarios con Autenticación JWT

## 📘 Descripción
Esta API Flask gestiona un **CRUD completo para los horarios**, con **autenticación segura vía JWT**, **hashing de contraseñas (bcrypt)** y **autorización por roles (admin/usuario)**.  
Incluye endpoints protegidos para la gestión de usuarios y horarios, donde los **usuarios normales pueden consultar** y los **administradores pueden crear, modificar y eliminar** horarios.

**Tecnologías utilizadas:**  
Flask, SQLAlchemy, Flask-JWT-Extended, bcrypt, MySQL/SQLite (fallback automático).

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/flask_horarios_api.git
cd flask_horarios_api
2️⃣ Crear entorno virtual (opcional pero recomendado)
bash
Copiar código
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
3️⃣ Instalar dependencias
bash
Copiar código
pip install -r requirements.txt
4️⃣ Configurar el archivo .env
Crea un archivo llamado .env en la raíz del proyecto:

bash
Copiar código
MYSQL_URI=mysql+pymysql://usuario:contraseña@localhost/horarios_db  # Opcional, usa SQLite si no está disponible
JWT_SECRET_KEY=clave-super-secreta-y-larga-para-tokens-1234567890abcdef
MYSQL_URI: conexión MySQL (usa SQLite por defecto: horarios_local.db).

JWT_SECRET_KEY: clave secreta para generar los tokens JWT (mínimo 32 caracteres).

▶️ Cómo Ejecutar el Proyecto
1️⃣ Asegúrate de tener el .env configurado correctamente
2️⃣ Ejecuta el servidor
bash
Copiar código
python app.py
3️⃣ Abre en el navegador:
👉 http://127.0.0.1:5000/

Login de prueba:
Usuario: admin@ejemplo.com
Contraseña: 1234 (regístralo si no existe)

Dashboard:

Usuarios: solo pueden consultar horarios

Administradores: pueden crear, editar o eliminar horarios

⚠️ En producción usa Gunicorn o WSGI, configura HTTPS y despliega en un servidor seguro.

🧩 Estructura del Proyecto
markdown
Copiar código
flask_horarios_api/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
│
├── models/
│   ├── __init__.py
│   ├── user_model.py
│   └── horario_model.py
│
├── controllers/
│   ├── __init__.py
│   └── horario_controller.py
│
├── routes/
│   ├── __init__.py
│   ├── horario_routes.py
│   └── auth_routes.py
│
├── utils/
│   ├── __init__.py
│   └── auth_middleware.py
│
└── tests/
    └── test_auth.py
🔐 Flujo de Autenticación
Paso	Descripción	Endpoint
Registro	Crea un nuevo usuario con email, password y rol (por defecto usuario)	POST /api/registro
Login	Devuelve access_token (1h) y refresh_token (14 días)	POST /api/login
Autenticación	Rutas protegidas requieren Authorization: Bearer <token>	-
Refrescar token	Renueva el access_token cuando expira	POST /api/refresh
Logout	Invalida el token actual (blacklist temporal)	POST /api/logout

🧠 Roles y Permisos
Rol	Descripción	Acceso
usuario	Solo lectura	Consultar horarios
admin	Control total	Crear, actualizar, eliminar y consultar horarios

Solo un administrador inicial puede existir. Los siguientes registros serán usuarios normales.

🧾 Tabla de Endpoints
Método	Endpoint	Descripción	Autenticación	Rol Requerido	Ejemplo de Body
POST	/api/registro	Registro de usuario	No	-	{"email": "test@test.com", "password": "1234", "role": "admin"}
POST	/api/login	Login de usuario	No	-	{"email": "test@test.com", "password": "1234"}
POST	/api/refresh	Renueva el token JWT	Refresh	-	-
POST	/api/logout	Cierra sesión e invalida token	Sí	-	-
GET	/api/horarios	Lista todos los horarios	Sí	usuario	-
GET	/api/horarios/<id>	Detalle de horario	Sí	usuario	-
POST	/api/horarios	Crea un nuevo horario	Sí	admin	{"materia": "Cálculo", "dia": "Lunes", "hora_inicio": "08:00", "hora_fin": "10:00"}
PUT	/api/horarios/<id>	Actualiza un horario	Sí	admin	Igual que POST
DELETE	/api/horarios/<id>	Elimina un horario	Sí	admin	-
GET	/api/usuarios	Lista todos los usuarios	Sí	admin	-

🧪 Pruebas Unitarias
1️⃣ Instalar pytest:

bash
Copiar código
pip install pytest
2️⃣ Ejecutar pruebas:

bash
Copiar código
pytest tests/test_auth.py -v
Cubre:

Registro y login

Acceso con y sin token

Roles y permisos

Rutas protegidas

🧰 Ejemplo de Token JWT
Access Token (Admin)
Copiar código
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Decodificado en jwt.io:

json
Copiar código
{
  "sub": "1",
  "role": "admin",
  "exp": 1760250165
}
Refresh Token
Usa:

bash
Copiar código
POST /api/refresh
Authorization: Bearer <refresh_token>
Devuelve un nuevo access_token.

📦 Producción y Despliegue
Usa Gunicorn o Waitress como servidor WSGI.

Configura HTTPS.

Integra Dockerfile incluido para despliegue rápido:

bash
Copiar código
docker build -t flask_horarios_api .
docker run -p 5000:5000 flask_horarios_api