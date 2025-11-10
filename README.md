# 📅 API Gestión de Horarios con Autenticación JWT

## 📋 Descripción General

Sistema completo de gestión de horarios académicos con autenticación JWT, autorización por roles y una interfaz web interactiva. Permite a los administradores crear, editar y eliminar horarios con visualización avanzada de datos, y permite a los usuarios normales gestionar sus propios horarios.

**Características principales:**
- ✅ Autenticación JWT con tokens de acceso y refresco
- ✅ Hash de contraseñas con bcrypt
- ✅ Control de roles (admin/user)
- ✅ CRUD completo de horarios
- ✅ Asignación flexible de horarios a usuarios
- ✅ Búsqueda, filtro y ordenamiento en tiempo real
- ✅ Tabla visual con colores (verde: asignado, rojo: sin asignar)
- ✅ Dashboard responsive con HTML/CSS/JS vanilla
- ✅ API RESTful documentada

**Stack tecnológico:**
- Backend: Flask 2.3.3
- ORM: SQLAlchemy 2.0.23
- Autenticación: Flask-JWT-Extended 4.6.0
- Hashing: bcrypt 4.1.2
- Base de datos: SQLite (desarrollo) / MySQL (producción)
- Frontend: HTML5, CSS3, JavaScript vanilla
- Servidor: Gunicorn

---

## 🚀 Instalación

### Requisitos previos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/DylanSteve15/parcial_2_api_jwt.git
   cd parcial_2_api_jwt
   ```

2. **Crea un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate
   # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura el archivo `.env`:**
   ```bash
   cat > .env << EOF
   JWT_SECRET_KEY=tu-clave-super-secreta-minimo-32-caracteres-1234567890abcdef
   MYSQL_URI=sqlite:///horarios_local.db
   EOF
   ```
   
   **Opciones:**
   - `MYSQL_URI=sqlite:///horarios_local.db` (desarrollo local)
   - `MYSQL_URI=mysql+pymysql://usuario:pass@localhost:3306/horarios` (MySQL)

5. **Ejecuta la aplicación:**
   ```bash
   python main.py
   ```

6. **Abre en tu navegador:**
   ```
   http://127.0.0.1:5000
   ```

---

## 🔐 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# JWT - Clave secreta para firmar tokens (genérala fuerte y larga)
JWT_SECRET_KEY=tu-clave-super-secreta-minimo-32-caracteres-aqui-1234567890abcdef

# Base de datos
# Opción 1: SQLite (desarrollo)
MYSQL_URI=sqlite:///horarios_local.db

# Opción 2: MySQL (producción)
# MYSQL_URI=mysql+pymysql://usuario:contraseña@localhost:3306/nombre_db
```

**Notas importantes:**
- `JWT_SECRET_KEY`: Debe ser una cadena larga y aleatoria (mínimo 32 caracteres)
- Si omites `MYSQL_URI`, la app crea automáticamente `horarios_local.db`
- No compartas nunca tus claves secretas en repositorios públicos

---

## 📊 Estructura del Proyecto

```
parcial_2_api_jwt/
├── main.py                          # Punto de entrada principal
├── requirements.txt                 # Dependencias Python
├── README.md                        # Este archivo
├── .env                             # Variables de entorno (no versionar)
│
├── config/
│   ├── database.py                 # Configuración y conexión a BD
│   ├── jwt.py                      # Configuración de tokens JWT
│   └── __init__.py
│
├── models/
│   ├── db.py                       # Base SQLAlchemy
│   ├── user_model.py               # Modelo de Usuario
│   ├── horario_model.py            # Modelo de Horario
│   └── __init__.py
│
├── controllers/
│   ├── user_controller.py          # Rutas de autenticación y usuarios
│   ├── horario_controller.py       # Rutas CRUD de horarios
│   └── __init__.py
│
├── services/
│   ├── user_service.py             # Lógica de negocio de usuarios
│   ├── horario_service.py          # Lógica de negocio de horarios
│   └── __init__.py
│
├── repositories/
│   ├── user_repository.py          # Acceso a BD usuarios
│   ├── horario_repository.py       # Acceso a BD horarios
│   └── __init__.py
│
└── static/
    └── index.html                  # Frontend completo (HTML/CSS/JS)
```

---

## 🗄️ Modelos de Datos

### User (Usuario)
```python
{
  "id": 1,                    # Identificador único
  "email": "admin@test.com",  # Email único
  "password": "hasheado",     # Hash bcrypt
  "role": "admin"             # "admin" o "user"
}
```

### Horario
```python
{
  "id": 1,                    # Identificador único
  "materia": "Matemática",    # Nombre de la materia
  "docente": "Dr. García",    # Nombre del docente
  "dia": "Lunes",             # Día de la semana
  "hora_inicio": "08:00",     # Hora de inicio (HH:MM)
  "hora_fin": "10:00",        # Hora de fin (HH:MM)
  "salon": "A101",            # Sala/aula
  "user_id": 2                # ID del usuario asignado (nullable)
}
```

---

## 🔑 Autenticación

### Flujo de Autenticación

```
1. Usuario se REGISTRA
   ↓
   POST /api/registry
   Body: {email, password, role?}
   Response: {id, email, role}
   
2. Usuario hace LOGIN
   ↓
   POST /api/login
   Body: {email, password}
   Response: {access_token, refresh_token, user}
   
3. Usuario accede a recurso protegido
   ↓
   GET/POST/PUT/DELETE /api/*
   Header: Authorization: Bearer <access_token>
   
4. Si token expira (1h)
   ↓
   POST /api/refresh
   Header: Authorization: Bearer <refresh_token>
   Response: {access_token}
   
5. Usuario sale (LOGOUT)
   ↓
   POST /api/logout
   Header: Authorization: Bearer <access_token>
   (Token añadido a blacklist)
```

### Estructura de Tokens JWT

**Access Token** (expira en 1 hora):
```json
{
  "sub": "1",           // user_id
  "role": "admin",      // Rol del usuario
  "exp": 1699700000    // Timestamp de expiración
}
```

**Refresh Token** (expira en 14 días):
- Se usa para obtener un nuevo access_token sin volver a hacer login
- Se envía en el header: `Authorization: Bearer <refresh_token>`

---

## 👥 Roles y Permisos

### Rol: `user` (Usuario Normal)
| Acción | Permiso |
|--------|---------|
| Ver sus propios horarios | ✅ |
| Crear sus propios horarios | ✅ |
| Editar sus propios horarios | ✅ |
| Eliminar sus propios horarios | ✅ |
| Ver todos los horarios | ❌ |
| Editar horarios de otros | ❌ |
| Crear/editar/eliminar usuarios | ❌ |

### Rol: `admin` (Administrador)
| Acción | Permiso |
|--------|---------|
| Ver TODOS los horarios | ✅ |
| Crear horarios (asignar a usuario) | ✅ |
| Editar cualquier horario | ✅ |
| Reasignar horarios a usuarios | ✅ |
| Eliminar cualquier horario | ✅ |
| Registrar nuevos usuarios | ✅ |
| Editar/eliminar usuarios | ✅ |
| Solo puede haber 1 admin | ✅ |

---

## 📡 API - Tabla de Endpoints

### Autenticación
| Método | Endpoint | Descripción | Auth | Body |
|--------|----------|-------------|------|------|
| POST | `/api/registry` | Registro nuevo usuario | ❌ | `{email, password, role?}` |
| POST | `/api/login` | Login y obtener tokens | ❌ | `{email, password}` |
| POST | `/api/refresh` | Renovar access_token | 🔄 Refresh | - |
| POST | `/api/logout` | Cerrar sesión | ✅ | - |

### Usuarios (Admin)
| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/api/users` | Listar todos los usuarios | ✅ | admin |
| GET | `/api/users/<id>` | Obtener usuario por ID | ✅ | - |
| PUT | `/api/users/<id>` | Actualizar usuario | ✅ | admin |
| DELETE | `/api/users/<id>` | Eliminar usuario | ✅ | admin |

### Horarios - Para Admin
| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/api/horarios` | Listar TODOS los horarios | ✅ | - |
| GET | `/api/horarios/<id>` | Obtener horario por ID | ✅ | - |
| POST | `/api/horarios` | Crear nuevo horario (con user_id opcional) | ✅ | admin |
| PUT | `/api/horarios/<id>` | Actualizar horario (cambiar usuario) | ✅ | admin |
| DELETE | `/api/horarios/<id>` | Eliminar horario | ✅ | admin |

### Horarios - Para Usuarios Normales
| Método | Endpoint | Descripción | Auth | Body |
|--------|----------|-------------|------|------|
| GET | `/api/mis-horarios` | Obtener propios horarios | ✅ | - |
| POST | `/api/mis-horarios` | Crear propio horario | ✅ | `{dia, hora_inicio, hora_fin, materia, docente, salon}` |
| PUT | `/api/mis-horarios/<id>` | Editar propio horario | ✅ | Igual a POST |
| DELETE | `/api/mis-horarios/<id>` | Eliminar propio horario | ✅ | - |

---

## 🎨 Frontend - Dashboard

### Para Administrador

#### 1. Sección "Crear Nuevo Horario"
```
┌─────────────────────────────────────────┐
│ Crear Nuevo Horario                     │
├─────────────────────────────────────────┤
│ [Selector Usuario (Opcional)]           │
│ [Selector Día]                          │
│ [Hora Inicio] [Hora Fin]                │
│ [Materia] [Docente] [Salón]            │
│ [Guardar Horario]                       │
└─────────────────────────────────────────┘
```

**Funcionamiento:**
- Selecciona un usuario del dropdown (opcional)
- Completa los campos del horario
- Haz clic en "Guardar Horario"
- El horario se crea y se asigna al usuario seleccionado

#### 2. Sección "Todos los Horarios" - CON BÚSQUEDA, FILTRO Y ORDENAMIENTO
```
┌─────────────────────────────────────────────────────────┐
│ 📋 Todos los Horarios                                   │
├─────────────────────────────────────────────────────────┤
│ [🔍 Buscar...] [👤 Filtrar Usuario] [📅 Filtrar Día]  │
├─────────────────────────────────────────────────────────┤
│ ID↕│Día↕│Inicio↕│Fin↕│Materia↕│Docente↕│...│Acciones│
│ ① │Lun │08:00  │10:00│Mat.    │Dr. García│...│✏️🗑️│
│ ② │Mar │10:00  │12:00│Fís.    │Dr. López │...│✏️🗑️│
│ ③ │Mié │14:00  │16:00│Quím    │Dra. Smith│...│✏️🗑️│
└─────────────────────────────────────────────────────────┘
```

**Características nuevas:**
- 🔍 **Búsqueda en tiempo real**: busca por materia, docente o usuario
- 📅 **Filtro por día**: muestra solo horarios de un día específico
- 👤 **Filtro por usuario**: muestra solo horarios asignados a un usuario
- 📊 **Ordenamiento por columnas**: haz clic en encabezados para ordenar (↑/↓)
- 🎨 **Colores:**
  - 🟢 Verde: horario asignado a un usuario
  - 🔴 Rojo: horario sin asignar
- ✏️ **Editar**: cambiar datos del horario y reasignar usuario
- 🗑️ **Eliminar**: eliminar horario

#### 3. Sección "Registrar Nuevo Usuario"
```
┌─────────────────────────────────────────┐
│ Registrar Nuevo Usuario                 │
├─────────────────────────────────────────┤
│ [Email]                                 │
│ [Contraseña]                            │
│ [Registrar Usuario]                     │
└─────────────────────────────────────────┘
```

---

### Para Usuario Normal

#### 1. Sección "Mis Horarios"
```
┌─────────────────────────────────────────┐
│ 📚 Mis Horarios                         │
├─────────────────────────────────────────┤
│ [+ Crear Mi Horario]                    │
├─────────────────────────────────────────┤
│ Día│Inicio│Fin│Materia│Docente│Acciones│
│ Lun│08:00│10:00│Matemática│Dr. García│✏️🗑️│
│ Mar│14:00│16:00│Física│Dr. López│✏️🗑️│
└─────────────────────────────────────────┘
```

**Funcionalidades:**
- Ver solo sus propios horarios (filtrados automáticamente)
- Crear nuevos horarios personales
- Editar sus horarios
- Eliminar sus horarios
- NO puede ver horarios de otros usuarios

---

## 🧪 Cómo Usar - Ejemplos

### 1. Registrar un usuario
```bash
curl -X POST http://localhost:5000/api/registry \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@test.com",
    "password": "contraseña123",
    "role": "user"
  }'
```

**Response:**
```json
{
  "id": 2,
  "email": "usuario@test.com",
  "role": "user"
}
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@test.com",
    "password": "contraseña123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 2,
    "email": "usuario@test.com",
    "role": "user"
  }
}
```

### 3. Crear horario como Admin (con usuario asignado)
```bash
curl -X POST http://localhost:5000/api/horarios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "materia": "Matemática",
    "docente": "Dr. García",
    "dia": "Lunes",
    "hora_inicio": "08:00",
    "hora_fin": "10:00",
    "salon": "A101",
    "user_id": 2
  }'
```

### 4. Crear horario como Usuario Normal (propios horarios)
```bash
curl -X POST http://localhost:5000/api/mis-horarios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "materia": "Programación",
    "docente": "Dr. López",
    "dia": "Martes",
    "hora_inicio": "14:00",
    "hora_fin": "16:00",
    "salon": "B202"
  }'
```

### 5. Obtener todos los horarios (solo Admin)
```bash
curl -X GET http://localhost:5000/api/horarios \
  -H "Authorization: Bearer <access_token>"
```

### 6. Editar horario y cambiar usuario asignado
```bash
curl -X PUT http://localhost:5000/api/horarios/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "materia": "Matemática Avanzada",
    "docente": "Dr. García",
    "dia": "Lunes",
    "hora_inicio": "09:00",
    "hora_fin": "11:00",
    "salon": "A102",
    "user_id": 3
  }'
```

### 7. Logout
```bash
curl -X POST http://localhost:5000/api/logout \
  -H "Authorization: Bearer <access_token>"
```

---

## 🚀 Despliegue (Producción)

### Opción 1: Railway.app

1. Conecta tu repositorio GitHub a Railway
2. Configura variables de entorno:
   - `JWT_SECRET_KEY`: Tu clave secreta fuerte
   - `MYSQL_URI`: Conexión a BD MySQL
3. Railway deployará automáticamente

### Opción 2: Heroku

```bash
# Instala Heroku CLI
# Login
heroku login

# Crea app
heroku create nombre-app

# Configura variables
heroku config:set JWT_SECRET_KEY=tu-clave-secreta
heroku config:set MYSQL_URI=tu-conexion-bd

# Deploy
git push heroku main
```

### Opción 3: Docker

```dockerfile
# Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
```

```bash
docker build -t horarios-api .
docker run -p 8000:8000 \
  -e JWT_SECRET_KEY=tu-clave \
  -e MYSQL_URI=tu-conexion \
  horarios-api
```

---

## 📝 Pruebas

### Cuentas de Prueba

**Admin:**
- Email: `admin@test.com`
- Password: `admin123`
- Rol: `admin`

**Usuario Normal:**
- Email: `usuario@test.com`
- Password: `usuario123`
- Rol: `user`

### Pruebas Manuales con la Interfaz

1. Abre http://localhost:5000
2. Regístrate como admin o usuario
3. Haz login
4. Si eres admin:
   - Crea usuarios en "Registrar Nuevo Usuario"
   - Crea horarios en "Crear Nuevo Horario"
   - Busca, filtra y ordena en "Todos los Horarios"
   - Edita horarios para cambiar usuario asignado
5. Si eres usuario:
   - Ve solo tus horarios en "Mis Horarios"
   - Crea/edita/elimina tus propios horarios

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| "No hay sesión activa" | Inicia sesión nuevamente, limpia localStorage |
| "Token inválido" | Token expiró, usa refresh token o haz login de nuevo |
| "Acceso denegado (403)" | No tienes el rol requerido |
| "Puerto 5000 en uso" | Cambia el puerto: `app.run(port=5001)` |
| "BD no se crea" | Verifica permisos de carpeta, elimina horarios_local.db |

---

## 🤝 Contribuciones

Este proyecto está disponible para aprendizaje y mejoras. Siéntete libre de:
- 🐛 Reportar bugs
- 💡 Sugerir nuevas características
- 🔧 Mejorar el código
- 📚 Mejorar la documentación

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👨‍💻 Autor

**Dylan Steve**
- GitHub: [@DylanSteve15](https://github.com/DylanSteve15)
- Proyecto: parcial_2_api_jwt

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo tener múltiples admins?**
A: No, solo se permite un administrador en el sistema. Si intentas registrar otro admin, será rechazado.

**P: ¿Cuánto tiempo duran los tokens?**
A: Access token: 1 hora | Refresh token: 14 días

**P: ¿Se pueden asignar múltiples horarios a un usuario?**
A: Sí, cada horario puede asignarse a un usuario. Un usuario puede tener varios horarios.

**P: ¿Qué bases de datos soporta?**
A: SQLite (desarrollo) y MySQL (producción). Para otras, actualiza config/database.py

**P: ¿Dónde se guardan los tokens?**
A: En localStorage del navegador (acceso) y blacklist en memoria (logout).

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en la consola
2. Verifica las variables de entorno
3. Asegúrate de tener las dependencias instaladas
4. Limpia el navegador (localStorage, cookies)

---

**Última actualización:** Noviembre 10, 2025
**Versión:** 2.0.0 (Con búsqueda, filtro, ordenamiento y asignación de usuarios)
