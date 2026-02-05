import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])

  function addNotification(type: Notification['type'], message: string, duration = 5000) {
    const id = crypto.randomUUID()
    notifications.value.push({ id, type, message, duration })

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
  }

  function removeNotification(id: string) {
    notifications.value = notifications.value.filter((n) => n.id !== id)
  }

  function success(message: string) {
    addNotification('success', message)
  }

  function error(message: string) {
    addNotification('error', message, 8000)
  }

  function warning(message: string) {
    addNotification('warning', message)
  }

  function info(message: string) {
    addNotification('info', message)
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info,
  }
})
