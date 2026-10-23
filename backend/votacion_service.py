from sqlalchemy import text
from database import engine


def obtener_resultados():
    with engine.connect() as conexion:
        consulta = text(
            "SELECT id, nombre_Partido, votos "
            "FROM partidos ORDER BY id"
        )

        resultado = conexion.execute(consulta)

        return [
            dict(fila)
            for fila in resultado.mappings().all()
        ]


def registrar_voto(partido_id: int):

    with engine.begin() as conexion:
        consulta = text(
            "UPDATE partidos "
            "SET votos = votos + 1 "
            "WHERE id = :partido_id"
        )

        resultado = conexion.execute(
            consulta,
            {"partido_id": partido_id}
        )

        if resultado.rowcount != 1:
            raise ValueError("El partido no existe")

    return obtener_resultados()
