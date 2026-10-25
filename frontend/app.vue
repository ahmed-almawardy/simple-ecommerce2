<script setup lang="ts">
const { toast } = useToast()
</script>

<template>
  <div>
    <AppHeader />
    <main>
      <NuxtPage />
    </main>
    <AppFooter />
    <Transition name="fade">
      <div v-if="toast" class="toast" :class="{ err: toast.kind === 'err' }" role="status">{{ toast.msg }}</div>
    </Transition>
  </div>
</template>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity .25s, transform .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(8px); }
</style>
