# Sistema de Votación en Tiempo Real

Proyecto de **Aplicaciones Distribuidas** realizado con **React, FastAPI, WebSockets y MySQL**. Simula una votación entre tres partidos: cuando un usuario emite un voto, todos los navegadores conectados reciben los resultados actualizados automáticamente mediante el patrón **Broadcast**.

> **Importante:** es una simulación académica, no un sistema para elecciones reales. No autentica votantes ni limita a una persona a un solo voto.

## Funcionalidades

- Interfaz responsive con tres partidos, fotografías, barras de progreso y porcentajes.
- Comunicación bidireccional mediante WebSockets y mensajes JSON.
- Actualización simultánea de los clientes conectados (Broadcast).
- Persistencia de los votos en MySQL.
- Indicador de conexión y desconexión.
- Prueba de concurrencia de 10 clientes WebSocket.

## Arquitectura

```text
Chrome / Edge / Brave (React)
           │
           │ WebSocket: ws://127.0.0.1:8000/ws
           ▼
    FastAPI (Python)
      ├── ConnectionManager ──► Broadcast a todos los clientes
      └── votacion_service.py
                  │ SQLAlchemy + PyMySQL
                  ▼
           MySQL (votaciones)
             └── partidos
```

Al votar, React envía `{"tipo":"votar","partido_id":1}`. FastAPI registra el cambio en MySQL y difunde a todos los clientes un JSON `{"tipo":"resultados","partidos":[...]}`.

## Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | React, JavaScript (JSX), HTML5, CSS3, Vite |
| Backend | Python, FastAPI y Uvicorn |
| Comunicación | WebSocket y JSON; HTTP para consultas |
| Datos | MySQL, SQLAlchemy y PyMySQL |

Las versiones del frontend quedan fijadas por `frontend/package-lock.json`. Para publicar las **versiones reales** del backend, genera `backend/requirements.txt` con `python -m pip freeze > requirements.txt` dentro de tu entorno virtual.

## Requisitos previos

- **Git** para clonar el código.
- **Python 3.10+** y pip.
- **Node.js** compatible con el Vite del proyecto; Vite indica al menos Node 20.19+ o 22.12+ según la rama (algunas plantillas pueden pedir una versión mayor).
- **MySQL Server**. MySQL Workbench es opcional.

Comprobar las herramientas en PowerShell:

```powershell
git --version
py --version
node --version
npm --version
```

## 1. Clonar el repositorio

```powershell
git clone https://github.com/TU_USUARIO/votacion-tiempo-real.git
cd votacion-tiempo-real
```

Reemplaza `TU_USUARIO` por el nombre real del propietario del repositorio.

## 2. Crear la base de datos

Abrir MySQL Workbench, conectarse a MySQL local y ejecutar el archivo `database/init.sql` (o copiar su contenido). El script crea la base **`votaciones`**, la tabla **`partidos`** y los partidos A, B y C con 0 votos. Ejecutarlo una sola vez en una base nueva.

Validar:

```sql
SELECT * FROM votaciones.partidos;
```

## 3. Ejecutar el backend FastAPI

Abrir PowerShell en la carpeta del repositorio:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar **`backend/.env`** e ingresar la contraseña local de MySQL:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=TU_CONTRASENA_LOCAL
DB_NAME=votaciones
```

**No compartir ni subir `.env` a GitHub**. Cada computadora necesita su propio archivo.

Arrancar el servidor desde `backend/`:

```powershell
uvicorn main:app --reload
```

Comprobaciones:

- `http://127.0.0.1:8000/` — respuesta básica.
- `http://127.0.0.1:8000/partidos` — partidos y votos en JSON.
- `http://127.0.0.1:8000/docs` — interfaz para probar endpoints HTTP.

Dejar esta terminal abierta.

## 4. Ejecutar el frontend React

Abrir una **segunda terminal** en la carpeta raíz del proyecto:

```powershell
cd frontend
npm install
npm run dev
```

Entrar a `http://localhost:5173/` (o a la dirección que muestre Vite). El frontend usa `ws://127.0.0.1:8000/ws`, por lo que **React y FastAPI deben ejecutarse en la misma PC** para esta demostración local. No es necesario recrear el proyecto con `npm create vite`: el código ya viene en el repositorio.

## 5. Demostrar Broadcast

1. Abrir `http://localhost:5173/` en **tres navegadores o pestañas** (por ejemplo, Chrome, Edge y Brave).
2. Comprobar que las tres interfaces indiquen **EN VIVO / Conectado**.
3. Pulsar **Votar** por un partido desde la primera ventana.
4. Observar que las barras, porcentajes y contadores de las otras ventanas cambian **sin recargar**.
5. Comprobar el contador en MySQL: `SELECT * FROM votaciones.partidos;`.

El porcentaje se calcula como `(votos_del_partido / total_de_votos) × 100`. Si no hay votos, el porcentaje es cero.

## 6. Prueba de concurrencia (opcional)

Con FastAPI en ejecución, abrir otra terminal dentro de `backend/`, activar el entorno virtual y ejecutar:

```powershell
.\.venv\Scripts\Activate.ps1
python tests/prueba_concurrencia.py
```

El script genera diez conexiones WebSocket y comprueba que el incremento total coincida con los diez votos enviados. Realiza la prueba cuando otros usuarios no estén votando, para que la comparación sea válida.

## Estructura del proyecto

```text
votacion-tiempo-real/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── connection_manager.py
│   ├── votacion_service.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       └── prueba_concurrencia.py
├── frontend/
│   ├── src/
│   │   ├── assets/partidos/
│   │   │   ├── partidoA.png
│   │   │   ├── partidoB.png
│   │   │   └── partidoC.png
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── package-lock.json
├── database/
│   └── init.sql
├── .gitignore
└── README.md
```

## Solución de problemas

| Problema | Qué revisar |
| --- | --- |
| `Access denied for user 'root'` | Usuario y contraseña de `backend/.env`. |
| `Unknown database 'votaciones'` | Ejecutar `database/init.sql`. |
| React muestra «Desconectado» | FastAPI debe funcionar en el puerto 8000. |
| `No module named fastapi` | Activar `.venv` e instalar `requirements.txt`. |
| `npm` no se reconoce | Instalar Node.js y reabrir PowerShell. |
| No se muestran las imágenes | Comprobar los archivos `frontend/src/assets/partidos/partidoA.png`, `partidoB.png`, `partidoC.png`. |
| No se puede conectar desde un celular | La URL `127.0.0.1` se refiere al propio dispositivo. Es necesario configurar acceso por LAN. |

## Limitaciones

El Connection Manager mantiene conexiones en memoria y funciona con una única instancia del servidor. No hay identificación de votantes, prevención de votos repetidos ni reconexión automática del frontend. La aplicación está diseñada como laboratorio local de **Broadcast**, no para uso electoral real.

## Documentación

- [FastAPI — WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [React — Hooks](https://react.dev/reference/react)
- [Vite — Getting Started](https://vite.dev/guide/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [MySQL](https://dev.mysql.com/doc/)

**Universidad de las Fuerzas Armadas ESPE — Aplicaciones Distribuidas.**
