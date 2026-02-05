import { ref, computed } from 'vue'

export function usePagination(initialPageSize = 20) {
  const currentPage = ref(1)
  const pageSize = ref(initialPageSize)
  const totalItems = ref(0)

  const totalPages = computed(() =>
    Math.ceil(totalItems.value / pageSize.value),
  )

  const offset = computed(() => (currentPage.value - 1) * pageSize.value)

  function setPage(page: number) {
    currentPage.value = Math.max(1, Math.min(page, totalPages.value || 1))
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  function prevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  function updateFromResponse(total: number) {
    totalItems.value = total
  }

  return {
    currentPage,
    pageSize,
    totalItems,
    totalPages,
    offset,
    setPage,
    nextPage,
    prevPage,
    updateFromResponse,
  }
}
