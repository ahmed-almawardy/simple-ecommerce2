<script setup lang="ts">
import type { Category, ProductList } from '~/types'

const api = useApi()
const { data: categories } = await useAsyncData('categories', () => api<Category[]>('/api/categories'))
const { data: latest } = await useAsyncData('latest', () =>
  api<ProductList>('/api/products', { query: { sort: 'newest', page_size: 8 } }),
)
const { data: efficient } = await useAsyncData('efficient', () =>
  api<ProductList>('/api/products', { query: { energy: ['A'], sort: 'price_asc', page_size: 4 } }),
)
const hero = 'https://picsum.photos/seed/volta-hero/2000/1200'
const kitchenImg = 'https://picsum.photos/seed/volta-kitchen/1200/1000'
const smartImg = 'https://picsum.photos/seed/volta-smart/1200/1000'
</script>

<template>
  <div>
    <section class="hero" :style="{ backgroundImage: `url(${hero})` }">
      <div class="container hero-inner">
        <small>New season • Up to 5-year warranty</small>
        <h1>Power your home</h1>
        <p>Efficient appliances and smart electronics for every room. Free delivery over $99.</p>
        <div class="hero-actions">
          <NuxtLink :to="{ path: '/products', query: { category: 'kitchen' } }" class="btn white">Shop kitchen <span>→</span></NuxtLink>
          <NuxtLink :to="{ path: '/products', query: { sort: 'newest' } }" class="btn white">What's new <span>→</span></NuxtLink>
        </div>
      </div>
    </section>

    <div class="ticker">
      <div>
        <template v-for="n in 8" :key="n">
          <span>Free delivery over $99</span><span>⚡</span><span>Up to 5-year warranty</span><span>⚡</span><span>30-day returns</span><span>⚡</span>
        </template>
      </div>
    </div>

    <section class="section">
      <div class="container">
        <h2 class="section-title">Shop by room</h2>
        <div class="tiles" style="grid-template-columns: repeat(3, 1fr)">
          <NuxtLink
            v-for="c in categories"
            :key="c.id"
            :to="{ path: '/products', query: { category: c.slug } }"
            class="tile"
            style="aspect-ratio: 5 / 4"
          >
            <img :src="c.image_url" :alt="c.name" loading="lazy" />
            <div class="label"><b>{{ c.name }}</b><b>→</b></div>
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="section" style="padding-top: 0">
      <div class="container">
        <h2 class="section-title">
          New arrivals
          <NuxtLink :to="{ path: '/products', query: { sort: 'newest' } }" class="link-arrow">View all</NuxtLink>
        </h2>
        <div class="grid">
          <ProductCard v-for="p in latest?.items" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <section class="section" style="padding-top: 0">
      <div class="container split">
        <div class="panel" :style="{ backgroundImage: `url(${kitchenImg})` }">
          <div>
            <h3>Cook smarter</h3>
            <NuxtLink :to="{ path: '/products', query: { category: 'kitchen' } }" class="btn white">Kitchen appliances <span>→</span></NuxtLink>
          </div>
        </div>
        <div class="panel" :style="{ backgroundImage: `url(${smartImg})` }">
          <div>
            <h3>Make it smart</h3>
            <NuxtLink :to="{ path: '/products', query: { category: 'smart-home' } }" class="btn white">Smart home <span>→</span></NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <section v-if="efficient?.items.length" class="section" style="padding-top: 0">
      <div class="container">
        <h2 class="section-title">
          Most efficient (energy class A)
          <NuxtLink :to="{ path: '/products', query: { energy: ['A'] } }" class="link-arrow">View all</NuxtLink>
        </h2>
        <div class="grid">
          <ProductCard v-for="p in efficient.items" :key="p.id" :product="p" />
        </div>
      </div>
    </section>

    <section class="section" style="padding-top: 0">
      <div class="container usp">
        <div><b>🚚</b>Free delivery on orders over $99</div>
        <div><b>🛡</b>Manufacturer warranty on every product</div>
        <div><b>↩</b>30-day hassle-free returns</div>
        <div><b>🔒</b>Secure payment with Stripe</div>
      </div>
    </section>

    <section class="section" style="background: #000; color: #fff; text-align: center">
      <div class="container">
        <h2 style="font-size: clamp(34px, 6vw, 84px); margin-bottom: 18px">Join VOLTA</h2>
        <p style="max-width: 48ch; margin: 0 auto 28px; color: #ccc">
          Create an account for fast checkout, order tracking and member-only deals.
        </p>
        <NuxtLink to="/register" class="btn white">Sign up free <span>→</span></NuxtLink>
      </div>
    </section>
  </div>
</template>
