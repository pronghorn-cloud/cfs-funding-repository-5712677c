<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApplicationsStore } from '@/stores/applications'
import { useAuth } from '@/composables/useAuth'
import { useNotificationsStore } from '@/stores/notifications'

const router = useRouter()
const appStore = useApplicationsStore()
const { user } = useAuth()
const notifications = useNotificationsStore()

const currentStep = ref(1)
const totalSteps = 5

// Form data
const formData = ref({
  title: '',
  funding_type: 'operational',
  amount_requested: null as number | null,
  fiscal_year: '',
  description: '',
  // Section data
  organization_info: {} as Record<string, unknown>,
  project_description: {} as Record<string, unknown>,
  budget: {} as Record<string, unknown>,
  outcomes: {} as Record<string, unknown>,
})

const fundingTypes = [
  { value: 'operational', label: 'Operational Funding' },
  { value: 'capital', label: 'Capital Funding' },
  { value: 'emergency', label: 'Emergency Funding' },
  { value: 'project_based', label: 'Project-Based Funding' },
]

const stepLabels = [
  'Organization Info',
  'Project Description',
  'Budget',
  'Outcomes',
  'Supporting Documents',
]

const canProceed = computed(() => {
  if (currentStep.value === 1) return formData.value.title.length > 0
  return true
})

async function saveDraft() {
  if (!appStore.currentApplication) {
    // Create new application
    const app = await appStore.createApplication({
      organization_id: user.value?.organization_id ?? '',
      title: formData.value.title,
      funding_type: formData.value.funding_type,
      amount_requested: formData.value.amount_requested ?? undefined,
      fiscal_year: formData.value.fiscal_year,
      description: formData.value.description,
    })
    if (app) {
      notifications.success('Draft saved successfully')
    }
  }
}

async function submitApplication() {
  if (appStore.currentApplication) {
    await appStore.submitApplication(appStore.currentApplication.id)
    if (!appStore.error) {
      notifications.success('Application submitted successfully!')
      router.push('/dashboard')
    } else {
      notifications.error(appStore.error)
    }
  }
}

function nextStep() {
  if (currentStep.value < totalSteps) {
    saveDraft()
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">New Funding Application</h1>

    <!-- Step indicator -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div
          v-for="(label, index) in stepLabels"
          :key="index"
          class="flex items-center"
          :class="{ 'flex-1': index < stepLabels.length - 1 }"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
            :class="currentStep > index + 1 ? 'bg-goa-success text-white' : currentStep === index + 1 ? 'bg-goa-blue text-white' : 'bg-gray-200 text-gray-600'"
          >
            {{ index + 1 }}
          </div>
          <span class="ml-2 text-sm hidden md:inline" :class="currentStep === index + 1 ? 'font-bold' : 'text-gray-500'">
            {{ label }}
          </span>
          <div v-if="index < stepLabels.length - 1" class="flex-1 h-0.5 mx-4 bg-gray-200">
            <div class="h-full bg-goa-blue transition-all" :style="{ width: currentStep > index + 1 ? '100%' : '0%' }" />
          </div>
        </div>
      </div>
    </div>

    <!-- Step 1: Basic Info -->
    <div v-show="currentStep === 1" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Application Details</h2>

      <goa-form-item label="Application Title" requirement="required">
        <goa-input
          name="title"
          :value="formData.title"
          @_change="(e: any) => formData.title = e.detail.value"
          placeholder="Enter a descriptive title for your application"
        />
      </goa-form-item>

      <goa-form-item label="Funding Type" requirement="required" class="mt-4">
        <goa-dropdown
          name="funding_type"
          :value="formData.funding_type"
          @_change="(e: any) => formData.funding_type = e.detail.value"
        >
          <goa-dropdown-item
            v-for="ft in fundingTypes"
            :key="ft.value"
            :value="ft.value"
            :label="ft.label"
          />
        </goa-dropdown>
      </goa-form-item>

      <goa-form-item label="Amount Requested ($)" class="mt-4">
        <goa-input
          name="amount"
          type="number"
          :value="formData.amount_requested?.toString() ?? ''"
          @_change="(e: any) => formData.amount_requested = Number(e.detail.value) || null"
          placeholder="0.00"
        />
      </goa-form-item>

      <goa-form-item label="Fiscal Year" class="mt-4">
        <goa-input
          name="fiscal_year"
          :value="formData.fiscal_year"
          @_change="(e: any) => formData.fiscal_year = e.detail.value"
          placeholder="e.g., 2025-2026"
        />
      </goa-form-item>

      <goa-form-item label="Description" class="mt-4">
        <goa-textarea
          name="description"
          :value="formData.description"
          @_change="(e: any) => formData.description = e.detail.value"
          placeholder="Brief description of your funding request"
          rows="4"
        />
      </goa-form-item>
    </div>

    <!-- Step 2: Project Description -->
    <div v-show="currentStep === 2" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Project Description</h2>
      <goa-callout type="information">
        Provide detailed information about the project or initiative this funding will support.
      </goa-callout>
      <goa-form-item label="Project Goals" class="mt-4">
        <goa-textarea name="project_goals" rows="4" placeholder="Describe the goals and objectives..." />
      </goa-form-item>
      <goa-form-item label="Target Population" class="mt-4">
        <goa-textarea name="target_population" rows="3" placeholder="Who will benefit from this project?" />
      </goa-form-item>
      <goa-form-item label="Implementation Timeline" class="mt-4">
        <goa-textarea name="timeline" rows="3" placeholder="Describe the implementation timeline..." />
      </goa-form-item>
    </div>

    <!-- Step 3: Budget -->
    <div v-show="currentStep === 3" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Budget Details</h2>
      <goa-callout type="information">
        Provide a detailed breakdown of how the requested funds will be used.
      </goa-callout>
      <goa-form-item label="Budget Breakdown" class="mt-4">
        <goa-textarea name="budget_breakdown" rows="6" placeholder="Line-by-line budget..." />
      </goa-form-item>
      <goa-form-item label="Other Funding Sources" class="mt-4">
        <goa-textarea name="other_funding" rows="3" placeholder="List any other funding sources..." />
      </goa-form-item>
    </div>

    <!-- Step 4: Outcomes -->
    <div v-show="currentStep === 4" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Expected Outcomes</h2>
      <goa-form-item label="Key Performance Indicators" class="mt-4">
        <goa-textarea name="kpis" rows="4" placeholder="What metrics will you track?" />
      </goa-form-item>
      <goa-form-item label="Expected Impact" class="mt-4">
        <goa-textarea name="expected_impact" rows="4" placeholder="Describe the expected impact..." />
      </goa-form-item>
    </div>

    <!-- Step 5: Documents -->
    <div v-show="currentStep === 5" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Supporting Documents</h2>
      <goa-callout type="information">
        Upload any supporting documents (PDF, Word, Excel). Max 50 MB per file.
      </goa-callout>
      <goa-file-upload class="mt-4" variant="dragdrop" />
    </div>

    <!-- Navigation -->
    <div class="flex justify-between mt-6">
      <goa-button type="secondary" @_click="prevStep" :disabled="currentStep === 1">
        Previous
      </goa-button>
      <div class="flex gap-3">
        <goa-button type="secondary" @_click="saveDraft">
          Save Draft
        </goa-button>
        <goa-button
          v-if="currentStep < totalSteps"
          type="primary"
          @_click="nextStep"
          :disabled="!canProceed"
        >
          Next
        </goa-button>
        <goa-button
          v-else
          type="primary"
          @_click="submitApplication"
        >
          Submit Application
        </goa-button>
      </div>
    </div>
  </div>
</template>
