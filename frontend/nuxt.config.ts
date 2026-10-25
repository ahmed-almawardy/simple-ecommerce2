export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      // override with NUXT_PUBLIC_API_BASE
      apiBase: 'http://localhost:8000',
      brand: 'VOLTA',
    },
  },
  app: {
    head: {
      title: 'VOLTA | Home electronics & appliances',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Kitchen, laundry, climate, cleaning, TV & audio and smart-home appliances with free delivery and warranty.' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@700&display=swap',
        },
      ],
    },
  },
})
