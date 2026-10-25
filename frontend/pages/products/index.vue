<script setup lang="ts">
import type { Category, Facets, ProductList } from '~/types'

const route = useRoute()
const router = useRouter()
const api = useApi()
const showFilters = ref(false)

const pick = (v: unknown) => (Array.isArray(v) ? v[0] : v) as string | undefined
const category = computed(() => pick(route.query.category))
const search = computed(() => pick(route.query.q))
const sort = computed(() => pick(route.query.sort) || 'newest')
const page = computed(() => Number(pick(route.query.page)) || 1)
const minPrice = computed(() => pick(route.query.min_price))
const maxPrice = computed(() => pick(route.query.max_price))
const inStock = computed(() => pick(route.query.in_stock) === '1')
const brands = computed(() => [route.query.brand].flat().filter(Boolean) as string[])
const energy = computed(() => [route.query.energy].flat().filter(Boolean) as string[])

const { data: categories } = await useAsyncData('categories', () => api<Category[]>('/api/categories'))
const { data: facets } = await useAsyncData(
  'facets',
  () => api<Facets>('/api/facets', { query: { category: category.value } }),
  { watch: [category] },
)
const { data, pending } = await useAsyncData(
  'plp',
  () =>
    api<ProductList>('/api/products', {
      query: {
        category: category.value,
        energy: energy.value,
        q: search.value,
        brand: brands.value,
        min_price: minPrice.value,
        max_price: maxPrice.value,
        in_stock: inStock.value || undefined,
        sort: sort.value,
        page: page.value,
        page_size: 12,
      },
    }),
  { watch: [() => route.query] },
)

const totalPages = computed(() => Math.max(1, Math.ceil((data.value?.total || 0) / 12)))

const setQuery = (patch: Record<string, any>, keepPage = false) => {
  const next: Record<string, any> = { ...route.query, ...patch }
  if (!keepPage) delete next.page
  for (const k of Object.keys(next)) {
    const v = next[k]
    if (v === undefined || v === null || v === '' || (Array.isArray(v) && !v.length)) delete next[k]
  }
  router.push({ path: '/products', query: next })
}

const toggleBrand = (b: string) =>
  setQuery({ brand: brands.value.includes(b) ? brands.value.filter((x) => x !== b) : [...brands.value, b] })

const toggleEnergy = (r: string) =>
  setQuery({ energy: energy.value.includes(r) ? energy.value.filter((x) => x !== r) : [...energy.value, r] })

const minInput = ref(minPrice.value || '')
const maxInput = ref(maxPrice.value || '')
watch([minPrice, maxPrice], () => {
  minInput.value = minPrice.value || ''
  maxInput.value = maxPrice.value || ''
})
const applyPrice = () => setQuery({ min_price: minInput.value, max_price: maxInput.value })

const title = computed(() => {
  if (search.value) return `Results for “${search.value}”`
  const cat = categories.value?.find((c) => c.slug === category.value)?.name
  return cat || 'All appliances'
})

const chips = computed(() => {
  const out: { label: string; clear: () => void }[] = []
  if (category.value) out.push({ label: categories.value?.find((c) => c.slug === category.value)?.name || category.value, clear: () => setQuery({ category: undefined }) })
  energy.value.forEach((r) => out.push({ label: `Energy ${r}`, clear: () => toggleEnergy(r) }))
  if (search.value) out.push({ label: `“${search.value}”`, clear: () => setQuery({ q: undefined }) })
  brands.value.forEach((b) => out.push({ label: b, clear: () => toggleBrand(b) }))
  if (minPrice.value || maxPrice.value) out.push({ label: `$${minPrice.value || 0} – ${maxPrice.value ? '$' + maxPrice.value : 'any'}`, clear: () => setQuery({ min_price: undefined, max_price: undefined }) })
  if (inStock.value) out.push({ label: 'In stock', clear: () => setQuery({ in_stock: undefined }) })
  return out
})

useHead({ title: () => `${title.value} | VOLTA` })
</script>

<template>
  <div class="container">
    <div class="breadcrumb"><NuxtLink to="/">Home</NuxtLink> / Products</div>
    <div class="plp-head">
      <h1>{{ title }}<span class="count">({{ data?.total ?? 0 }})</span></h1>
      <div style="display: flex; gap: 10px">
        <button class="btn ghost filter-toggle" @click="showFilters = !showFilters">Filters</button>
        <select class="select" :value="sort" aria-label="Sort" @change="setQuery({ sort: ($event.target as HTMLSelectElement).value })">
          <option value="newest">Newest</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
          <option value="name">Name A–Z</option>
        </select>
      </div>
    </div>

    <div v-if="chips.length" class="chips">
      <button v-for="c in chips" :key="c.label" class="chip" @click="c.clear">{{ c.label }} ✕</button>
      <button class="chip" style="border-style: dashed" @click="router.push('/products')">Clear all</button>
    </div>

    <div class="plp">
      <aside class="filters" :class="{ open: showFilters }">
        <div class="fgroup">
          <h4>Category</h4>
          <label><input type="radio" name="cat" :checked="!category" @change="setQuery({ category: undefined })" /> All</label>
          <label v-for="c in categories" :key="c.id">
            <input type="radio" name="cat" :checked="category === c.slug" @change="setQuery({ category: c.slug })" /> {{ c.name }}
          </label>
        </div>
        <div class="fgroup">
          <h4>Price ($)</h4>
          <form class="price-row" @submit.prevent="applyPrice">
            <input v-model="minInput" type="number" min="0" :placeholder="String(Math.floor((facets?.min_price_cents || 0) / 100))" aria-label="Min price" />
            <span>–</span>
            <input v-model="maxInput" type="number" min="0" :placeholder="String(Math.ceil((facets?.max_price_cents || 0) / 100))" aria-label="Max price" />
            <button class="btn" style="padding: 10px 14px">Go</button>
          </form>
        </div>
        <div v-if="facets?.brands.length" class="fgroup">
          <h4>Brand</h4>
          <label v-for="b in facets.brands" :key="b">
            <input type="checkbox" :checked="brands.includes(b)" @change="toggleBrand(b)" /> {{ b }}
          </label>
        </div>
        <div v-if="facets?.energy_ratings.length" class="fgroup">
          <h4>Energy rating</h4>
          <label v-for="r in facets.energy_ratings" :key="r">
            <input type="checkbox" :checked="energy.includes(r)" @change="toggleEnergy(r)" />
            <span class="energy" :class="r">{{ r }}</span>
          </label>
        </div>
        <div class="fgroup">
          <label><input type="checkbox" :checked="inStock" @change="setQuery({ in_stock: inStock ? undefined : '1' })" /> In stock only</label>
        </div>
      </aside>

      <section>
        <div v-if="pending && !data" class="grid"><div v-for="n in 8" :key="n" class="skeleton" /></div>
        <div v-else-if="data?.items.length" class="grid" :style="{ opacity: pending ? 0.5 : 1 }">
          <ProductCard v-for="p in data.items" :key="p.id" :product="p" />
        </div>
        <div v-else class="empty">
          <h3>No products found</h3>
          <p class="muted">Try removing a filter or searching for something else.</p>
          <button class="btn" @click="router.push('/products')">Clear filters</button>
        </div>

        <div v-if="totalPages > 1" class="pager">
          <button :disabled="page <= 1" @click="setQuery({ page: page - 1 }, true)">←</button>
          <button v-for="n in totalPages" :key="n" :class="{ on: n === page }" @click="setQuery({ page: n }, true)">{{ n }}</button>
          <button :disabled="page >= totalPages" @click="setQuery({ page: page + 1 }, true)">→</button>
        </div>
      </section>
    </div>
  </div>
</template>
