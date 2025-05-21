<template>
  <v-card class="pa-4">
    <v-card-title>Upload Dataset</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="handleSubmit">
        <v-text-field
          v-model="name"
          label="Dataset Name"
          required
        ></v-text-field>
        
        <v-textarea
          v-model="description"
          label="Description"
          rows="3"
        ></v-textarea>
        
        <v-file-input
          v-model="file"
          label="Dataset File"
          accept=".csv,.json"
          show-size
          required
        ></v-file-input>
        
        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          :disabled="!isValid"
        >
          Upload Dataset
        </v-btn>
      </v-form>
    </v-card-text>
    
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="3000"
    >
      {{ snackbar.message }}
    </v-snackbar>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'DatasetUpload',
  
  setup() {
    const name = ref('')
    const description = ref('')
    const file = ref<File | null>(null)
    const loading = ref(false)
    const snackbar = ref({
      show: false,
      message: '',
      color: 'success'
    })
    
    const isValid = computed(() => {
      return name.value && file.value
    })
    
    const handleSubmit = async () => {
      if (!isValid.value) return
      
      loading.value = true
      const formData = new FormData()
      formData.append('name', name.value)
      formData.append('description', description.value)
      if (file.value) {
        formData.append('file', file.value)
      }
      
      try {
        const response = await axios.post('http://localhost:8000/datasets/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        snackbar.value = {
          show: true,
          message: 'Dataset uploaded successfully!',
          color: 'success'
        }
        
        // Reset form
        name.value = ''
        description.value = ''
        file.value = null
        
      } catch (error) {
        snackbar.value = {
          show: true,
          message: 'Error uploading dataset',
          color: 'error'
        }
      } finally {
        loading.value = false
      }
    }
    
    return {
      name,
      description,
      file,
      loading,
      snackbar,
      isValid,
      handleSubmit
    }
  }
})
</script>

<style scoped>
.v-card {
  max-width: 600px;
  margin: 0 auto;
}
</style> 