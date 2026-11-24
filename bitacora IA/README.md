# Bitácora de uso de IA

## 14/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 14/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Implementación del API Gateway y flujo de autenticación centralizada con JWT (ms-usuarios). |
| **Prompt utilizado (resumen)** | "Ayúdame a configurar el enrutamiento del api-gateway hacia los microservicios y validar el esquema de autenticación Bearer JWT desde ms-usuarios." |
| **Nivel de intervención humana** | Alto |
| **Resultado / aprendizaje** | Se estructuraron las rutas proxy en el Gateway y la validación de tokens. Se ajustaron los endpoints y respuestas JSON para trabajar con el usuario real de pruebas y se verificó el flujo de login en Thunder Client. |

## 15/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 15/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Integración de los microservicios de catálogo (ms-productos, ms-proveedores) y registro de inventario (ms-inventario). |
| **Prompt utilizado (resumen)** | "Apóyame en la validación de entradas en ms-inventario consultando ms-productos vía HTTP y el cálculo de stock actual por bodega." |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | Se implementó la verificación remota de productos antes de registrar entradas (POST /api/inventario/entradas) manejando códigos 422, 502 y 503, y se validó el cálculo dinámico de stock mediante suma de movimientos. |

## 16/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 16/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Comunicación segura e idempotencia entre ms-ordenes y ms-inventario para recepciones de compra. |
| **Prompt utilizado (resumen)** | "Revisa el endpoint POST /api/inventario/recepciones para asegurar que solo acepte peticiones de ms-ordenes y evite recepciones duplicadas." |
| **Nivel de intervención humana** | Alto |
| **Resultado / aprendizaje** | Se aplicó validación mediante cabecera interna (X-Ordenes-Key con hash\_equals), transacciones en base de datos y control de duplicados por huella SHA-256 (409 Conflict), asegurando integridad en el ingreso de mercancía. |

## 18/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 18/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Contenerización multi-lenguaje (Laravel, Flask, Node.js) con Dockerfiles y orquestación en docker-compose.yml. |
| **Prompt utilizado (resumen)** | "Ayúdame a estructurar los Dockerfiles, docker-compose.yml, init.sql y .env.example para ejecutar SisInv en Windows y Ubuntu sin Kubernetes ni multi-stage builds." |
| **Nivel de intervención humana** | Alto |
| **Resultado / aprendizaje** | Se definieron los 6 contenedores de aplicación y el contenedor de MySQL con aprovisionamiento de bases de datos independientes (init.sql). Se aprendió a desacoplar credenciales mediante .env y garantizar portabilidad entre sistemas operativos. |

## 19/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 19/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Depuración de red interna en Docker y configuración de config/services.php en ms-inventario. |
| **Prompt utilizado (resumen)** | "En ms-inventario, ¿la variable MS\_PRODUCTOS\_URL dentro de docker-compose.yml debe apuntar a http\://ms-productos:8002 o a 127.0.0.1:8002?" |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | Se detectó que faltaba inyectar MS\_PRODUCTOS\_URL en el servicio de inventario dentro de Docker Compose. Se comprendió la resolución DNS interna de la red sisinv-net frente al localhost aislado de cada contenedor. |

## 20/11/2026 · Miguel Ángel Ocampo

| Campo | Registro |
| --- | --- |
| **Fecha** | 20/11/2026 |
| **Integrante** | Miguel Ángel Ocampo |
| **Herramienta de IA** | Codex |
| **Tarea / actividad apoyada** | Implementación del microservicio de Inventario en Laravel. |
| **Prompt utilizado (resumen)** | Ayúdame a crear un servicio para registrar bodegas y entradas de mercancía, validar los productos y consultar el stock por bodega desde el API Gateway. |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | Se implementó el registro de bodegas y entradas. Inventario consulta al servicio de Productos para comprobar que el producto existe y calcula el saldo sumando las entradas por producto y bodega. |

## 20/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 20/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Auditoría de alineación con la Entrega 2 e implementación del endpoint de Kardex en ms-inventario. |
| **Prompt utilizado (resumen)** | "Verifica en el documento de la Segunda Entrega si incluimos el Kardex y ayúdame a exponer GET .../kardex en routes/api.php e InventarioController.php." |
| **Nivel de intervención humana** | Alto |
| **Resultado / aprendizaje** | Se confirmó la entidad MOVIMIENTOS KARDEX en el MER de MS-INVENTARIOS. Se implementó el cálculo cronológico de tipo\_movimiento, cantidad\_delta, saldo\_posterior y saldo\_actual reutilizando la tabla entradas, validando el 200 OK vía API Gateway. |

## 21/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 21/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Diseño de la matriz de 15 pruebas de rendimiento y creación del script locustfile.py automatizado en PowerShell. |
| **Prompt utilizado (resumen)** | "Estructura las 15 pruebas de rendimiento (Carga, Estrés y Capacidad) en Locust sobre los 5 flujos clave de SisInv y automatiza la generación de reportes." |
| **Nivel de intervención humana** | Bajo |
| **Resultado / aprendizaje** | Se definieron 5 flujos (login, productos, stock, kardex, entradas) × 3 perfiles de concurrencia. Se parametrizó locustfile.py con credenciales y UUIDs reales y se ejecutó la batería en modo \--headless exportando CSV y HTML. |

## 22/11/2026 · Cristian Camilo González Villa

| Campo | Registro |
| --- | --- |
| **Fecha** | 22/11/2026 |
| **Integrante** | Cristian Camilo González Villa |
| **Herramienta de IA** | Gemini |
| **Tarea / actividad apoyada** | Diagnóstico de cuellos de botella en Locust (setup: login y WinError 10061), creación del Dashboard HTML y análisis preliminar. |
| **Prompt utilizado (resumen)** | "Analiza los fallos de setup: login y WinError 10061 en Locust, genera un dashboard visual a partir de los CSV y ayúdame a interpretar las anomalías de las pruebas de Carga." |
| **Nivel de intervención humana** | Alto |
| **Resultado / aprendizaje** | Se refactorizó locustfile.py para compartir un único JWT en @events.test\_start, se creó generar\_dashboard.py (Chart.js \+ semáforo) y se identificó que la cola residual de CAPACIDAD causó 401 en CARGA, documentando el techo de \~4 RPS del servidor monohilo de desarrollo y el costo de bcrypt en /login. |

## 20/11/2026 · Miguel Ángel Ocampo

| Campo | Registro |
| --- | --- |
| **Fecha** | 20/11/2026 |
| **Integrante** | Miguel Ángel Ocampo |
| **Herramienta de IA** | Codex |
| **Tarea / actividad apoyada** | Implementación del microservicio de Proveedores en Flask. |
| **Prompt utilizado (resumen)** | Ayúdame a crear un servicio para registrar, buscar, editar y dar de baja proveedores, con acceso desde el API Gateway. |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | Se implementó la gestión de proveedores con SQLite, validación de identificaciones tributarias duplicadas y permisos de administrador para los cambios. La baja lógica conserva el registro del proveedor. |

## 21/11/2026 · Miguel Ángel Ocampo

| Campo | Registro |
| --- | --- |
| **Fecha** | 21/11/2026 |
| **Integrante** | Miguel Ángel Ocampo |
| **Herramienta de IA** | Codex |
| **Tarea / actividad apoyada** | Implementación de Órdenes de Compra en Express e integración con Inventario. |
| **Prompt utilizado (resumen)** | Ayúdame a crear y consultar órdenes de compra, y a recibirlas en una bodega sin duplicar el stock si se repite la solicitud. |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | La orden pasa de `PENDIENTE` a `RECIBIDA` después de registrar la mercancía en Inventario. En una prueba, el stock pasó de 0 a 10 unidades y se mantuvo en 10 al repetir la recepción. |

## 23/11/2026 · Miguel Ángel Ocampo

| Campo | Registro |
| --- | --- |
| **Fecha** | 23/11/2026 |
| **Integrante** | Miguel Ángel Ocampo |
| **Herramienta de IA** | Codex |
| **Tarea / actividad apoyada** | Ampliación de las pruebas de rendimiento con Locust. |
| **Prompt utilizado (resumen)** | Revisa qué endpoints faltan en las pruebas de rendimiento y agrega escenarios para medirlos con 5, 20 y 40 usuarios simulados. |
| **Nivel de intervención humana** | Medio |
| **Resultado / aprendizaje** | Se agregaron escenarios para 12 endpoints y se prepararon 36 corridas. Las solicitudes de preparación de datos quedaron fuera de las métricas de cada operación. |
