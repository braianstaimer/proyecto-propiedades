---
sidebar_position: 1
title: GET /api/health
---

# `GET /api/health`

Endpoint de salud que reporta estado de los componentes externos.

## Request

```bash
curl http://localhost:8000/api/health
```

Sin headers obligatorios. Acepta `X-Request-ID` para correlación.

## Response 200

```json
{
  "status": "ok",
  "db": "ok",
  "llm": "ok",
  "version": "0.1.0"
}
```

## Semántica

| Campo | Valores | Significado |
|---|---|---|
| `status` | `ok` \| `degraded` | `ok` si ambos `db` y `llm` responden; `degraded` si alguno cae |
| `db` | `ok` \| `down` | `SELECT 1` contra MySQL responde |
| `llm` | `ok` \| `down` | `GET /api/tags` contra Ollama responde |
| `version` | `string` | Versión del paquete (`app.__version__`) |

## Uso recomendado

- **Liveness probe** (k8s `livenessProbe`): basta status code 200.
- **Readiness probe** (k8s `readinessProbe`): condicionar a `status == "ok"`.
- **Diagnóstico desde el frontend:** si `llm == "down"` mostrar banner "Servicio de IA temporalmente inactivo".

## Comportamiento de error

- El endpoint **nunca devuelve 5xx** salvo bug interno; los fallos de DB/LLM se reportan en el body con `down`.
- Esto permite que el balanceador siga sirviendo `/api/health` aunque el dominio esté caído.

## Implementación

Ver [`backend/app/routes.py::health`](https://github.com/braianstaimer/proyecto-propiedades-backend/blob/main/app/routes.py). Delega a:

- `PropertyRepository.healthcheck()` → `SELECT 1`
- `LLMProvider.healthcheck()` → `GET {OLLAMA_URL}/api/tags`
