-- Instalar en una base nueva; los INSERT deben ejecutarse solo una vez.
CREATE DATABASE IF NOT EXISTS votaciones;
USE votaciones;

CREATE TABLE IF NOT EXISTS partidos (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre_Partido VARCHAR(100) NOT NULL UNIQUE,
    votos INT NOT NULL DEFAULT 0
);

INSERT INTO partidos (nombre_Partido)
VALUES
    ('Partido A'),
    ('Partido B'),
    ('Partido C');

SELECT * FROM partidos;
