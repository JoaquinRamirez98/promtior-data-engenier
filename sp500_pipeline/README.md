# Pipeline de Datos S&P 500 - Desafío Técnico Promtior (Joaquín Ramírez)

¡Hola! Este repositorio contiene mi solución al desafío técnico para la posición de Data Engineer en Promtior. He desarrollado un pipeline de datos que extrae información de las empresas del S&P 500 desde Wikipedia, la procesa y la carga en una base de datos SQLite. Finalmente, los insights clave se presentan en un dashboard interactivo creado con Power BI.

Mi objetivo fue construir una solución robusta, modular y fácil de entender, aplicando buenas prácticas de ingeniería de datos.

## Tabla de Contenidos
* [Visión General del Proyecto](#visión-general-del-proyecto)
* [Tecnologías Utilizadas](#tecnologías-utilizadas)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Prerrequisitos](#prerrequisitos)
* [Instalación](#instalación)
* [Ejecución del Pipeline](#ejecución-del-pipeline)
* [Resultados y Visualización](#resultados-y-visualización)
* [Documentación Adicional](#documentación-adicional)

## Visión General del Proyecto

Este pipeline de datos cumple con el ciclo ETL (Extract, Transform, Load) y visualización:
1.  **Extracción:** Se conecta a la página de Wikipedia "List of S&P 500 companies" y extrae la tabla principal de componentes.
2.  **Transformación:** Los datos brutos se limpian y estructuran utilizando Pandas. Esto incluye la conversión de tipos de datos, el parseo de información como años de fundación y la división de la ubicación de las sedes en ciudad y estado.
3.  **Carga:** Los datos procesados se almacenan en una tabla `companies` dentro de una base de datos SQLite local (`data/sp500_companies.db`).
4.  **Visualización:** Un informe en Power BI (`reports/sp500_analysis.pbix`) consume los datos de SQLite para responder a las siguientes preguntas clave:
    *   ¿Cuáles son los 5 `GICS Sectors` con mayor número de empresas en el S&P 500?
    *   ¿Cuáles son las 10 empresas más antiguas del S&P 500 (basado en `Founded_Year`)?
    *   ¿Cuáles son los 5 estados (`Headquarters_State`) con mayor número de sedes de empresas del S&P 500?

## Tecnologías Utilizadas

*   **Lenguaje:** Python 3.11 (ajusta si usaste otra versión)
*   **Extracción Web:** `requests` para peticiones HTTP, `BeautifulSoup4` para el parseo de HTML.
*   **Transformación de Datos:** `pandas` para la manipulación eficiente de DataFrames.
*   **Base de Datos:** SQLite 3 para el almacenamiento local.
*   **Visualización:** Microsoft Power BI Desktop.
*   **Gestión de Entorno:** `venv` para entornos virtuales.
*   **Gestión de Dependencias:** `pip` y `requirements.txt`.
*   **Control de Versiones:** Git y GitHub.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera para promover la modularidad y claridad:

data-challenge-S-P500-wikipedia/ # Nombre de tu repo
├── data/
│ └── sp500_companies.db # Base de datos SQLite generada
├── doc/
│ ├── project_overview.md # Mi enfoque detallado, desafíos y soluciones
│ └── database_schema.png # Diagrama del esquema de la base de datos
├── reports/
│ └── sp500_analysis.pbix # Reporte de Power BI
├── src/
│ ├── init.py
│ ├── config.py # Configuraciones centrales
│ ├── data_extraction.py # Módulo de extracción de datos
│ ├── data_transformation.py # Módulo de transformación de datos
│ ├── database_operations.py # Módulo de operaciones de base de datos
│ └── main_pipeline.py # Script orquestador del pipeline
├── .gitignore
├── requirements.txt # Dependencias de Python
└── README.md # Este archivo


## Prerrequisitos

Para ejecutar este proyecto, necesitarás:

1.  **Python:** Idealmente versión 3.10 o superior.
2.  **pip:** El instalador de paquetes de Python.
3.  **Git:** Para clonar el repositorio.
4.  **Microsoft Power BI Desktop:** Para abrir e interactuar con el archivo `.pbix`.
5.  **Controlador ODBC de SQLite (para Power BI):**
    *   El archivo `.pbix` está configurado para usar una conexión ODBC a SQLite. Si deseas refrescar los datos o explorar la conexión, necesitarás el driver ODBC de SQLite. Recomiendo descargar el instalador `.exe` de 64 bits (ej. `sqliteodbc_w64.exe`) desde [http://www.ch-werner.de/sqliteodbc/](http://www.ch-werner.de/sqliteodbc/), instalarlo y reiniciar Power BI.

## Instalación

Sigue estos pasos para poner en marcha el proyecto:

1.  **Clona este repositorio:**
    git clone https://github.com/JoaquinRamirez98/promtior-data-engenier.git
    cd data-challenge-S-P500-wikipedia
    

2.  **Crea y activa un entorno virtual Python:**
    *   En Windows:
        python -m venv .venv
        .\.venv\Scripts\activate
        
    *   En macOS/Linux:
        python3 -m venv .venv
        source .venv/bin/activate
    

3.  **Instala las dependencias necesarias:**
    pip install -r requirements.txt


## Ejecución del Pipeline

Con el entorno virtual activado, ejecuta el pipeline desde la raíz del proyecto:

python -m src.main_pipeline


Esto ejecutará el script main_pipeline.py, que orquesta los pasos de extracción, transformación y carga. Verás logs en la consola indicando el progreso.

Resultados y Visualización

* Base de Datos: El pipeline generará (o reemplazará) la base de datos data/sp500_companies.db.

* Reporte Power BI: El dashboard interactivo se encuentra en reports/sp500_analysis.pbix. Puedes abrirlo con Power BI Desktop para ver las respuestas a las preguntas y explorar los datos. La conexión en el archivo ya está configurada para leer de la base de datos local.

Documentación Adicional

Para una comprensión más profunda de mi proceso de pensamiento, las decisiones de diseño y cómo abordé los desafíos:
* Resumen Detallado del Proyecto: Consulta doc/project_overview.md.

* Esquema de la Base de Datos: El diagrama visual de la tabla companies está en doc/database_schema.png.
¡Gracias por la oportunidad de realizar este desafío! Espero que esta solución demuestre mis capacidades.