<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const { isAuthenticated } = useAuth()
const router = useRouter()

if (isAuthenticated.value) {
  router.replace('/dashboard')
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-12">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-goa-blue mb-4">
        CFS Funding Portal
      </h1>
      <p class="text-xl text-gray-600 mb-8">
        Community Facilities and Supports - Shelter Funding Applications
      </p>
      <goa-button type="primary" @_click="router.push('/login')">
        Sign In to Get Started
      </goa-button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
      <goa-callout type="information" heading="Apply for Funding">
        Submit and track your shelter funding applications online. Save drafts and return anytime.
      </goa-callout>

      <goa-callout type="information" heading="Track Progress">
        Monitor your application status in real-time and respond to reviewer feedback.
      </goa-callout>

      <goa-callout type="information" heading="Vulnerability Insights">
        Access social vulnerability data to inform your funding priorities and decisions.
      </goa-callout>
    </div>

    <div class="mt-12 bg-gray-50 rounded-lg p-8">
      <h2 class="text-2xl font-semibold mb-4">About the Social Vulnerability Index</h2>
      <p class="text-gray-700 mb-4">
        The Social Vulnerability Index (SVI) provides a data-driven assessment of community
        vulnerability across Alberta. It combines 83 indicators across 6 categories to help
        inform funding decisions and resource allocation.
      </p>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <goa-badge content="Socioeconomic" />
        <goa-badge content="Demographic" />
        <goa-badge content="Health" />
        <goa-badge content="Housing" />
        <goa-badge content="Infrastructure" />
        <goa-badge content="Environmental" />
      </div>
    </div>
  </div>
</template>
