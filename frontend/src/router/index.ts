import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public routes
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      children: [
        {
          path: '',
          name: 'landing',
          component: () => import('@/views/public/LandingPage.vue'),
        },
      ],
    },
    {
      path: '/login',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: '',
          name: 'login',
          component: () => import('@/views/public/LoginPage.vue'),
        },
      ],
    },

    // Applicant routes
    {
      path: '/dashboard',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'applicant-dashboard',
          component: () => import('@/views/applicant/ApplicantDashboard.vue'),
        },
      ],
    },
    {
      path: '/applications',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'new',
          name: 'application-new',
          component: () => import('@/views/applicant/ApplicationForm.vue'),
        },
        {
          path: 'review',
          name: 'application-review-submit',
          component: () => import('@/views/applicant/ApplicationReviewSubmit.vue'),
        },
        {
          path: ':id',
          name: 'application-detail',
          component: () => import('@/views/applicant/ApplicationDetail.vue'),
          props: true,
        },
      ],
    },

    // Reviewer routes
    {
      path: '/reviews',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true, roles: ['reviewer', 'admin'] },
      children: [
        {
          path: '',
          name: 'reviewer-dashboard',
          component: () => import('@/views/reviewer/ReviewerDashboard.vue'),
        },
        {
          path: ':appId',
          name: 'application-review',
          component: () => import('@/views/reviewer/ApplicationReview.vue'),
          props: true,
        },
        {
          path: 'compare',
          name: 'application-compare',
          component: () => import('@/views/reviewer/ApplicationCompare.vue'),
        },
      ],
    },

    // Vulnerability routes
    {
      path: '/vulnerability',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true, roles: ['reviewer', 'admin'] },
      children: [
        {
          path: '',
          name: 'heatmap',
          component: () => import('@/views/vulnerability/HeatmapView.vue'),
        },
        {
          path: 'compare',
          name: 'region-comparison',
          component: () => import('@/views/vulnerability/RegionComparison.vue'),
        },
        {
          path: 'indicators',
          name: 'indicator-explorer',
          component: () => import('@/views/vulnerability/IndicatorExplorer.vue'),
        },
        {
          path: 'data-sources',
          name: 'data-source-status',
          component: () => import('@/views/vulnerability/DataSourceStatus.vue'),
          meta: { roles: ['admin'] },
        },
      ],
    },

    // Reports routes
    {
      path: '/reports',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        {
          path: '',
          name: 'report-generator',
          component: () => import('@/views/reports/ReportGenerator.vue'),
        },
      ],
    },

    // Admin routes
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboard.vue'),
        },
        {
          path: 'users',
          name: 'user-management',
          component: () => import('@/views/admin/UserManagement.vue'),
        },
        {
          path: 'config',
          name: 'system-config',
          component: () => import('@/views/admin/SystemConfig.vue'),
        },
      ],
    },
  ],
})

// Auth guard
router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Role check
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && authStore.user) {
    if (!requiredRoles.includes(authStore.user.role)) {
      return { name: 'applicant-dashboard' }
    }
  }

  return true
})

export default router

// Type augmentation for route meta
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: string[]
  }
}
