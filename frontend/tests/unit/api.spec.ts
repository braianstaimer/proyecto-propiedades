import { describe, it, expect, beforeEach, vi } from 'vitest'
import { AxiosError } from 'axios'

vi.mock('axios', async () => {
  const actual = await vi.importActual<typeof import('axios')>('axios')
  return {
    ...actual,
    default: {
      ...actual.default,
      create: vi.fn(() => ({
        post: vi.fn(),
        get: vi.fn(),
        defaults: { headers: { common: {} } },
        interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
      })),
    },
  }
})

describe('api service', () => {
  beforeEach(() => {
    vi.resetModules()
  })

  it('searchProperties returns SearchResponse on 200', async () => {
    const { apiClient, searchProperties } = await import('@/services/api')
    apiClient.post = vi.fn().mockResolvedValue({
      data: { query: 'x', sql: 'SELECT 1 FROM propiedades', count: 0, results: [], took_ms: 1 },
    })
    const result = await searchProperties({ query: 'x' })
    expect(result.count).toBe(0)
    expect(result.sql).toContain('SELECT')
  })

  it('searchProperties throws ApiError with envelope code on 4xx', async () => {
    const { apiClient, searchProperties, ApiError } = await import('@/services/api')
    const axiosErr = new AxiosError('Request failed')
    Object.assign(axiosErr, {
      response: {
        status: 422,
        data: {
          error: { code: 'LLM_TIMEOUT', message: 'tarde', detail: null, request_id: 'r-1' },
        },
      },
    })
    apiClient.post = vi.fn().mockRejectedValue(axiosErr)
    await expect(searchProperties({ query: 'x' })).rejects.toBeInstanceOf(ApiError)
    try {
      await searchProperties({ query: 'x' })
    } catch (e) {
      const err = e as InstanceType<typeof ApiError>
      expect(err.code).toBe('LLM_TIMEOUT')
      expect(err.message).toBe('tarde')
      expect(err.httpStatus).toBe(422)
      expect(err.requestId).toBe('r-1')
    }
  })

  it('searchProperties maps timeout to CLIENT_TIMEOUT', async () => {
    const { apiClient, searchProperties, ApiError } = await import('@/services/api')
    const axiosErr = new AxiosError('timeout')
    Object.assign(axiosErr, { code: 'ECONNABORTED' })
    apiClient.post = vi.fn().mockRejectedValue(axiosErr)
    await expect(searchProperties({ query: 'x' })).rejects.toMatchObject({
      code: 'CLIENT_TIMEOUT',
    })
  })

  it('searchProperties maps generic axios error to NETWORK_ERROR', async () => {
    const { apiClient, searchProperties } = await import('@/services/api')
    apiClient.post = vi.fn().mockRejectedValue(new AxiosError('boom'))
    await expect(searchProperties({ query: 'x' })).rejects.toMatchObject({
      code: 'NETWORK_ERROR',
    })
  })

  it('searchProperties maps non-axios throws to UNKNOWN_ERROR', async () => {
    const { apiClient, searchProperties } = await import('@/services/api')
    apiClient.post = vi.fn().mockRejectedValue(new Error('weird'))
    await expect(searchProperties({ query: 'x' })).rejects.toMatchObject({
      code: 'UNKNOWN_ERROR',
    })
  })

  it('getHealth returns HealthResponse on 200', async () => {
    const { apiClient, getHealth } = await import('@/services/api')
    apiClient.get = vi.fn().mockResolvedValue({
      data: { status: 'ok', db: 'ok', llm: 'ok', version: '0.1.0' },
    })
    const result = await getHealth()
    expect(result.status).toBe('ok')
    expect(result.version).toBe('0.1.0')
  })
})
