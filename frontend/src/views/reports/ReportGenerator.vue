<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useApplicationsStore } from '@/stores/applications'
import { reportsService, type BriefingRequest } from '@/services/reports.service'
import { useNotificationsStore } from '@/stores/notifications'

const appStore = useApplicationsStore()
const notifications = useNotificationsStore()

const selectedApps = ref<string[]>([])
const reportType = ref<'minister_briefing' | 'treasury_board'>('minister_briefing')
const includeSVI = ref(true)
const format = ref<'pdf' | 'docx'>('pdf')
const isGenerating = ref(false)

onMounted(async () => {
  await appStore.fetchApplications({ status: 'approved', page_size: 100 })
})

function toggleApp(appId: string) {
  const idx = selectedApps.value.indexOf(appId)
  if (idx >= 0) {
    selectedApps.value.splice(idx, 1)
  } else {
    selectedApps.value.push(appId)
  }
}

async function generate() {
  if (selectedApps.value.length === 0) {
    notifications.warning('Please select at least one application')
    return
  }

  isGenerating.value = true
  try {
    const request: BriefingRequest = {
      application_ids: selectedApps.value,
      report_type: reportType.value,
      include_svi_data: includeSVI.value,
      format: format.value,
    }
    const result = await reportsService.generate(request)
    notifications.success(`Report generated: ${result.file_name}`)
    // Download the file
    window.open(result.download_url, '_blank')
  } catch {
    notifications.error('Failed to generate report')
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">Report Generator</h1>

    <!-- Report Config -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4">Report Configuration</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <goa-form-item label="Report Type">
          <goa-dropdown
            name="report_type"
            :value="reportType"
            @_change="(e: any) => reportType = e.detail.value"
          >
            <goa-dropdown-item value="minister_briefing" label="Minister Briefing" />
            <goa-dropdown-item value="treasury_board" label="Treasury Board Submission" />
          </goa-dropdown>
        </goa-form-item>

        <goa-form-item label="Format">
          <goa-dropdown
            name="format"
            :value="format"
            @_change="(e: any) => format = e.detail.value"
          >
            <goa-dropdown-item value="pdf" label="PDF" />
            <goa-dropdown-item value="docx" label="Word Document" />
          </goa-dropdown>
        </goa-form-item>

        <goa-form-item label="Options">
          <label class="flex items-center gap-2 mt-2">
            <input type="checkbox" v-model="includeSVI" class="rounded" />
            Include SVI data
          </label>
        </goa-form-item>
      </div>
    </div>

    <!-- Application Selection -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-4">Select Applications ({{ selectedApps.length }} selected)</h2>

      <goa-spinner v-if="appStore.isLoading" />

      <div v-else-if="appStore.applications?.items.length === 0" class="text-gray-500 text-center py-4">
        No approved applications available for reporting.
      </div>

      <div v-else class="space-y-2">
        <label
          v-for="app in appStore.applications?.items"
          :key="app.id"
          class="flex items-center gap-3 p-3 border rounded cursor-pointer hover:bg-gray-50"
          :class="{ 'border-goa-blue bg-blue-50': selectedApps.includes(app.id) }"
        >
          <input
            type="checkbox"
            :checked="selectedApps.includes(app.id)"
            @change="toggleApp(app.id)"
            class="rounded"
          />
          <div class="flex-1">
            <div class="font-medium">{{ app.title }}</div>
            <div class="text-sm text-gray-500">
              {{ app.funding_type }} |
              {{ app.amount_requested ? `$${Number(app.amount_requested).toLocaleString()}` : 'N/A' }}
            </div>
          </div>
          <goa-badge :content="app.status" type="success" />
        </label>
      </div>
    </div>

    <div class="flex justify-end">
      <goa-button type="primary" @_click="generate" :disabled="isGenerating || selectedApps.length === 0">
        {{ isGenerating ? 'Generating...' : 'Generate Report' }}
      </goa-button>
    </div>
  </div>
</template>
