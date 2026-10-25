export const useToast = () => {
  const toast = useState<{ msg: string; kind: 'ok' | 'err' } | null>('toast', () => null)
  let timer: ReturnType<typeof setTimeout> | undefined
  const show = (msg: string, kind: 'ok' | 'err' = 'ok') => {
    toast.value = { msg, kind }
    if (import.meta.client) {
      clearTimeout(timer)
      timer = setTimeout(() => (toast.value = null), 3200)
    }
  }
  return { toast, show }
}
