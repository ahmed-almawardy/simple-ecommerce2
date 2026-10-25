<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const { cart, load, setQty, remove } = useCart()
const { show } = useToast()
await load()

const change = async (id: number, q: number) => {
  try {
    await setQty(id, q)
  } catch (e) {
    show(errMsg(e), 'err')
  }
}
useHead({ title: 'Your cart | VOLTA' })
</script>

<template>
  <div class="container">
    <h1 class="page-title">Your bag</h1>

    <div v-if="!cart.items.length" class="empty" style="padding-top: 20px">
      <h3>Your bag is empty</h3>
      <p class="muted">Looks like you haven't added anything yet.</p>
      <NuxtLink to="/products" class="btn">Start shopping <span>→</span></NuxtLink>
    </div>

    <div v-else class="two-col">
      <div>
        <div v-for="it in cart.items" :key="it.product.id" class="line">
          <NuxtLink :to="`/products/${it.product.slug}`"><img :src="it.product.image_url" :alt="it.product.name" /></NuxtLink>
          <div>
            <h3>{{ it.product.name }}</h3>
            <div class="muted" style="font-size: 14px; margin: 4px 0 12px; text-transform: capitalize">
              {{ it.product.brand }} • {{ it.product.category.name }} • {{ money(it.product.price_cents) }}
            </div>
            <div class="qty">
              <button aria-label="Decrease" @click="change(it.product.id, it.quantity - 1)">−</button>
              <span>{{ it.quantity }}</span>
              <button :disabled="it.quantity >= it.product.stock" aria-label="Increase" @click="change(it.product.id, it.quantity + 1)">+</button>
            </div>
            <button class="rm" @click="remove(it.product.id)">Remove</button>
          </div>
          <div class="lp">{{ money(it.line_total_cents) }}</div>
        </div>
      </div>

      <aside class="summary">
        <h2>Order summary</h2>
        <div class="row"><span>{{ cart.count }} item{{ cart.count > 1 ? 's' : '' }}</span><span>{{ money(cart.total_cents) }}</span></div>
        <div class="row"><span>Delivery</span><span>Free</span></div>
        <div class="row total"><span>Total</span><span>{{ money(cart.total_cents) }}</span></div>
        <NuxtLink to="/checkout" class="btn block" style="margin-top: 20px">Checkout <span>→</span></NuxtLink>
        <NuxtLink to="/products" class="btn ghost block" style="margin-top: 10px">Continue shopping</NuxtLink>
      </aside>
    </div>
  </div>
</template>
