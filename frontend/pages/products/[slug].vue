<script setup lang="ts">
import type { Product, ProductList } from '~/types'

const route = useRoute()
const api = useApi()
const { loggedIn } = useAuth()
const { add } = useCart()
const { show } = useToast()

const slug = computed(() => route.params.slug as string)
const { data: product, error } = await useAsyncData(
  () => `product-${slug.value}`,
  () => api<Product>(`/api/products/${slug.value}`),
  { watch: [slug] },
)
if (error.value || !product.value) {
  throw createError({ statusCode: 404, statusMessage: 'Product not found', fatal: true })
}

const { data: related } = await useAsyncData(
  () => `related-${slug.value}`,
  () => api<ProductList>('/api/products', { query: { category: product.value!.category.slug, page_size: 5 } }),
  { watch: [slug] },
)
const others = computed(() => related.value?.items.filter((p) => p.id !== product.value?.id).slice(0, 4) || [])

const active = ref(0)
const qty = ref(1)
watch(slug, () => {
  active.value = 0
  qty.value = 1
})
const images = computed(() => (product.value?.images?.length ? product.value.images : [product.value!.image_url]))
const maxQty = computed(() => Math.min(10, product.value?.stock || 1))
const adding = ref(false)

const addToCart = async () => {
  if (!loggedIn.value) {
    return navigateTo({ path: '/login', query: { redirect: route.fullPath } })
  }
  adding.value = true
  try {
    await add(product.value!.id, qty.value)
    show(`${product.value!.name} added to your cart`)
  } catch (e) {
    show(errMsg(e), 'err')
  } finally {
    adding.value = false
  }
}

useHead({ title: () => `${product.value?.name} | VOLTA` })
</script>

<template>
  <div v-if="product" class="container">
    <div class="breadcrumb">
      <NuxtLink to="/">Home</NuxtLink> /
      <NuxtLink :to="{ path: '/products', query: { category: product.category.slug } }">{{ product.category.name }}</NuxtLink> /
      {{ product.name }}
    </div>

    <div class="pdp">
      <div class="gallery">
        <div class="thumbs">
          <button v-for="(img, i) in images" :key="img" :class="{ on: i === active }" :aria-label="`Photo ${i + 1}`" @click="active = i">
            <img :src="img" alt="" />
          </button>
        </div>
        <div class="mainimg"><img :src="images[active]" :alt="product.name" /></div>
      </div>

      <div class="pdp-info">
        <div class="kicker">{{ product.brand }} • {{ product.category.name }}</div>
        <h1>{{ product.name }}</h1>
        <div class="price">{{ money(product.price_cents) }}</div>
        <div v-if="product.energy_rating" style="margin: -8px 0 16px"><span class="energy" :class="product.energy_rating">Energy class {{ product.energy_rating }}</span></div>

        <div v-if="product.stock === 0" class="stock out">Sold out</div>
        <div v-else-if="product.stock <= 15" class="stock low">Only {{ product.stock }} left in stock</div>
        <div v-else class="stock ok">In stock</div>

        <div class="buy-row">
          <div class="qty">
            <button :disabled="qty <= 1" aria-label="Decrease" @click="qty--">−</button>
            <span>{{ qty }}</span>
            <button :disabled="qty >= maxQty" aria-label="Increase" @click="qty++">+</button>
          </div>
          <button class="btn" :disabled="product.stock === 0 || adding" @click="addToCart">
            {{ adding ? 'Adding…' : 'Add to cart' }} <span>→</span>
          </button>
        </div>

        <div class="perks">
          <div>🚚 Free delivery on orders over $99</div>
          <div>🛡 {{ product.warranty_months / 12 >= 1 ? `${product.warranty_months / 12}-year` : `${product.warranty_months}-month` }} manufacturer warranty</div>
          <div>↩ Free 30-day returns</div>
          <div>🔒 Secure checkout</div>
        </div>

        <h3 class="desc-title">Description</h3>
        <p class="desc">{{ product.description }}</p>

        <h3 v-if="Object.keys(product.specs).length" class="desc-title">Specifications</h3>
        <table v-if="Object.keys(product.specs).length" class="specs">
          <tbody>
            <tr v-for="(v, k) in product.specs" :key="k"><th>{{ k }}</th><td>{{ v }}</td></tr>
            <tr><th>Brand</th><td>{{ product.brand }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <section v-if="others.length" class="section" style="padding-top: 0">
      <h2 class="section-title">You may also like</h2>
      <div class="grid">
        <ProductCard v-for="p in others" :key="p.id" :product="p" />
      </div>
    </section>
  </div>
</template>
