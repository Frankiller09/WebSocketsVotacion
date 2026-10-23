
import { useEffect, useRef, useState } from "react";
import "./App.css";

import fotoPartidoA from "./assets/partidos/partidoA.png";
import fotoPartidoB from "./assets/partidos/partidoB.png";
import fotoPartidoC from "./assets/partidos/partidoC.png";

// Conexión con nuestro backend FastAPI
const WS_URL = "ws://127.0.0.1:8000/ws";

// Cada ID corresponde al partido registrado en MySQL
const configuracionPartidos = {
  1: {
    imagen: fotoPartidoA,
    color: "#3998ee",
  },
  2: {
    imagen: fotoPartidoB,
    color: "#b2d66b",
  },
  3: {
    imagen: fotoPartidoC,
    color: "#f18468",
  },
};

function App() {
  const [partidos, setPartidos] = useState([]);
  const [estadoConexion, setEstadoConexion] = useState("conectando");
  const [error, setError] = useState("");

  const socketRef = useRef(null);

  // Conexión WebSocket
  useEffect(() => {
    let activo = true;

    const socket = new WebSocket(WS_URL);
    socketRef.current = socket;

    socket.onopen = () => {
      if (!activo) return;

      console.log("WebSocket conectado");
      setEstadoConexion("conectado");
      setError("");
    };

    socket.onmessage = (evento) => {
      if (!activo) return;

      try {
        const mensaje = JSON.parse(evento.data);

        console.log("Broadcast recibido:", mensaje);

        if (
          mensaje.tipo === "resultados" &&
          Array.isArray(mensaje.partidos)
        ) {
          setPartidos(mensaje.partidos);
          setError("");
        }

        if (mensaje.tipo === "error") {
          setError(mensaje.mensaje || "Error de votación");
        }
      } catch (err) {
        console.error("Error al interpretar JSON:", err);
        setError("No se pudo procesar el mensaje recibido");
      }
    };

    socket.onerror = () => {
      if (!activo) return;

      setEstadoConexion("desconectado");
      setError("No se pudo conectar con el servidor");
    };

    socket.onclose = () => {
      if (!activo) return;

      setEstadoConexion("desconectado");
      console.log("WebSocket desconectado");
    };

    return () => {
      activo = false;
      socket.close();

      if (socketRef.current === socket) {
        socketRef.current = null;
      }
    };
  }, []);

  // Enviar voto al servidor
  const votar = (partidoId) => {
    const socket = socketRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError("No existe conexión con el servidor");
      return;
    }

    socket.send(
      JSON.stringify({
        tipo: "votar",
        partido_id: partidoId,
      })
    );
  };

  // Calcular total global para obtener porcentajes
  const totalVotos = partidos.reduce(
    (total, partido) => total + partido.votos,
    0
  );

  const conectado = estadoConexion === "conectado";

  const estadoTexto = {
    conectando: "Conectando...",
    conectado: "Conectado",
    desconectado: "Desconectado",
  };

  return (
    <div className="aplicacion">

      {/* ENCABEZADO */}
      <header className="encabezado">
        <div className="encabezado-interior">

          <div className="titulo">
            <span className="titulo-superior">
              PLATAFORMA ELECTORAL
            </span>

            <h1>SISTEMA DE VOTACIÓN EN TIEMPO REAL</h1>

            <p>
              Resultados actualizados mediante WebSockets
            </p>
          </div>

          <div className="indicadores">

            <span
              className={`indicador-vivo ${
                conectado ? "activo" : "inactivo"
              }`}
            >
              <span className="punto-vivo"></span>
              {conectado ? "EN VIVO" : "SIN TRANSMISIÓN"}
            </span>

            <span
              className={`estado-conexion ${
                conectado ? "online" : "offline"
              }`}
              role="status"
              aria-live="polite"
            >
              <span className="punto-conexion"></span>
              {estadoTexto[estadoConexion]}
            </span>

          </div>
        </div>
      </header>

      {/* ZONA PRINCIPAL */}
      <main className="contenido">

        {error && (
          <div className="mensaje-error" role="alert">
            {error}
          </div>
        )}

        <section
          className="tarjetas-partidos"
          aria-label="Partidos participantes"
        >

          {partidos.length === 0 ? (
            <div className="sin-resultados">
              <p>Esperando resultados del servidor...</p>
            </div>
          ) : (
            partidos.map((partido) => {

              const config = configuracionPartidos[partido.id] || {
                imagen: null,
                color: "#94a3b8",
              };

              const porcentaje = totalVotos > 0
                ? (partido.votos / totalVotos) * 100
                : 0;

              return (
                <article
                  className="tarjeta-partido"
                  key={partido.id}
                  style={{ "--color-partido": config.color }}
                >

                  {/* NOMBRE DEL PARTIDO */}
                  <h2 className="nombre-partido">
                    {partido.nombre_Partido}
                  </h2>

                  {/* FOTOGRAFÍA */}
                  <div className="imagen-partido">
                    {config.imagen ? (
                      <img
                        src={config.imagen}
                        alt={`Representante de ${partido.nombre_Partido}`}
                      />
                    ) : (
                      <span>Sin fotografía</span>
                    )}
                  </div>

                  {/* BOTÓN VOTAR */}
                  <button
                    type="button"
                    className="boton-votar"
                    onClick={() => votar(partido.id)}
                    disabled={!conectado}
                  >
                    <span>Votar</span>
                    <span aria-hidden="true">→</span>
                  </button>

                  {/* RESULTADOS */}
                  <div className="resultados">

                    <div className="encabezado-resultados">
                      <span>Porcentaje de votos</span>

                      <strong>
                        {porcentaje.toFixed(1)}%
                      </strong>
                    </div>

                    <div
                      className="barra-progreso"
                      role="progressbar"
                      aria-label={`Porcentaje de ${partido.nombre_Partido}`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={Math.round(porcentaje)}
                    >
                      <div
                        className="barra-relleno"
                        style={{
                          width: `${porcentaje}%`
                        }}
                      ></div>
                    </div>

                    <div className="total-votos">
                      <span>Total de votos</span>

                      <strong>
                        {new Intl.NumberFormat("es-EC").format(
                          partido.votos
                        )}
                      </strong>
                    </div>

                  </div>

                </article>
              );
            })
          )}

        </section>
      </main>

    </div>
  );
}

export default App;
