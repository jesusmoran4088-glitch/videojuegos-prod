# 🧪 Pruebas Unitarias - Mini-Proyecto Flask

Este repositorio contiene la suite de pruebas unitarias diseñada para garantizar el correcto funcionamiento de la microaplicación de videojuegos. 

## 📊 Cobertura de Pruebas

La suite está dividida en tres áreas clave para asegurar la calidad del software:

- 🗄️ **Modelos (`test_models.py`):** Verifica la correcta creación e inserción de registros en la base de datos utilizando SQLAlchemy, asegurando que las tablas y relaciones funcionen.
- 🌐 **Rutas (`test_routes.py`):** Comprueba el acceso a rutas públicas (como el *index*, esperando un código 200) y valida la redirección (302) de las rutas protegidas cuando no hay una sesión activa, enviando al usuario al login.
- 🔌 **API (`test_api.py`):** Valida que los endpoints de la API respondan con los códigos de estado HTTP correctos (ej. 404 para rutas no encontradas).

## 🚧 Retos Encontrados y Soluciones

Durante el desarrollo de las pruebas, nos enfrentamos a varios desafíos técnicos que se resolvieron de la siguiente manera:

1. **Configuración de la base de datos:** 
   * *Reto:* Las pruebas no debían afectar la base de datos real de producción (MySQL).
   * *Solución:* Se cambió la conexión a SQLite en memoria (`sqlite:///:memory:`) dentro de la configuración de pruebas en `app.py`. Esto permite hacer pruebas rápidas y limpias sin ensuciar MySQL.
2. **Problemas con el ID en SQLite:** 
   * *Reto:* SQLite no soporta el autoincremento directo en columnas de tipo `BigInteger`, lo que causaba errores al insertar datos en las pruebas.
   * *Solución:* Se ajustó el modelo `Juego` cambiando el tipo de dato a `Integer` con la propiedad `autoincrement=True`.
3. **Importación de módulos:** 
   * *Reto:* Python no encontraba el archivo principal `app.py` al ejecutar las pruebas desde la carpeta `tests`.
   * *Solución:* Se creó un archivo `conftest.py` y se ajustaron las rutas de importación en el sistema para evitar conflictos de módulos.

## 🚀 Ejecución

Para correr todas las pruebas y ver el detalle de cada una, ejecuta el siguiente comando en la raíz de tu terminal:

```bash
python -m unittest discover -v tests
