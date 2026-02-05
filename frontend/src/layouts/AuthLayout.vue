<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <goa-app-header heading="CFS Funding Portal" url="/" />

    <main id="main-content" class="flex-1 flex items-center justify-center" role="main">
      <router-view />
    </main>

    <goa-app-footer>
      <a href="https://www.alberta.ca/disclaimer" slot="meta">Disclaimer</a>
      <a href="https://www.alberta.ca/privacy" slot="meta">Privacy</a>
      <a href="https://www.alberta.ca/accessibility" slot="meta">Accessibility</a>
    </goa-app-footer>
  </div>
</template>
