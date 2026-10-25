<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
import type { Order } from '~/types'

const api = useApi()
const { data: orders } = await useAsyncData('orders', () => api<Order[]>('/api/orders'))
const date = (s: string) => new Date(s + 'Z').toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
useHead({ title: 'My orders | VOLTA' })
</script>

<template>
  <div class="container" style="padding-bottom: 80px">
    <h1 class="page-title">My orders</h1>
    <div v-if="!orders?.length" class="empty" style="padding-top: 20px">
      <h3>No orders yet</h3>
      <NuxtLink to="/products" class="btn">Start shopping <span>→</span></NuxtLink>
    </div>
    <div v-for="o in orders" :key="o.id" class="order-card">
      <div class="order-head">
        <span><b>Order #{{ o.id }}</b> • {{ date(o.created_at) }}</span>
        <span><span class="status" :class="o.status">{{ o.status }}</span> &nbsp; <b>{{ money(o.total_cents) }}</b></span>
      </div>
      <div class="order-body">
        <div v-for="i in o.items" :key="i.product_id" class="sum-item">
          <img :src="i.image_url" :alt="i.name" /><div>{{ i.name }}<div class="muted">Qty {{ i.quantity }}</div></div>
          <b>{{ money(i.unit_price_cents * i.quantity) }}</b>
        </div>
      </div>
    </div>
  </div>
</template>
