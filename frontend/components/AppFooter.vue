<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div>
          <div class="logo" style="color: #fff; margin-bottom: 14px"><span>⚡</span>VOLTA</div>
          <p style="color: #999; font-size: 14px; max-width: 30ch; margin: 0">Appliances and electronics for a smarter, more efficient home.</p>
        </div>
        <div>
          <h4>Shop</h4>
          <NuxtLink :to="{ path: '/products', query: { category: 'kitchen' } }">Kitchen</NuxtLink>
          <NuxtLink :to="{ path: '/products', query: { category: 'laundry' } }">Laundry</NuxtLink>
          <NuxtLink :to="{ path: '/products', query: { category: 'climate' } }">Cooling & Heating</NuxtLink>
          <NuxtLink :to="{ path: '/products', query: { category: 'smart-home' } }">Smart Home</NuxtLink>
        </div>
        <div>
          <h4>Account</h4>
          <NuxtLink to="/login">Log in</NuxtLink>
          <NuxtLink to="/register">Create account</NuxtLink>
          <NuxtLink to="/orders">My orders</NuxtLink>
          <NuxtLink to="/cart">Cart</NuxtLink>
        </div>
        <div>
          <h4>Help</h4>
          <a href="#">Delivery & installation</a>
          <a href="#">Returns & warranty</a>
          <a href="#">Contact us</a>
        </div>
      </div>
      <div class="legal">© {{ new Date().getFullYear() }} VOLTA. Demo store.</div>
    </div>
  </footer>
</template>
