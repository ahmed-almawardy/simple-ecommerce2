<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const api = useApi()
const { user } = useAuth()
const { cart, load } = useCart()
await load()

const form = reactive({ full_name: user.value?.full_name || '', address: '', city: '', postal_code: '', country: '' })
const loading = ref(false)
const error = ref('')

const pay = async () => {
  error.value = ''
  loading.value = true
  try {
    const res = await api<{ order_id: number; payment_url: string }>('/api/orders/checkout', { method: 'POST', body: form })
    await navigateTo(res.payment_url, { external: true })
  } catch (e) {
    error.value = errMsg(e)
    loading.value = false
  }
}
useHead({ title: 'Checkout | VOLTA' })
</script>

<template>
  <div class="container">
    <h1 class="page-title">Checkout</h1>

    <div v-if="!cart.items.length" class="empty">
      <h3>Your bag is empty</h3>
      <NuxtLink to="/products" class="btn">Start shopping <span>→</span></NuxtLink>
    </div>

    <div v-else class="two-col">
      <form class="form" @submit.prevent="pay">
        <h2 style="font-size: 22px; margin-bottom: 6px">Delivery address</h2>
        <div class="field"><label>Full name</label><input v-model="form.full_name" required minlength="2" autocomplete="name" /></div>
        <div class="field"><label>Address</label><input v-model="form.address" required autocomplete="street-address" /></div>
        <div class="two">
          <div class="field"><label>City</label><input v-model="form.city" required autocomplete="address-level2" /></div>
          <div class="field"><label>Postal code</label><input v-model="form.postal_code" required autocomplete="postal-code" /></div>
        </div>
        <div class="field"><label>Country</label><input v-model="form.country" required autocomplete="country-name" /></div>
        <div v-if="error" class="error">{{ error }}</div>
        <button class="btn block" :disabled="loading" style="margin-top: 10px">
          {{ loading ? 'Redirecting to payment…' : `Pay ${money(cart.total_cents)}` }} <span>→</span>
        </button>
        <p class="muted" style="font-size: 13px; margin: 0">You'll be taken to our secure payment page to complete your purchase.</p>
      </form>

      <aside class="summary">
        <h2>Your order</h2>
        <div v-for="it in cart.items" :key="it.product.id" class="sum-item">
          <img :src="it.product.image_url" :alt="it.product.name" />
          <div>{{ it.product.name }}<div class="muted">Qty {{ it.quantity }}</div></div>
          <b>{{ money(it.line_total_cents) }}</b>
        </div>
        <div class="row" style="margin-top: 10px"><span>Delivery</span><span>Free</span></div>
        <div class="row total"><span>Total</span><span>{{ money(cart.total_cents) }}</span></div>
      </aside>
    </div>
  </div>
</template>
