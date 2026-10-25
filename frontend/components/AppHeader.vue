<script setup lang="ts">
import type { Category } from '~/types'

const route = useRoute()
const { user, loggedIn, logout } = useAuth()
const { cart } = useCart()
const api = useApi()
const { data: categories } = await useAsyncData('categories', () => api<Category[]>('/api/categories'))

const q = ref('')
const open = ref(false)
const search = () => {
  navigateTo({ path: '/products', query: q.value ? { q: q.value } : {} })
  open.value = false
}
watch(() => route.fullPath, () => (open.value = false))
</script>

<template>
  <header>
    <div class="announce">Free delivery over $99 &nbsp;•&nbsp; 30-day free returns</div>
    <div class="header">
      <div class="container header-top">
        <button class="menu-btn" aria-label="Menu" @click="open = !open">☰</button>
        <NuxtLink to="/" class="logo"><span>⚡</span>VOLTA</NuxtLink>
        <nav class="nav" :class="{ open }">
          <NuxtLink :to="{ path: '/products', query: { sort: 'newest' } }">New</NuxtLink>
          <NuxtLink v-for="c in categories" :key="c.id" :to="{ path: '/products', query: { category: c.slug } }">
            {{ c.name }}
          </NuxtLink>
        </nav>
        <div class="header-right">
          <form class="search" @submit.prevent="search">
            <input v-model="q" type="search" placeholder="Search appliances" aria-label="Search products" />
          </form>
          <div v-if="loggedIn" class="user-menu">
            <NuxtLink to="/orders">Orders</NuxtLink>
            <span class="hello">Hi, {{ user?.full_name.split(' ')[0] }}</span>
            <button @click="logout">Log out</button>
          </div>
          <NuxtLink v-else to="/login" class="icon-link">Log in</NuxtLink>
          <NuxtLink to="/cart" class="icon-link" aria-label="Cart">
            🛍<span v-if="cart.count" class="badge">{{ cart.count }}</span>
          </NuxtLink>
        </div>
      </div>
    </div>
  </header>
</template>
