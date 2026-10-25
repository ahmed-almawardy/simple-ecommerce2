<script setup lang="ts">
// DEV ONLY: stands in for Stripe when STRIPE_SECRET_KEY is not configured on the backend.
definePageMeta({ middleware: 'auth' })
import type { Order } from '~/types'

const route = useRoute()
const api = useApi()
const orderId = route.query.order_id as string
const { data: order } = await useAsyncData('mock-order', () => api<Order>(`/api/orders/${orderId}`))
const loading = ref(false)
const error = ref('')

const payNow = async () => {
  loading.value = true
  try {
    await api(`/api/orders/${orderId}/mock-pay`, { method: 'POST' })
    await navigateTo({ path: '/checkout/success', query: { order_id: orderId } })
  } catch (e) {
    error.value = errMsg(e)
    loading.value = false
  }
}
</script>

<template>
  <div class="container" style="max-width: 560px; padding-bottom: 80px">
    <h1 class="page-title">Payment</h1>
    <div class="error" style="margin-bottom: 20px">
      Demo payment page. Stripe isn't configured, so no real card is charged. Set <b>STRIPE_SECRET_KEY</b> on the backend to use real payments.
    </div>
    <div v-if="order" class="summary" style="position: static">
      <h2>Order #{{ order.id }}</h2>
      <div v-for="i in order.items" :key="i.product_id" class="sum-item">
        <img :src="i.image_url" :alt="i.name" /><div>{{ i.name }}<div class="muted">Qty {{ i.quantity }}</div></div>
        <b>{{ money(i.unit_price_cents * i.quantity) }}</b>
      </div>
      <div class="row total"><span>Total</span><span>{{ money(order.total_cents) }}</span></div>
      <div v-if="error" class="error" style="margin-top: 12px">{{ error }}</div>
      <button class="btn block" style="margin-top: 20px" :disabled="loading" @click="payNow">
        {{ loading ? 'Processing…' : 'Simulate successful payment' }} <span>→</span>
      </button>
    </div>
  </div>
</template>
