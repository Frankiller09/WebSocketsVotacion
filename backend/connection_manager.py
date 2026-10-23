from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:

    def __init__(self):
        self.clientes_activos: list[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.clientes_activos.append(websocket)

    def desconectar(self, websocket: WebSocket):
        if websocket in self.clientes_activos:
            self.clientes_activos.remove(websocket)

    async def broadcast(self, mensaje: dict):
        for cliente in self.clientes_activos.copy():
            try:
                await cliente.send_json(mensaje)
            except (WebSocketDisconnect, RuntimeError, OSError):
                self.desconectar(cliente)
