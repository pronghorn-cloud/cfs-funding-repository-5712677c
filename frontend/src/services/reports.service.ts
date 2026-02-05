import api from './api'

export interface BriefingRequest {
  application_ids: string[]
  report_type: 'minister_briefing' | 'treasury_board'
  include_svi_data: boolean
  format: 'pdf' | 'docx'
}

export interface ReportResponse {
  report_id: string
  report_type: string
  format: string
  file_name: string
  download_url: string
}

export const reportsService = {
  async generate(request: BriefingRequest): Promise<ReportResponse> {
    const { data } = await api.post<ReportResponse>('/reports/generate', request)
    return data
  },
}
