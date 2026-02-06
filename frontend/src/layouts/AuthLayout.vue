<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <goa-app-header heading="CFS Funding Portal" url="/" />

    <main id="main-content" class="flex-1 flex items-center justify-center" role="main" style="padding: 18px;">
      <router-view />
    </main>

    <footer class="border-t border-gray-200 bg-gray-50 py-4">
      <div class="text-center">
        <nav class="flex justify-center gap-[2em] text-sm" aria-label="Footer links">
          <a href="https://www.alberta.ca/disclaimer" class="text-goa-blue hover:underline">Disclaimer</a>
          <a href="https://www.alberta.ca/privacy" class="text-goa-blue hover:underline">Privacy</a>
          <a href="https://www.alberta.ca/accessibility" class="text-goa-blue hover:underline">Accessibility</a>
        </nav>
        <p class="text-xs text-gray-500 mt-2">&copy; {{ new Date().getFullYear() }} Government of Alberta</p>
      </div>
    </footer>
  </div>
</template>
