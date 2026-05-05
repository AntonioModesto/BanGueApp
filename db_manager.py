import sqlite3
import os

# Definimos la ruta de la base de datos
DB_DIR = os.path.join(os.path.dirname(__file__), 'database')
DB_PATH = os.path.join(DB_DIR, 'banda_guerra.db')

def conectar():
    """Establece la conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)

def inicializar_bd():
    """Crea las tablas necesarias si es la primera vez que se ejecuta el sistema."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla 1: Elementos (Con su estado para las Bajas Lógicas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elementos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_control TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            rostro_encoding BLOB NOT NULL,
            estado TEXT DEFAULT 'Activo'
        )
    ''')
    
    # Parche por si ya tenías la tabla elementos sin la columna "estado"
    cursor.execute("PRAGMA table_info(elementos)")
    columnas_elementos = [col[1] for col in cursor.fetchall()]
    if 'estado' not in columnas_elementos:
        cursor.execute("ALTER TABLE elementos ADD COLUMN estado TEXT DEFAULT 'Activo'")

    # Tabla 2: Asistencias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_control TEXT NOT NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (no_control) REFERENCES elementos (no_control)
        )
    ''')

    # Tabla 3: NUEVA TABLA DE INVENTARIO (El CRUD de los instrumentos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_equipo TEXT NOT NULL,
            no_serie TEXT UNIQUE NOT NULL,
            estado_fisico TEXT DEFAULT 'Bueno',
            asignado_a TEXT,
            FOREIGN KEY (asignado_a) REFERENCES elementos (no_control)
        )
    ''')

    conexion.commit()
    conexion.close()
    print(f"✅ Base de datos inicializada y actualizada en: {DB_PATH}")

if __name__ == "__main__":
    inicializar_bd()