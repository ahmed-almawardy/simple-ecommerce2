import type { Cart } from '~/types'

const empty = (): Cart => ({ items: [], total_cents: 0, count: 0 })

export const useCart = () => {
  const api = useApi()
  const token = useCookie<string | null>('token')
  const cart = useState<Cart>('cart', empty)

  const load = async () => {
    if (!token.value) {
      cart.value = empty()
      return
    }
    try {
      cart.value = await api<Cart>('/api/cart')
    } catch {
      /* ignore: auth plugin handles bad tokens */
    }
  }
  const add = async (productId: number, quantity = 1) => {
    cart.value = await api<Cart>('/api/cart/items', { method: 'POST', body: { product_id: productId, quantity } })
  }
  const setQty = async (productId: number, quantity: number) => {
    cart.value = await api<Cart>(`/api/cart/items/${productId}`, { method: 'PATCH', body: { quantity } })
  }
  const remove = async (productId: number) => {
    cart.value = await api<Cart>(`/api/cart/items/${productId}`, { method: 'DELETE' })
  }
  const reset = () => {
    cart.value = empty()
  }
  return { cart, load, add, setQty, remove, reset }
}
