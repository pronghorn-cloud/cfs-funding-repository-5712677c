<script setup lang="ts">
import { ref } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import { vulnerabilityService } from '@/services/vulnerability.service'

const notifications = useNotificationsStore()
const isRecalculating = ref(false)

async function recalculate() {
  isRecalculating.value = true
  try {
    const result = await vulnerabilityService.recalculate({
      year: new Date().getFullYear(),
      normalization_method: 'min_max',
    })
    notifications.success(
      `Recalculated ${result.regions_calculated} regions in ${result.duration_seconds}s`,
    )
  } catch {
    notifications.error('Recalculation failed')
  } finally {
    isRecalculating.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">System Configuration</h1>

    <div class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">SVI Configuration</h2>
        <p class="text-gray-600 mb-4">Manage Social Vulnerability Index calculation parameters.</p>
        <goa-button type="primary" @_click="recalculate" :disabled="isRecalculating">
          {{ isRecalculating ? 'Recalculating...' : 'Recalculate All Scores' }}
        </goa-button>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Application Settings</h2>
        <goa-form-item label="Current Fiscal Year">
          <goa-input name="fiscal_year" value="2025-2026" />
        </goa-form-item>
        <goa-form-item label="Max File Upload Size (MB)" class="mt-4">
          <goa-input name="max_upload" type="number" value="50" />
        </goa-form-item>
      </div>
    </div>
  </div>
</template>
