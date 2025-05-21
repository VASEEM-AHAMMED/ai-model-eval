<template>
  <div class="dataset-management">
    <h1 class="text-h4 mb-6">Dataset Management</h1>
    
    <!-- Dataset Upload Section -->
    <section class="mb-8">
      <DatasetUpload @upload-success="handleUploadSuccess" />
    </section>
    
    <!-- Dataset List and Metrics -->
    <section>
      <v-card>
        <v-card-title>
          Datasets
          <v-spacer></v-spacer>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
        </v-card-title>
        
        <v-data-table
          :headers="headers"
          :items="datasets"
          :search="search"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <v-btn
              color="primary"
              text
              @click="viewMetrics(item)"
            >
              View Metrics
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
    </section>
    
    <!-- Metrics Dialog -->
    <v-dialog
      v-model="metricsDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn
            icon
            dark
            @click="metricsDialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Dataset Metrics</v-toolbar-title>
        </v-toolbar>
        
        <v-card-text>
          <MetricsVisualization
            v-if="selectedDataset"
            :dataset-id="selectedDataset.id"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import DatasetUpload from '../components/DatasetUpload.vue'
import MetricsVisualization from '../components/MetricsVisualization.vue'
import axios from 'axios'

export default defineComponent({
  name: 'DatasetManagement',
  
  components: {
    DatasetUpload,
    MetricsVisualization
  },
  
  setup() {
    const datasets = ref([])
    const loading = ref(false)
    const search = ref('')
    const metricsDialog = ref(false)
    const selectedDataset = ref(null)
    
    const headers = [
      { text: 'Name', value: 'name' },
      { text: 'Description', value: 'description' },
      { text: 'Format', value: 'format' },
      { text: 'Size', value: 'size' },
      { text: 'Created At', value: 'created_at' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]
    
    const fetchDatasets = async () => {
      loading.value = true
      try {
        const response = await axios.get('http://localhost:8000/datasets/')
        datasets.value = response.data
      } catch (error) {
        console.error('Error fetching datasets:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleUploadSuccess = () => {
      fetchDatasets()
    }
    
    const viewMetrics = (dataset: any) => {
      selectedDataset.value = dataset
      metricsDialog.value = true
    }
    
    onMounted(() => {
      fetchDatasets()
    })
    
    return {
      datasets,
      loading,
      search,
      headers,
      metricsDialog,
      selectedDataset,
      handleUploadSuccess,
      viewMetrics
    }
  }
})
</script>

<style scoped>
.dataset-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
</style> 