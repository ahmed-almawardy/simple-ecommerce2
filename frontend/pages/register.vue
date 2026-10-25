<script setup lang="ts">
const route = useRoute()
const { register, loggedIn } = useAuth()
const { show } = useToast()
const form = reactive({ full_name: '', email: '', password: '' })
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
    await register(form.full_name, form.email, form.password)
    show('Account created! We sent you a welcome email.')
    await navigateTo(redirect.value)
  } catch (e) {
    error.value = errMsg(e)
  } finally {
    loading.value = false
  }
}
useHead({ title: 'Create account | VOLTA' })
</script>

<template>
  <div class="auth">
    <div class="auth-art" style="background-image: url(https://picsum.photos/seed/volta-register/1200/1400)"><h2>Join<br />VOLTA.</h2></div>
    <form class="auth-form form" @submit.prevent="submit">
      <h1>Create account</h1>
      <p class="muted">Fast checkout, order tracking and member-only deals.</p>
      <div class="field"><label>Full name</label><input v-model="form.full_name" required minlength="2" autocomplete="name" /></div>
      <div class="field"><label>Email</label><input v-model="form.email" type="email" required autocomplete="email" /></div>
      <div class="field"><label>Password (min. 8 characters)</label><input v-model="form.password" type="password" required minlength="8" autocomplete="new-password" /></div>
      <div v-if="error" class="error">{{ error }}</div>
      <button class="btn block" :disabled="loading">{{ loading ? 'Creating…' : 'Create account' }} <span>→</span></button>
      <div class="alt">Already a member? <NuxtLink :to="{ path: '/login', query: route.query }">Log in</NuxtLink></div>
    </form>
  </div>
</template>
