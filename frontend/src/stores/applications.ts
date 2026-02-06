import { defineStore } from 'pinia'
import { ref } from 'vue'
import { applicationsService } from '@/services/applications.service'
import type { Application, PaginatedResponse } from '@/types'

export interface DraftFormData {
  title: string
  funding_type: string
  amount_requested: number | null
  fiscal_year: string
  description: string
  project_goals: string
  target_population: string
  timeline: string
  budget_breakdown: string
  other_funding: string
  kpis: string
  expected_impact: string
  uploadedFileNames: string[]
}

export const useApplicationsStore = defineStore('applications', () => {
  const applications = ref<PaginatedResponse<Application> | null>(null)
  const currentApplication = ref<Application | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const draftFormData = ref<DraftFormData | null>(null)

  async function fetchApplications(params?: {
    page?: number
    page_size?: number
    organization_id?: string
    status?: string
  }) {
    isLoading.value = true
    error.value = null
    try {
      applications.value = await applicationsService.list(params)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch applications'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApplication(id: string) {
    isLoading.value = true
    error.value = null
    try {
      currentApplication.value = await applicationsService.get(id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch application'
    } finally {
      isLoading.value = false
    }
  }

  async function createApplication(data: {
    organization_id: string
    title: string
    funding_type: string
    amount_requested?: number
    fiscal_year?: string
    description?: string
  }): Promise<Application | null> {
    isLoading.value = true
    error.value = null
    try {
      const app = await applicationsService.create(data as any)
      return app
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create application'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function saveSection(
    appId: string,
    sectionType: string,
    data: Record<string, unknown>,
    isComplete: boolean = false,
  ) {
    try {
      await applicationsService.saveSection(appId, sectionType, data, isComplete)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to save section'
    }
  }

  async function submitApplication(appId: string) {
    try {
      currentApplication.value = await applicationsService.transitionStatus(appId, 'submitted')
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to submit application'
    }
  }

  return {
    applications,
    currentApplication,
    isLoading,
    error,
    draftFormData,
    fetchApplications,
    fetchApplication,
    createApplication,
    saveSection,
    submitApplication,
  }
})
