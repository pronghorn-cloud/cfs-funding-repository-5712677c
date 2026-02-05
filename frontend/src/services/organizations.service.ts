import api from './api'
import type { Organization, OrganizationCreate, PaginatedResponse } from '@/types'

export const organizationsService = {
  async list(params?: { page?: number; page_size?: number; search?: string }): Promise<PaginatedResponse<Organization>> {
    const { data } = await api.get<PaginatedResponse<Organization>>('/organizations', { params })
    return data
  },

  async get(id: string): Promise<Organization> {
    const { data } = await api.get<Organization>(`/organizations/${id}`)
    return data
  },

  async create(org: OrganizationCreate): Promise<Organization> {
    const { data } = await api.post<Organization>('/organizations', org)
    return data
  },

  async update(id: string, org: Partial<OrganizationCreate>): Promise<Organization> {
    const { data } = await api.patch<Organization>(`/organizations/${id}`, org)
    return data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/organizations/${id}`)
  },
}
