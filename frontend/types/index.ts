export interface User {
  id: number
  email: string
  full_name: string
}

export interface Category {
  id: number
  name: string
  slug: string
  image_url: string
}

export interface Product {
  id: number
  name: string
  slug: string
  description: string
  price_cents: number
  image_url: string
  images: string[]
  stock: number
  brand: string
  energy_rating: string
  warranty_months: number
  specs: Record<string, string>
  category: Category
}

export interface ProductList {
  items: Product[]
  total: number
  page: number
  page_size: number
}

export interface Facets {
  brands: string[]
  energy_ratings: string[]
  min_price_cents: number
  max_price_cents: number
}

export interface CartItem {
  product: Product
  quantity: number
  line_total_cents: number
}

export interface Cart {
  items: CartItem[]
  total_cents: number
  count: number
}

export interface OrderItem {
  product_id: number
  name: string
  image_url: string
  unit_price_cents: number
  quantity: number
}

export interface Order {
  id: number
  status: string
  total_cents: number
  created_at: string
  paid_at: string | null
  full_name: string
  address: string
  city: string
  postal_code: string
  country: string
  items: OrderItem[]
}
