// Tipos espejo del contrato OpenAPI. Regenerable con `npm run gen:types`.

export type TipoPropiedad = 'casa' | 'departamento' | 'terreno' | 'oficina' | 'local'

export interface PropertyOut {
  id: number
  titulo: string
  descripcion: string | null
  tipo: TipoPropiedad
  precio: number
  habitaciones: number | null
  banos: number | null
  area_m2: number | null
  ubicacion: string
  fecha_publicacion: string
}

export interface SearchRequest {
  query: string
}

export interface SearchResponse {
  query: string
  sql: string
  count: number
  results: PropertyOut[]
  took_ms: number
}

export interface ErrorDetail {
  code: string
  message: string
  detail: string | null
  request_id: string | null
}

export interface ErrorResponse {
  error: ErrorDetail
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  db: 'ok' | 'down'
  llm: 'ok' | 'down'
  version: string
}
