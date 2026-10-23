import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from connection_manager import ConnectionManager
from votacion_service import obtener_resultados, registrar_voto


app = FastAPI()

manager = ConnectionManager()

bloqueo = asyncio.Lock()


@app.get("/")
def inicio():
    return {"mensaje": "Sistema de votacion funcionando"}


@app.get("/partidos")
def listar_partidos():
    return obtener_resultados()


@app.websocket("/ws")
async def websocket_votaciones(websocket: WebSocket):

    async with bloqueo:
        await manager.conectar(websocket)

        resultados = await run_in_threadpool(
            obtener_resultados
        )

        await websocket.send_json({
            "tipo": "resultados",
            "partidos": resultados
        })

    print("Cliente conectado")

    try:
        while True:

            try:
                mensaje = await websocket.receive_json()
            except json.JSONDecodeError:
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": "JSON invalido"
                })
                continue

            if not isinstance(mensaje, dict):
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": "Formato de mensaje invalido"
                })
                continue

            if mensaje.get("tipo") != "votar":
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": "Accion no reconocida"
                })
                continue

            partido_id = mensaje.get("partido_id")

            if type(partido_id) is not int:
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": "ID de partido invalido"
                })
                continue

            async with bloqueo:

                try:
                    resultados = await run_in_threadpool(
                        registrar_voto,
                        partido_id
                    )

                except ValueError as error:
                    await websocket.send_json({
                        "tipo": "error",
                        "mensaje": str(error)
                    })
                    continue

                except SQLAlchemyError:
                    await websocket.send_json({
                        "tipo": "error",
                        "mensaje": "Error de base de datos"
                    })
                    continue

                await manager.broadcast({
                    "tipo": "resultados",
                    "partidos": resultados
                })

    except WebSocketDisconnect:
        print("Cliente desconectado")

    finally:
        manager.desconectar(websocket)