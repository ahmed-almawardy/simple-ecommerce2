/** Thin $fetch wrapper that targets the FastAPI backend and attaches the JWT. */
export const useApi = () => {
  const config = useRuntimeConfig()
  const token = useCookie<string | null>('token')
  return <T = any>(path: string, opts: Record<string, any> = {}) =>
    $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...opts,
      headers: {
        ...(opts.headers || {}),
        ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
      },
    })
}
