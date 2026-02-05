import api from './api'
import type { Review } from '@/types'

export interface ReviewScoreInput {
  criteria: string
  score: number
  weight: number
  comments?: string
}

export const reviewsService = {
  async create(
    applicationId: string,
    scores: ReviewScoreInput[],
    recommendation?: string,
    notes?: string,
  ): Promise<Review> {
    const { data } = await api.post<Review>('/reviews', {
      application_id: applicationId,
      scores,
      recommendation,
      notes,
    })
    return data
  },

  async get(reviewId: string): Promise<Review> {
    const { data } = await api.get<Review>(`/reviews/${reviewId}`)
    return data
  },

  async update(
    reviewId: string,
    scores?: ReviewScoreInput[],
    recommendation?: string,
    notes?: string,
  ): Promise<Review> {
    const { data } = await api.patch<Review>(`/reviews/${reviewId}`, {
      scores,
      recommendation,
      notes,
    })
    return data
  },

  async complete(reviewId: string): Promise<Review> {
    const { data } = await api.post<Review>(`/reviews/${reviewId}/complete`)
    return data
  },

  async listForApplication(applicationId: string): Promise<Review[]> {
    const { data } = await api.get<Review[]>(`/reviews/application/${applicationId}`)
    return data
  },

  async listMine(): Promise<Review[]> {
    const { data } = await api.get<Review[]>('/reviews/reviewer/me')
    return data
  },
}
