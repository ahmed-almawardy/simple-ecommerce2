<script setup lang="ts">
import type { Product } from '~/types'
defineProps<{ product: Product }>()
</script>

<template>
  <NuxtLink :to="`/products/${product.slug}`" class="card">
    <div class="media">
      <img :src="product.image_url" :alt="product.name" loading="lazy" />
      <span v-if="product.energy_rating" class="tag energy" :class="product.energy_rating">Energy {{ product.energy_rating }}</span>
      <span v-if="product.stock === 0" class="tag">Sold out</span>
      <span v-else-if="product.stock <= 15" class="tag low">Only {{ product.stock }} left</span>
    </div>
    <div class="info">
      <div class="price">{{ money(product.price_cents) }}</div>
      <div class="name">{{ product.name }}</div>
      <div class="meta">{{ product.brand }} • {{ product.category.name }}</div>
    </div>
  </NuxtLink>
</template>
