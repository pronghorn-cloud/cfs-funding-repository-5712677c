<script setup lang="ts">
import { ref } from 'vue'

// Placeholder user management
const users = ref([
  { id: '1', email: 'admin@example.com', display_name: 'Admin User', role: 'admin', is_active: true },
  { id: '2', email: 'reviewer@example.com', display_name: 'Reviewer User', role: 'reviewer', is_active: true },
  { id: '3', email: 'applicant@example.com', display_name: 'Applicant User', role: 'applicant', is_active: true },
])
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">User Management</h1>

    <div class="bg-white rounded-lg shadow">
      <goa-table class="w-full">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="font-medium">{{ user.display_name }}</td>
            <td>{{ user.email }}</td>
            <td>
              <goa-badge :content="user.role" />
            </td>
            <td>
              <goa-badge :content="user.is_active ? 'Active' : 'Inactive'" :type="user.is_active ? 'success' : 'midtone'" />
            </td>
            <td>
              <goa-button type="tertiary" size="compact">Edit</goa-button>
            </td>
          </tr>
        </tbody>
      </goa-table>
    </div>
  </div>
</template>
