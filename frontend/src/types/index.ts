// Auth types
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserProfile {
  id: string
  email: string
  display_name: string
  first_name: string | null
  last_name: string | null
  role: 'applicant' | 'reviewer' | 'admin'
  organization_id: string | null
  is_active: boolean
  last_login: string | null
}

// Organization types
export interface Organization {
  id: string
  name: string
  legal_name: string | null
  organization_type: string
  registration_number: string | null
  address_line_1: string | null
  address_line_2: string | null
  city: string | null
  province: string
  postal_code: string | null
  phone: string | null
  email: string | null
  website: string | null
  description: string | null
  region_id: string | null
  created_at: string
  updated_at: string
}

export interface OrganizationCreate {
  name: string
  legal_name?: string
  organization_type: string
  registration_number?: string
  address_line_1?: string
  address_line_2?: string
  city?: string
  province?: string
  postal_code?: string
  phone?: string
  email?: string
  website?: string
  description?: string
  region_id?: string
}

// Application types
export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'additional_info_requested'
  | 'reviewed'
  | 'recommended'
  | 'approved'
  | 'denied'
  | 'withdrawn'

export type FundingType = 'operational' | 'capital' | 'emergency' | 'project_based'

export interface Application {
  id: string
  organization_id: string
  title: string
  funding_type: FundingType
  status: ApplicationStatus
  amount_requested: number | null
  amount_approved: number | null
  fiscal_year: string | null
  description: string | null
  submitted_at: string | null
  decision_at: string | null
  created_at: string
  updated_at: string
  sections: ApplicationSection[]
}

export interface ApplicationSection {
  id: string
  section_type: string
  section_order: number
  data: Record<string, unknown>
  is_complete: boolean
  updated_at: string
}

export interface ApplicationCreate {
  organization_id: string
  title: string
  funding_type: FundingType
  amount_requested?: number
  fiscal_year?: string
  description?: string
}

export interface Comment {
  id: string
  user_id: string
  content: string
  is_internal: boolean
  created_at: string
}

// Document types
export interface DocumentInfo {
  id: string
  application_id: string
  file_name: string
  file_type: string
  file_size: number
  content_type: string
  category: string | null
  created_at: string
}

// Review types
export interface ReviewScore {
  id: string
  criteria: string
  score: number
  weight: number
  comments: string | null
}

export interface Review {
  id: string
  application_id: string
  reviewer_id: string
  status: string
  overall_score: number | null
  recommendation: string | null
  notes: string | null
  scores: ReviewScore[]
  created_at: string
  updated_at: string
}

// SVI types
export interface SVIScore {
  id: string
  region_id: string
  region_name: string | null
  year: number
  composite_score: number
  grade: 'A' | 'B' | 'C' | 'D' | 'E'
  category_scores: Record<string, number>
  risk_index: number | null
  normalization_method: string
}

export interface HeatmapDataPoint {
  region_id: string
  region_name: string
  latitude: number | null
  longitude: number | null
  composite_score: number
  grade: string
  category_scores: Record<string, number>
}

export interface HeatmapResponse {
  year: number
  data: HeatmapDataPoint[]
  geojson: GeoJSON.FeatureCollection | null
  legend: Record<string, string>
}

export interface IndicatorCategory {
  id: string
  name: string
  display_name: string
  description: string | null
  weight: number
  sort_order: number
  indicator_count: number
}

export interface Indicator {
  id: string
  category_id: string
  name: string
  display_name: string
  description: string | null
  unit: string | null
  data_source: string | null
  weight: number
  is_inverse: boolean
  is_active: boolean
}

// Geography types
export interface Region {
  id: string
  name: string
  code: string
  region_type: string
  parent_id: string | null
  population: number | null
  area_sq_km: number | null
  latitude: number | null
  longitude: number | null
  municipality_count: number
}

export interface Municipality {
  id: string
  name: string
  code: string | null
  municipality_type: string
  region_id: string
  population: number | null
  latitude: number | null
  longitude: number | null
}

// Common types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  error: string
  detail: string
}
