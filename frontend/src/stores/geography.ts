import { defineStore } from 'pinia'
import { ref } from 'vue'
import { geographyService } from '@/services/geography.service'
import type { Municipality, Region } from '@/types'

export const useGeographyStore = defineStore('geography', () => {
  const regions = ref<Region[]>([])
  const municipalities = ref<Municipality[]>([])
  const geojson = ref<GeoJSON.FeatureCollection | null>(null)
  const isLoading = ref(false)

  async function fetchRegions(regionType?: string) {
    isLoading.value = true
    try {
      regions.value = await geographyService.listRegions(regionType)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchGeoJSON() {
    try {
      geojson.value = await geographyService.getAllGeoJSON()
    } catch {
      // Silent fail - GeoJSON may not be available yet
    }
  }

  async function fetchMunicipalities(regionId?: string) {
    municipalities.value = await geographyService.listMunicipalities(regionId)
  }

  return {
    regions,
    municipalities,
    geojson,
    isLoading,
    fetchRegions,
    fetchGeoJSON,
    fetchMunicipalities,
  }
})
