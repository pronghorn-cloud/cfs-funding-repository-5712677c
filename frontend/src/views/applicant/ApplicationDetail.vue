<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useApplicationsStore } from '@/stores/applications'
import { applicationsService } from '@/services/applications.service'
import type { Comment } from '@/types'

const route = useRoute()
const appStore = useApplicationsStore()

const comments = ref<Comment[]>([])
const newComment = ref('')

const appId = route.params.id as string

onMounted(async () => {
  await appStore.fetchApplication(appId)
  comments.value = await applicationsService.listComments(appId)
})

async function addComment() {
  if (!newComment.value.trim()) return
  const comment = await applicationsService.addComment(appId, newComment.value)
  comments.value.unshift(comment)
  newComment.value = ''
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'approved': return 'text-goa-success'
    case 'denied': return 'text-goa-emergency'
    case 'submitted': case 'under_review': return 'text-goa-blue'
    default: return 'text-gray-600'
  }
}
</script>

<template>
  <div>
    <goa-spinner v-if="appStore.isLoading" />

    <template v-else-if="appStore.currentApplication">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-3xl font-bold">{{ appStore.currentApplication.title }}</h1>
          <p class="text-gray-600 mt-1">
            Type: {{ appStore.currentApplication.funding_type }} |
            Fiscal Year: {{ appStore.currentApplication.fiscal_year || 'N/A' }}
          </p>
        </div>
        <goa-badge
          :content="appStore.currentApplication.status"
          :type="appStore.currentApplication.status === 'approved' ? 'success' : 'information'"
        />
      </div>

      <!-- Details Card -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Application Details</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm text-gray-500">Amount Requested</label>
            <p class="font-semibold">
              {{ appStore.currentApplication.amount_requested
                ? `$${Number(appStore.currentApplication.amount_requested).toLocaleString()}`
                : 'Not specified' }}
            </p>
          </div>
          <div>
            <label class="text-sm text-gray-500">Amount Approved</label>
            <p class="font-semibold">
              {{ appStore.currentApplication.amount_approved
                ? `$${Number(appStore.currentApplication.amount_approved).toLocaleString()}`
                : 'Pending' }}
            </p>
          </div>
          <div>
            <label class="text-sm text-gray-500">Submitted</label>
            <p>{{ appStore.currentApplication.submitted_at
              ? new Date(appStore.currentApplication.submitted_at).toLocaleString()
              : 'Not submitted' }}</p>
          </div>
          <div>
            <label class="text-sm text-gray-500">Last Updated</label>
            <p>{{ new Date(appStore.currentApplication.updated_at).toLocaleString() }}</p>
          </div>
        </div>
        <div v-if="appStore.currentApplication.description" class="mt-4">
          <label class="text-sm text-gray-500">Description</label>
          <p>{{ appStore.currentApplication.description }}</p>
        </div>
      </div>

      <!-- Sections -->
      <div class="bg-white rounded-lg shadow p-6 mb-6" v-if="appStore.currentApplication.sections.length > 0">
        <h2 class="text-xl font-semibold mb-4">Application Sections</h2>
        <div v-for="section in appStore.currentApplication.sections" :key="section.id" class="border-b last:border-0 py-3">
          <div class="flex justify-between items-center">
            <span class="font-medium">{{ section.section_type.replace(/_/g, ' ') }}</span>
            <goa-badge :content="section.is_complete ? 'Complete' : 'Incomplete'" :type="section.is_complete ? 'success' : 'midtone'" />
          </div>
        </div>
      </div>

      <!-- Comments -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Comments</h2>

        <div class="mb-4">
          <goa-form-item label="Add a comment">
            <goa-textarea
              name="comment"
              :value="newComment"
              @_change="(e: any) => newComment = e.detail.value"
              rows="3"
              placeholder="Enter your comment..."
            />
          </goa-form-item>
          <goa-button type="primary" size="compact" @_click="addComment" class="mt-2">
            Post Comment
          </goa-button>
        </div>

        <div v-for="comment in comments" :key="comment.id" class="border-t py-3">
          <div class="flex justify-between text-sm text-gray-500">
            <span>{{ comment.user_id }}</span>
            <span>{{ new Date(comment.created_at).toLocaleString() }}</span>
          </div>
          <p class="mt-1">{{ comment.content }}</p>
          <goa-badge v-if="comment.is_internal" content="Internal" type="midtone" class="mt-1" />
        </div>

        <p v-if="comments.length === 0" class="text-gray-500 text-center py-4">No comments yet</p>
      </div>
    </template>
  </div>
</template>
