# Resumen del Proyecto: Pipeline de Datos S&P 500

## 1. Introducción y Objetivo del Desafío

El presente desafío para la empresa promtior, orientado al puesto de data engenier. Este mismo tuvo como objetivo el desarrollo de un pipeline de datos para extraer información sobre alguna pagina a eleccion (en mi caso las empresas listadas en el S&P 500), transformar estos datos a un formato estructurado, limpio, y finalmente exponer insights relevantes a través de un reporte en Power BI. Este proyecto busca demostrar habilidades en ingeniería de datos, incluyendo web scraping, transformación de datos, manejo de bases de datos y visualización.

## 2. Enfoque y Lógica de Implementación

Se adoptó un enfoque modular para el desarrollo del pipeline, separando las responsabilidades de extracción, transformación y carga (ETL). La solución se implementó principalmente en Python, aprovechando sus robustas librerías para cada etapa del proceso.

### 2.1. Tecnologías Utilizadas
    *   Lenguaje de Programación: Python 3.x
    *   Extracción de Datos (Web Scraping): Librerías `requests` (para peticiones HTTP) y `BeautifulSoup4` (para parseo de HTML).
    *   Transformación de Datos: Librería `pandas` para la manipulación y limpieza de datos tabulares.
    *   Almacenamiento de Datos: SQLite como base de datos local por su simplicidad y portabilidad para este desafío.
    *   Visualización y Reporte: Microsoft Power BI Desktop.
    *   Control de Versiones: Git y GitHub.

### 2.2. Flujo del Pipeline de Datos (ETL)
    1.  Extracción (Extract): Se obtiene el contenido HTML de la página de Wikipedia "List of S&P 500 companies". Se identifica y parsea la tabla principal que contiene los datos de las compañías.

    2.  Transformación (Transform): Los datos crudos extraídos se cargan en un DataFrame de Pandas. Se realiza la limpieza (manejo de nulos, corrección de formatos), conversión de tipos de datos (fechas, números) y estructuración (separación de ciudad/estado, selección de columnas finales).

    3.  Carga (Load): El DataFrame transformado se carga en una tabla llamada `companies` dentro de una base de datos SQLite local. Se utiliza una estrategia de reemplazo (`if_exists='replace'`) para facilitar la re-ejecución durante el desarrollo y las pruebas.

    4.  Visualización (Exposición de Insights): Power BI se conecta a la base de datos SQLite para ingestar la tabla `companies` y generar visualizaciones que responden a las preguntas específicas del desafío.

## 3. Lógica de Implementación Detallada

### 3.1. Extracción de Datos
    *   La fuente de datos es la URL: `https://en.wikipedia.org/wiki/List_of_S%26P_500_companies`.
    *   La tabla principal de componentes se selecciona prioritariamente usando su `id` HTML (`constituents`). Como fallback, se itera sobre todas las tablas con la clase `wikitable sortable` y se identifica la correcta buscando la presencia del encabezado único "GICS Sector".
    *   Los encabezados de la tabla HTML se mapean dinámicamente a las columnas deseadas definidas en un archivo de configuración, permitiendo una mayor flexibilidad ante cambios menores en la estructura de la tabla.

### 3.2. Transformación de Datos
    *   La columna `Founded` se procesa para extraer el primer año de 4 dígitos como `Founded_Year` (tipo entero).
    *   La columna `Date_Added` se convierte al tipo `datetime` de Pandas, limpiando previamente posibles notas al pie.
    *   La columna `CIK` se convierte a tipo entero.
    *   `Headquarters_Location` se divide en `Headquarters_City` y `Headquarters_State` usando el delimitador coma.
    *   Se seleccionan y ordenan las columnas finales según lo especificado en `config.FINAL_COLUMNS`.

### 3.3. Carga de Datos
    *   Se establece una conexión con la base de datos `data/sp500_companies.db`.
    *   El DataFrame final transformado se guarda en la tabla `companies` utilizando el método `to_sql` de Pandas, con `if_exists='replace'`.

### 3.4. Visualización en Power BI
    *   La conexión a SQLite desde Power BI se realiza utilizando el conector ODBC genérico y una cadena de conexión que especifica el driver `SQLite3 ODBC Driver` y la ruta al archivo de la base de datos.
    *   Se crearon tres visualizaciones principales para responder a las preguntas:
        *   Un gráfico de barras para el "Top 5 Sectores por Número de empresas", utilizando un filtro Top N.
        *   Una tabla para las "10 Empresas Más Antiguas", ordenada por `Founded_Year` y filtrada por Top N con base en el mínimo de `Founded_Year`.
        *   Un gráfico de barras para el "Top 5 Estados por Sedes", utilizando un filtro Top N.
    *   Se ajustaron los formatos de los campos numéricos (como `Founded_Year`) para asegurar una correcta visualización como números enteros.

## 4. Principales Desafíos Encontrados y Soluciones

*   **Desafío 1:** Identificación correcta de la tabla HTML principal. Inicialmente, el script seleccionaba una tabla incorrecta (la de cambios históricos).
    *   **Solución:** Se implementó una lógica de selección de tabla más robusta. Primero, se intenta la selección directa y más precisa por el `id="constituents"`. Si esto falla, se aplica un segundo método que itera sobre todas las tablas `wikitable sortable` e identifica la correcta verificando la presencia de un encabezado distintivo como "GICS Sector". La depuración con `logging` fue crucial para identificar qué tabla y qué encabezados se estaban procesando.

*   **Desafío 2:** Conexión de Power BI a la base de datos SQLite. El conector nativo para SQLite no aparecía directamente en la lista de orígenes de datos de Power BI.
    *   **Solución:** Se investigó y se procedió a descargar e instalar el controlador ODBC de 64 bits para SQLite desde el sitio del desarrollador (ch-werner.de). Posteriormente, la conexión se estableció exitosamente en Power BI utilizando el conector ODBC genérico y la cadena de conexión `Driver={SQLite3 ODBC Driver};Database=<ruta_al_archivo.db>`.
    
*   **Desafío 3:** Visualización de años como números decimales en Power BI. El campo `Founded_Year` se mostraba con decimales (ej. 2.024,00).
    *   **Solución:** Se ajustó el formato de la columna `Founded_Year` directamente en Power BI, dentro de "Herramientas de columnas", estableciendo el tipo de dato y el formato a "Número entero" y las posiciones decimales a 0.

## 5. Posibles Mejoras Futuras

*   Incorporar un sistema de logging más avanzado, con diferentes niveles y salida a archivos para un mejor seguimiento y depuración en entornos productivos.
*   Mejorar el manejo de errores en la extracción web, implementando reintentos con backoff exponencial en caso de fallos de conexión o errores HTTP transitorios.
*   Desarrollar pruebas unitarias para las funciones clave de extracción y transformación, garantizando la calidad y fiabilidad del código.
*   Para un mayor volumen de datos o ejecuciones más frecuentes, se podría considerar migrar la base de datos a PostgreSQL o MySQL y utilizar un orquestador de pipelines como Apache Airflow.

## 6. Conclusión

El pipeline de datos desarrollado cumple satisfactoriamente con los requisitos del desafío técnico. Se ha logrado extraer información de la web, transformarla de manera significativa y cargarla en una base de datos local. Finalmente, los insights requeridos han sido presentados de forma clara y concisa mediante un dashboard interactivo en Power BI, respondiendo a todas las preguntas planteadas. Este proyecto demuestra la capacidad de construir un flujo de datos ETL completo utilizando herramientas y técnicas estándar en la ingeniería de datos.