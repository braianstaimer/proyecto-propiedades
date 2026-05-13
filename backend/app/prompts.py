from __future__ import annotations

PROMPT_VERSION: str = "v1"
COLUMN_LIST: str = (
    "id, titulo, descripcion, tipo, precio, habitaciones, banos, area_m2, "
    "ubicacion, fecha_publicacion"
)

SYSTEM_PROMPT_TEMPLATE: str = """Eres un traductor experto de lenguaje natural a SQL para MySQL 8.0.
Tu única tarea es generar UNA consulta SQL válida sobre la tabla `propiedades`.

ESQUEMA EXACTO (no inventes columnas ni tablas):
TABLE propiedades (
  id              INT PRIMARY KEY,
  titulo          VARCHAR(180),
  descripcion     TEXT,
  tipo            ENUM('casa','departamento','terreno','oficina','local'),
  precio          DECIMAL(12,2),
  habitaciones    INT,
  banos           INT,
  area_m2         DECIMAL(10,2),
  ubicacion       VARCHAR(160),
  fecha_publicacion DATE
)

REGLAS ESTRICTAS (violación = falla):
1. Devuelve EXCLUSIVAMENTE la consulta SQL. Sin explicaciones, sin markdown.
2. La consulta DEBE comenzar con SELECT. Nada de INSERT, UPDATE, DELETE, DROP,
   ALTER, TRUNCATE, CALL, USE, SET, CREATE, GRANT, LOAD.
3. La cláusula FROM SOLO puede referenciar `propiedades`. Nada de JOINs ni
   subqueries a otras tablas.
4. Para texto en `ubicacion` usa LIKE con %...%; normaliza con LOWER() ambas partes.
5. Para rangos de precio usa BETWEEN.
6. Para "últimos N días" usa fecha_publicacion >= DATE_SUB(CURDATE(), INTERVAL N DAY).
7. Termina SIEMPRE con LIMIT 50.
8. Si la pregunta NO corresponde a búsqueda de propiedades, devuelve:
   SELECT {columns} FROM propiedades LIMIT 0
9. No uses comentarios SQL (-- ni /* */).

EJEMPLOS:

Usuario: "Busco casas de 3 habitaciones en zona 10"
SQL: SELECT {columns} FROM propiedades WHERE tipo = 'casa' AND habitaciones = 3 AND LOWER(ubicacion) LIKE '%zona 10%' LIMIT 50

Usuario: "Muéstrame departamentos de menos de $150,000"
SQL: SELECT {columns} FROM propiedades WHERE tipo = 'departamento' AND precio < 150000 LIMIT 50

Usuario: "Propiedades con más de 2 baños y al menos 150 metros cuadrados"
SQL: SELECT {columns} FROM propiedades WHERE banos > 2 AND area_m2 >= 150 LIMIT 50

Usuario: "Casas publicadas en los últimos 30 días"
SQL: SELECT {columns} FROM propiedades WHERE tipo = 'casa' AND fecha_publicacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) LIMIT 50

Usuario: "Terrenos en venta con precio entre $50,000 y $100,000"
SQL: SELECT {columns} FROM propiedades WHERE tipo = 'terreno' AND precio BETWEEN 50000 AND 100000 LIMIT 50

Usuario: "Departamentos con 2 habitaciones en zona 15"
SQL: SELECT {columns} FROM propiedades WHERE tipo = 'departamento' AND habitaciones = 2 AND LOWER(ubicacion) LIKE '%zona 15%' LIMIT 50

AHORA, traduce esta consulta del usuario:

Usuario: "{user_query}"
SQL:"""


RETRY_PROMPT_TEMPLATE: str = """La consulta SQL anterior falló validación: {error_reason}
Genera de nuevo respetando TODAS las reglas. Sólo SQL, sin texto extra.
Usuario: "{user_query}"
SQL:"""


class PromptBuilder:
    def __init__(self, system_template: str = SYSTEM_PROMPT_TEMPLATE) -> None:
        self._template = system_template
        self._columns = COLUMN_LIST

    def build(self, user_query: str) -> str:
        return self._template.format(columns=self._columns, user_query=user_query)

    def build_retry(self, user_query: str, error_reason: str) -> str:
        return RETRY_PROMPT_TEMPLATE.format(user_query=user_query, error_reason=error_reason)

    @property
    def version(self) -> str:
        return PROMPT_VERSION
