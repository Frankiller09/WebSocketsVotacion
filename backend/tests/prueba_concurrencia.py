import asyncio
import json
from urllib.request import urlopen

import websockets

URL_HTTP = "http://127.0.0.1:8000/partidos"
URL_WS = "ws://127.0.0.1:8000/ws"

CANTIDAD_CLIENTES = 10
PARTIDO_ID = 1


def consultar_votos():
    with urlopen(URL_HTTP, timeout=10) as respuesta:
        partidos = json.load(respuesta)

    for partido in partidos:
        if partido["id"] == PARTIDO_ID:
            return partido["votos"]

    raise ValueError("No se encontro el partido")


async def simular_cliente(inicio, preparados, esperado):
    async with websockets.connect(URL_WS) as socket:

        # Recibir el estado inicial
        await socket.recv()

        # Informar que este cliente ya esta conectado
        preparados.release()

        # Esperar a que todos puedan votar juntos
        await inicio.wait()

        # Enviar un voto por WebSocket
        await socket.send(json.dumps({
            "tipo": "votar",
            "partido_id": PARTIDO_ID
        }))

        # Esperar el resultado final difundido
        while True:
            respuesta = await socket.recv()
            mensaje = json.loads(respuesta)

            if mensaje.get("tipo") != "resultados":
                continue

            for partido in mensaje["partidos"]:
                if (
                    partido["id"] == PARTIDO_ID
                    and partido["votos"] >= esperado
                ):
                    return


async def main():
    votos_antes = await asyncio.to_thread(consultar_votos)
    esperado = votos_antes + CANTIDAD_CLIENTES

    print(f"Votos antes: {votos_antes}")
    print(f"Clientes simultaneos: {CANTIDAD_CLIENTES}")

    inicio = asyncio.Event()
    preparados = asyncio.Semaphore(0)

    tareas = [
        asyncio.create_task(
            simular_cliente(inicio, preparados, esperado)
        )
        for _ in range(CANTIDAD_CLIENTES)
    ]

    try:
        # Confirmar que los 10 clientes estan conectados
        for _ in range(CANTIDAD_CLIENTES):
            await asyncio.wait_for(
                preparados.acquire(),
                timeout=15
            )

        print("Todos los clientes conectados")
        print("Enviando votos simultaneos...")

        inicio.set()

        # Esperar que todos reciban el resultado final
        await asyncio.wait_for(
            asyncio.gather(*tareas),
            timeout=30
        )

        votos_despues = await asyncio.to_thread(consultar_votos)
        diferencia = votos_despues - votos_antes

        print(f"Votos despues: {votos_despues}")
        print(f"Votos registrados: {diferencia}")

        if diferencia == CANTIDAD_CLIENTES:
            print("PRUEBA EXITOSA: No se perdieron votos")
        else:
            print("PRUEBA FALLIDA: Conteo incorrecto")

    finally:
        for tarea in tareas:
            if not tarea.done():
                tarea.cancel()


if __name__ == "__main__":
    asyncio.run(main())
