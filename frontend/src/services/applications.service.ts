import api from './api'
import type {
  Application,
  ApplicationCreate,
  ApplicationSection,
  Comment,
  PaginatedResponse,
} from '@/types'

export const applicationsService = {
  async list(params?: {
    page?: number
    page_size?: number
    organization_id?: string
    status?: string
  }): Promise<PaginatedResponse<Application>> {
    const { data } = await api.get<PaginatedResponse<Application>>('/applications', { params })
    return data
  },

  async get(id: string): Promise<Application> {
    const { data } = await api.get<Application>(`/applications/${id}`)
    return data
  },

  async create(app: ApplicationCreate): Promise<Application> {
    const { data } = await api.post<Application>('/applications', app)
    return data
  },

  async update(id: string, app: Partial<ApplicationCreate>): Promise<Application> {
    const { data } = await api.patch<Application>(`/applications/${id}`, app)
    return data
  },

  async saveSection(
    appId: string,
    sectionType: string,
    sectionData: Record<string, unknown>,
    isComplete: boolean = false,
  ): Promise<ApplicationSection> {
    const { data } = await api.post<ApplicationSection>(`/applications/${appId}/sections`, {
      section_type: sectionType,
      data: sectionData,
      is_complete: isComplete,
    })
    return data
  },

  async transitionStatus(appId: string, newStatus: string, notes?: string): Promise<Application> {
    const { data } = await api.post<Application>(`/applications/${appId}/status`, {
      new_status: newStatus,
      notes,
    })
    return data
  },

  async makeDecision(
    appId: string,
    status: 'approved' | 'denied',
    amountApproved?: number,
    notes?: string,
  ): Promise<Application> {
    const { data } = await api.post<Application>(`/applications/${appId}/decision`, {
      status,
      amount_approved: amountApproved,
      notes,
    })
    return data
  },

  async addComment(appId: string, content: string, isInternal: boolean = false): Promise<Comment> {
    const { data } = await api.post<Comment>(`/applications/${appId}/comments`, {
      content,
      is_internal: isInternal,
    })
    return data
  },

  async listComments(appId: string): Promise<Comment[]> {
    const { data } = await api.get<Comment[]>(`/applications/${appId}/comments`)
    return data
  },
}
