import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reviewsService } from '@/services/reviews.service'
import type { Review } from '@/types'

export const useReviewsStore = defineStore('reviews', () => {
  const reviews = ref<Review[]>([])
  const currentReview = ref<Review | null>(null)
  const myReviews = ref<Review[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchReviewsForApplication(applicationId: string) {
    isLoading.value = true
    try {
      reviews.value = await reviewsService.listForApplication(applicationId)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch reviews'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMyReviews() {
    isLoading.value = true
    try {
      myReviews.value = await reviewsService.listMine()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch reviews'
    } finally {
      isLoading.value = false
    }
  }

  return {
    reviews,
    currentReview,
    myReviews,
    isLoading,
    error,
    fetchReviewsForApplication,
    fetchMyReviews,
  }
})
