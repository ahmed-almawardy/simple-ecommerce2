<script setup lang="ts">
const route = useRoute()
const { login, loggedIn } = useAuth()
const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const redirect = computed(() => {
  const r = route.query.redirect as string | undefined
  return r && r.startsWith('/') && !r.startsWith('//') ? r : '/'
})
if (loggedIn.value) await navigateTo(redirect.value)

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await login(form.email, form.password)
    await navigateTo(redirect.value)
  } catch (e) {
    error.value = errMsg(e)
  } finally {
    loading.value = false
  }
}
useHead({ title: 'Log in | VOLTA' })
</script>

<template>
  <div class="auth">
    <div class="auth-art" style="background-image: url(https://picsum.photos/seed/volta-login/1200/1400)"><h2>Welcome<br />back.</h2></div>
    <form class="auth-form form" @submit.prevent="submit">
      <h1>Log in</h1>
      <p class="muted">Access your cart, orders and member deals.</p>
      <div class="field"><label>Email</label><input v-model="form.email" type="email" required autocomplete="email" /></div>
      <div class="field"><label>Password</label><input v-model="form.password" type="password" required autocomplete="current-password" /></div>
      <div v-if="error" class="error">{{ error }}</div>
      <button class="btn block" :disabled="loading">{{ loading ? 'Signing in…' : 'Log in' }} <span>→</span></button>
      <div class="alt">New here? <NuxtLink :to="{ path: '/register', query: route.query }">Create an account</NuxtLink></div>
    </form>
  </div>
</template>
