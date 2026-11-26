\# Pruebas Unitarias - Mini-Proyecto Flask



Este repositorio contiene las pruebas unitarias para la microaplicación de videojuegos.



\## Cobertura de Pruebas

\- \*\*Modelos (`test\_models.py`):\*\* Verifica la creación e inserción de registros en la base de datos utilizando SQLAlchemy.

\- \*\*Rutas (`test\_routes.py`):\*\* Comprueba el acceso a rutas públicas (index 200) y la redirección de rutas protegidas (302 a login).

\- \*\*API (`test\_api.py`):\*\* Valida que los endpoints de la API respondan con los códigos de estado HTTP correctos.



\## Retos Encontrados y Soluciones

1\. \*\*Configuración de la base de datos:\*\* Se cambió la conexión de MySQL a SQLite en memoria (`sqlite:///:memory:`) en el archivo `app.py` para evitar afectar la base de datos real durante las pruebas.

2\. \*\*Problemas con el ID en SQLite:\*\* SQLite no soporta autoincremento directo en `BigInteger`, por lo que se ajustó el modelo `Juego` a `Integer` con `autoincrement=True`.

3\. \*\*Importación de módulos:\*\* Se creó un archivo `conftest.py` y se ajustaron las rutas de importación para que Python encontrara el archivo `app.py` sin conflictos.



\## Ejecución

Comando: `python -m unittest discover -v tests`

