import sqlite3
import os

# 1. Buscamos dónde está guardado tu script.sql
ruta_script = os.path.join(os.path.dirname(__file__), "..", "db", "script.sql")

# 2. Nos conectamos a la base de datos
conexion = sqlite3.connect("dulce_descontrol.db")
cursor = conexion.cursor()

try:
    # 3. Leemos tu script.sql y lo ejecutamos todo de golpe
    with open(ruta_script, "r", encoding="utf-8") as archivo:
        script = archivo.read()
        cursor.executescript(script)
    
    conexion.commit()
    print("✅ ¡Éxito! Las tablas se crearon y los datos de prueba fueron cargados.")
except Exception as e:
    print(f"❌ Hubo un error: {e}")
finally:
    conexion.close()