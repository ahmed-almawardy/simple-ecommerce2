// Restore the session (user + cart) from the token cookie on first load.
export default defineNuxtPlugin(async () => {
  const { fetchUser, user } = useAuth()
  const { load } = useCart()
  await fetchUser()
  if (user.value) await load()
})
