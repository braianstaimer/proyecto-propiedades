import axios, { AxiosError } from 'axios'
import type {
  ErrorResponse,
  HealthResponse,
  SearchRequest,
  SearchResponse,
} from '@/types/api'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public httpStatus: number,
    public requestId?: string | null,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function normalizeError(err: unknown): ApiError {
  if (err instanceof AxiosError) {
    const status = err.response?.status ?? 0
    const body = err.response?.data as ErrorResponse | undefined
    if (body?.error) {
      return new ApiError(body.error.code, body.error.message, status, body.error.request_id)
    }
    if (err.code === 'ECONNABORTED') {
      return new ApiError('CLIENT_TIMEOUT', 'La búsqueda tardó más de lo esperado.', 0)
    }
    return new ApiError(
      'NETWORK_ERROR',
      'No se pudo conectar con el servidor. Verifique su conexión.',
      status,
    )
  }
  return new ApiError('UNKNOWN_ERROR', 'Error inesperado.', 0)
}

export async function searchProperties(payload: SearchRequest): Promise<SearchResponse> {
  try {
    const { data } = await apiClient.post<SearchResponse>('/api/search', payload)
    return data
  } catch (err) {
    throw normalizeError(err)
  }
}

export async function getHealth(): Promise<HealthResponse> {
  try {
    const { data } = await apiClient.get<HealthResponse>('/api/health')
    return data
  } catch (err) {
    throw normalizeError(err)
  }
}
