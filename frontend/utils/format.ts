export const money = (cents: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100)

/** Turn a $fetch error (FastAPI style) into a readable message. */
export const errMsg = (e: any): string => {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg?.replace('Value error, ', '')).filter(Boolean).join('. ')
  return e?.message || 'Something went wrong. Please try again.'
}
