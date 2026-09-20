# EcoPunto

Plataforma web para la gestión y trazabilidad de residuos reciclables en comunidades urbanas de Bogotá.

**Universidad Manuela Beltrán** – Ingeniería de Software
Asignaturas: Estándares y Métricas de Software / Ingeniería Web
Evento **PLANETA VERDE 2026**

---

## 1. Requisitos

- Python 3.10 o superior
- pip

## 2. Instalación y ejecución

```bash
# 1. Ubicarse en la carpeta del proyecto
cd ecopunto

# 2. (Opcional) crear un entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

La base de datos `ecopunto.db` se crea automáticamente con el esquema y los datos
de prueba la primera vez que se ejecuta `app.py`.

Abrir el navegador en: **http://127.0.0.1:5000**

## 3. Usuarios de prueba

| Correo | Contraseña | Rol |
|---|---|---|
| admin@umb.edu.co | Admin2026* | administrador |
| laura.gomez@umb.edu.co | Eco2026* | ciudadano |
| carlos.pena@umb.edu.co | Eco2026* | ciudadano |

## 4. Pruebas funcionales

```bash
python test_ecopunto.py
```

Ejecuta 20 pruebas sobre los dos CRUD, las validaciones, el cálculo de CO₂ y la API REST.

## 5. Estructura del proyecto

```
ecopunto/
├── app.py                 Controlador: rutas Flask y API REST
├── database.py            Modelo: acceso a datos y consultas SQL
├── schema.sql             Definición del esquema (DDL)
├── seed.sql               Datos de prueba (DML)
├── test_ecopunto.py       Pruebas funcionales
├── requirements.txt       Dependencias
├── static/css/estilos.css Hoja de estilos institucional
└── templates/             Vistas Jinja2 + Bootstrap 5
    ├── base.html
    ├── login.html
    ├── tablero.html
    ├── puntos_lista.html
    ├── punto_form.html
    ├── registros_lista.html
    ├── registro_form.html
    ├── reportes.html
    └── error.html
```

## 6. Arquitectura

Aplicación cliente-servidor de tres capas bajo el patrón **MVC**:

- **Modelo** → `database.py` (SQLite 3, sentencias preparadas)
- **Vista** → `templates/` (HTML5, CSS3, Bootstrap 5, diseño responsive)
- **Controlador** → `app.py` (rutas Flask, validaciones, control de sesión)

## 7. API REST

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/puntos` | Lista los puntos de reciclaje. Filtro opcional `?localidad=` |
| GET | `/api/v1/puntos/<id>` | Consulta un punto específico |
| GET | `/api/v1/indicadores` | Indicadores ambientales consolidados |

Ejemplo:

```bash
curl http://127.0.0.1:5000/api/v1/puntos?localidad=Kennedy
```

## 8. Migración a MySQL

El archivo `schema.sql` es compatible con MySQL 8 aplicando estos cambios:

- `INTEGER PRIMARY KEY AUTOINCREMENT` → `INT AUTO_INCREMENT PRIMARY KEY`
- `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` se mantiene igual
- Agregar `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4` al final de cada `CREATE TABLE`
- En `database.py`, reemplazar `sqlite3.connect()` por `mysql.connector.connect()`
  y los placeholders `?` por `%s`
