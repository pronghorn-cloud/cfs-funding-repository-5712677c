import { defineStore } from 'pinia'
import { ref } from 'vue'
import { organizationsService } from '@/services/organizations.service'
import type { Organization, OrganizationCreate, PaginatedResponse } from '@/types'

export const useOrganizationsStore = defineStore('organizations', () => {
  const organizations = ref<PaginatedResponse<Organization> | null>(null)
  const currentOrganization = ref<Organization | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchOrganizations(params?: {
    page?: number
    page_size?: number
    search?: string
  }) {
    isLoading.value = true
    error.value = null
    try {
      organizations.value = await organizationsService.list(params)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch organizations'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchOrganization(id: string) {
    isLoading.value = true
    try {
      currentOrganization.value = await organizationsService.get(id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch organization'
    } finally {
      isLoading.value = false
    }
  }

  async function createOrganization(data: OrganizationCreate): Promise<Organization | null> {
    isLoading.value = true
    error.value = null
    try {
      const org = await organizationsService.create(data)
      return org
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create organization'
      return null
    } finally {
      isLoading.value = false
    }
  }

  return {
    organizations,
    currentOrganization,
    isLoading,
    error,
    fetchOrganizations,
    fetchOrganization,
    createOrganization,
  }
})
