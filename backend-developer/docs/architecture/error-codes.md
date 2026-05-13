---
sidebar_position: 1
title: Catálogo de errores
---

# Catálogo de errores

Todos los errores se devuelven con el envelope:

```json
{
  "error": {
    "code": "LLM_TIMEOUT",
    "message": "El modelo tardó más del tiempo permitido. Intente de nuevo.",
    "detail": null,
    "request_id": "01H8X..."
  }
}
```

## Tabla completa

| HTTP | `error.code` | Cuándo | Acción del cliente |
|---|---|---|---|
| 422 | `EMPTY_QUERY` | query vacía o > 500 chars | Validar antes de enviar |
| 422 | `LLM_TIMEOUT` | Ollama tardó > 15s | Reintentar con query más corta |
| 422 | `LLM_INVALID_OUTPUT` | LLM no devolvió SQL parseable | Reformular la consulta |
| 422 | `SQL_NOT_SELECT` | El SQL generado contiene DML/DDL | Reformular (la IA "se confundió") |
| 422 | `SQL_FORBIDDEN_TABLE` | Tabla distinta a `propiedades` | Sólo se permite buscar propiedades |
| 422 | `SQL_FORBIDDEN_STATEMENT` | Multi-statement (`;` con segunda sentencia) | Reformular |
| 422 | `SQL_DANGEROUS_FUNCTION` | SLEEP/BENCHMARK/LOAD_FILE/INTO OUTFILE | Reformular |
| 429 | `RATE_LIMIT` | > N requests/min/IP (si hardening activo) | Esperar `Retry-After` segundos |
| 500 | `DB_ERROR` | Falla en MySQL | Reintentar; verificar status DB |
| 503 | `LLM_UNAVAILABLE` | Ollama no responde / DNS falla | Esperar y reintentar; verificar `ollama serve` |

## Errores client-side (envelope espejo)

Generados por el cliente axios cuando no hay respuesta JSON del servidor:

| `error.code` | Cuándo |
|---|---|
| `CLIENT_TIMEOUT` | `axios` abortó por timeout (default 30s) |
| `NETWORK_ERROR` | Fallo de red, DNS o servidor caído |
| `UNKNOWN_ERROR` | Cualquier otro throw |

## Diseño

- **Códigos son `SCREAMING_SNAKE_CASE`** para que el frontend pueda mapear a mensajes humanos.
- **`message`** es texto en español listo para mostrar al usuario.
- **`detail`** sólo aparece en modo dev/debug.
- **`request_id`** es opcional pero se propaga vía header `X-Request-ID` (si el cliente lo envía, se respeta; si no, se genera UUID).
