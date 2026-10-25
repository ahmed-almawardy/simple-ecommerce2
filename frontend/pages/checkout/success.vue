<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
import type { Order } from '~/types'

const route = useRoute()
const api = useApi()
const { load } = useCart()

const order = ref<Order | null>(null)
const error = ref('')

onMounted(async () => {
  try {
    const sid = route.query.session_id as string | undefined
    order.value = sid
      ? await api<Order>('/api/orders/confirm', { method: 'POST', body: { session_id: sid } })
      : await api<Order>(`/api/orders/${route.query.order_id}`)
    await load()
  } catch (e) {
    error.value = errMsg(e)
  }
})
useHead({ title: 'Order confirmed | VOLTA' })
</script>

<template>
  <div class="container" style="max-width: 760px; padding-bottom: 80px">
    <div v-if="error" class="empty"><h3>We couldn't load your order</h3><p class="muted">{{ error }}</p><NuxtLink to="/orders" class="btn">My orders</NuxtLink></div>
    <div v-else-if="!order" class="empty muted">Confirming your payment…</div>
    <template v-else>
      <div class="success">
        <div class="check">{{ order.status === 'paid' ? '✓' : '…' }}</div>
        <h1 style="font-size: clamp(32px, 5vw, 56px)">{{ order.status === 'paid' ? 'Thank you!' : 'Payment processing' }}</h1>
        <p class="muted" style="margin-top: 14px">
          <template v-if="order.status === 'paid'">Order #{{ order.id }} is confirmed. We've emailed you a receipt.</template>
          <template v-else>We're waiting for the payment to be confirmed. Refresh in a moment or check your orders.</template>
        </p>
      </div>
      <div class="summary" style="position: static">
        <div v-for="i in order.items" :key="i.product_id" class="sum-item">
          <img :src="i.image_url" :alt="i.name" /><div>{{ i.name }}<div class="muted">Qty {{ i.quantity }}</div></div>
          <b>{{ money(i.unit_price_cents * i.quantity) }}</b>
        </div>
        <div class="row total"><span>Total</span><span>{{ money(order.total_cents) }}</span></div>
        <p class="muted" style="font-size: 14px; margin: 14px 0 0">
          Shipping to {{ order.full_name }}, {{ order.address }}, {{ order.city }} {{ order.postal_code }}, {{ order.country }}
        </p>
      </div>
      <div style="display: flex; gap: 12px; margin-top: 24px; flex-wrap: wrap">
        <NuxtLink to="/products" class="btn">Keep shopping <span>→</span></NuxtLink>
        <NuxtLink to="/orders" class="btn ghost">My orders</NuxtLink>
      </div>
    </template>
  </div>
</template>
