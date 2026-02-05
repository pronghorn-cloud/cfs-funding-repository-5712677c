import api from './api'
import type { Municipality, Region } from '@/types'

export const geographyService = {
  async listRegions(regionType?: string): Promise<Region[]> {
    const { data } = await api.get<Region[]>('/geography/regions', {
      params: regionType ? { region_type: regionType } : undefined,
    })
    return data
  },

  async getRegion(id: string): Promise<Region> {
    const { data } = await api.get<Region>(`/geography/regions/${id}`)
    return data
  },

  async getRegionGeoJSON(id: string): Promise<{ id: string; name: string; geojson: unknown }> {
    const { data } = await api.get(`/geography/regions/${id}/geojson`)
    return data
  },

  async getAllGeoJSON(): Promise<GeoJSON.FeatureCollection> {
    const { data } = await api.get('/geography/geojson')
    return data
  },

  async listMunicipalities(regionId?: string): Promise<Municipality[]> {
    const { data } = await api.get<Municipality[]>('/geography/municipalities', {
      params: regionId ? { region_id: regionId } : undefined,
    })
    return data
  },
}
