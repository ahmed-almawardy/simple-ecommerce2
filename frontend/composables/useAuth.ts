import type { User } from '~/types'

export const useAuth = () => {
  const api = useApi()
  const token = useCookie<string | null>('token', { maxAge: 60 * 60 * 24 * 7, sameSite: 'lax' })
  const user = useState<User | null>('user', () => null)
  const cartStore = useCart()
  const loggedIn = computed(() => !!user.value)

  const fetchUser = async () => {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      user.value = await api<User>('/api/auth/me')
    } catch {
      token.value = null
      user.value = null
    }
  }

  const authenticate = async (path: string, body: Record<string, string>) => {
    const res = await api<{ access_token: string; user: User }>(path, { method: 'POST', body })
    token.value = res.access_token
    user.value = res.user
    await cartStore.load()
  }

  const login = (email: string, password: string) => authenticate('/api/auth/login', { email, password })
  const register = (full_name: string, email: string, password: string) =>
    authenticate('/api/auth/register', { full_name, email, password })

  const logout = async () => {
    token.value = null
    user.value = null
    cartStore.reset()
    await navigateTo('/')
  }

  return { user, loggedIn, token, fetchUser, login, register, logout }
}
