export default defineNuxtRouteMiddleware((to) => {
  const token = useCookie<string | null>('token')
  if (!token.value) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
})
