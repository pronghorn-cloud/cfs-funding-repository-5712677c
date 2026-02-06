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
const showSaveAlert = ref(false)
const uploadedFiles = ref<File[]>([])

// Form data — all fields across all steps
const formData = ref({
  title: '',
  funding_type: 'operational',
  amount_requested: null as number | null,
  fiscal_year: '',
  description: '',
  project_goals: '',
  target_population: '',
  timeline: '',
  budget_breakdown: '',
  other_funding: '',
  kpis: '',
  expected_impact: '',
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
    const app = await appStore.createApplication({
      organization_id: user.value?.organization_id ?? '',
      title: formData.value.title,
      funding_type: formData.value.funding_type,
      amount_requested: formData.value.amount_requested ?? undefined,
      fiscal_year: formData.value.fiscal_year,
      description: formData.value.description,
    })
    if (app) {
      showSaveAlert.value = true
      setTimeout(() => { showSaveAlert.value = false }, 5000)
    }
  } else {
    showSaveAlert.value = true
    setTimeout(() => { showSaveAlert.value = false }, 5000)
  }
}

function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    uploadedFiles.value.push(...Array.from(input.files))
  }
}

function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

function goToReview() {
  // Store form data in Pinia so the review page can read it
  appStore.draftFormData = {
    title: formData.value.title,
    funding_type: formData.value.funding_type,
    amount_requested: formData.value.amount_requested,
    fiscal_year: formData.value.fiscal_year,
    description: formData.value.description,
    project_goals: formData.value.project_goals,
    target_population: formData.value.target_population,
    timeline: formData.value.timeline,
    budget_breakdown: formData.value.budget_breakdown,
    other_funding: formData.value.other_funding,
    kpis: formData.value.kpis,
    expected_impact: formData.value.expected_impact,
    uploadedFileNames: uploadedFiles.value.map(f => f.name),
  }
  router.push({ name: 'application-review-submit' })
}

function nextStep() {
  if (currentStep.value < totalSteps) {
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

    <!-- Save Draft Alert -->
    <goa-notification v-if="showSaveAlert" type="event" class="mb-4" @_dismiss="showSaveAlert = false">
      Application draft has been successfully saved.
    </goa-notification>

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
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Application Details</h2>

      <goa-form-item label="Application Title" requirement="required">
        <goa-input
          name="title"
          :value="formData.title"
          @_change="(e: any) => formData.title = e.detail.value"
          placeholder="Enter a descriptive title for your application"
        />
      </goa-form-item>

      <div class="mt-4 relative z-10">
        <goa-form-item label="Funding Type" requirement="required">
          <select
            class="w-full border border-gray-400 rounded px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-goa-blue"
            :value="formData.funding_type"
            @change="(e: any) => formData.funding_type = e.target.value"
          >
            <option v-for="ft in fundingTypes" :key="ft.value" :value="ft.value">
              {{ ft.label }}
            </option>
          </select>
        </goa-form-item>
      </div>

      <goa-form-item label="Amount Requested (CAD $)" helptext="Enter the amount in Canadian dollars." class="mt-4">
        <goa-input
          name="amount"
          type="number"
          :value="formData.amount_requested?.toFixed(2) ?? ''"
          @_change="(e: any) => formData.amount_requested = parseFloat(Number(e.detail.value).toFixed(2)) || null"
          placeholder="0.00"
          step="0.01"
          min="0"
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
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Project Description</h2>
      <goa-callout type="information">
        Provide detailed information about the project or initiative this funding will support.
      </goa-callout>
      <goa-form-item label="Project Goals" class="mt-4">
        <goa-textarea
          name="project_goals"
          :value="formData.project_goals"
          @_change="(e: any) => formData.project_goals = e.detail.value"
          rows="4"
          placeholder="Describe the goals and objectives..."
        />
      </goa-form-item>
      <goa-form-item label="Target Population" class="mt-4">
        <goa-textarea
          name="target_population"
          :value="formData.target_population"
          @_change="(e: any) => formData.target_population = e.detail.value"
          rows="3"
          placeholder="Who will benefit from this project?"
        />
      </goa-form-item>
      <goa-form-item label="Implementation Timeline" class="mt-4">
        <goa-textarea
          name="timeline"
          :value="formData.timeline"
          @_change="(e: any) => formData.timeline = e.detail.value"
          rows="3"
          placeholder="Describe the implementation timeline..."
        />
      </goa-form-item>
    </div>

    <!-- Step 3: Budget -->
    <div v-show="currentStep === 3" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Budget Details</h2>
      <goa-callout type="information">
        Provide a detailed breakdown of how the requested funds will be used. All amounts in Canadian dollars (CAD).
      </goa-callout>
      <goa-form-item label="Budget Breakdown" class="mt-4">
        <goa-textarea
          name="budget_breakdown"
          :value="formData.budget_breakdown"
          @_change="(e: any) => formData.budget_breakdown = e.detail.value"
          rows="6"
          placeholder="Line-by-line budget..."
        />
      </goa-form-item>
      <goa-form-item label="Other Funding Sources" class="mt-4">
        <goa-textarea
          name="other_funding"
          :value="formData.other_funding"
          @_change="(e: any) => formData.other_funding = e.detail.value"
          rows="3"
          placeholder="List any other funding sources..."
        />
      </goa-form-item>
    </div>

    <!-- Step 4: Outcomes -->
    <div v-show="currentStep === 4" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Expected Outcomes</h2>
      <goa-form-item label="Key Performance Indicators" class="mt-4">
        <goa-textarea
          name="kpis"
          :value="formData.kpis"
          @_change="(e: any) => formData.kpis = e.detail.value"
          rows="4"
          placeholder="What metrics will you track?"
        />
      </goa-form-item>
      <goa-form-item label="Expected Impact" class="mt-4">
        <goa-textarea
          name="expected_impact"
          :value="formData.expected_impact"
          @_change="(e: any) => formData.expected_impact = e.detail.value"
          rows="4"
          placeholder="Describe the expected impact..."
        />
      </goa-form-item>
    </div>

    <!-- Step 5: Documents -->
    <div v-show="currentStep === 5" class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4 text-goa-blue-700">Supporting Documents</h2>
      <goa-callout type="information">
        Upload any supporting documents (PDF, Word, Excel). Max 50 MB per file.
      </goa-callout>

      <div class="mt-4">
        <label
          class="inline-flex items-center gap-2 px-4 py-2 bg-goa-blue text-white rounded cursor-pointer hover:bg-goa-blue-600 transition-colors text-sm font-medium"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Upload Document
          <input
            type="file"
            class="hidden"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx,.csv"
            @change="handleFileUpload"
          />
        </label>
      </div>

      <!-- Uploaded files list -->
      <div v-if="uploadedFiles.length > 0" class="mt-4 space-y-2">
        <div
          v-for="(file, index) in uploadedFiles"
          :key="index"
          class="flex items-center justify-between bg-gray-50 border border-gray-200 rounded px-4 py-2"
        >
          <div class="flex items-center gap-2 text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>{{ file.name }}</span>
            <span class="text-gray-400">({{ (file.size / 1024).toFixed(1) }} KB)</span>
          </div>
          <button
            @click="removeFile(index)"
            class="text-goa-emergency hover:underline text-sm"
            :aria-label="`Remove ${file.name}`"
          >
            Remove
          </button>
        </div>
      </div>

      <p v-else class="mt-4 text-sm text-gray-500">No documents uploaded yet.</p>
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
          @_click="goToReview"
        >
          Done
        </goa-button>
      </div>
    </div>
  </div>
</template>
