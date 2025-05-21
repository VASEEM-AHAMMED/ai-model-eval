<template>
  <v-card class="pa-4">
    <v-card-title>Model Performance Metrics</v-card-title>
    
    <v-card-text>
      <div v-if="loading" class="text-center">
        <v-progress-circular indeterminate></v-progress-circular>
      </div>
      
      <div v-else-if="error" class="text-center red--text">
        {{ error }}
      </div>
      
      <div v-else>
        <!-- Metrics Overview -->
        <v-row>
          <v-col cols="12" md="6" v-for="(value, key) in latestMetrics" :key="key">
            <v-card outlined>
              <v-card-text>
                <div class="text-h6 text-capitalize">{{ formatMetricName(key) }}</div>
                <div class="text-h4">{{ formatMetricValue(value) }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Performance Chart -->
        <v-row class="mt-4">
          <v-col cols="12">
            <Line
              v-if="chartData"
              :data="chartData"
              :options="chartOptions"
            />
          </v-col>
        </v-row>
        
        <!-- Confusion Matrix -->
        <v-row class="mt-4" v-if="confusionMatrix">
          <v-col cols="12">
            <h3>Confusion Matrix</h3>
            <v-simple-table>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th></th>
                    <th v-for="(_, index) in confusionMatrix[0]" :key="index">
                      Predicted {{ index }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in confusionMatrix" :key="rowIndex">
                    <th>Actual {{ rowIndex }}</th>
                    <td v-for="(cell, cellIndex) in row" :key="cellIndex">
                      {{ cell }}
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
          </v-col>
        </v-row>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import axios from 'axios'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'MetricsVisualization',
  components: { Line },
  
  props: {
    datasetId: {
      type: Number,
      required: true
    }
  },
  
  setup(props) {
    const metrics = ref<any[]>([])
    const loading = ref(false)
    const error = ref('')
    
    const latestMetrics = computed(() => {
      if (!metrics.value.length) return {}
      const latest = metrics.value[metrics.value.length - 1]
      return {
        accuracy: latest.accuracy,
        precision: latest.precision,
        recall: latest.recall,
        f1_score: latest.f1_score
      }
    })
    
    const confusionMatrix = computed(() => {
      if (!metrics.value.length) return null
      return metrics.value[metrics.value.length - 1].confusion_matrix
    })
    
    const chartData = computed(() => {
      if (!metrics.value.length) return null
      
      return {
        labels: metrics.value.map((_, index) => `Evaluation ${index + 1}`),
        datasets: [
          {
            label: 'Accuracy',
            data: metrics.value.map(m => m.accuracy),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          },
          {
            label: 'Precision',
            data: metrics.value.map(m => m.precision),
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1
          },
          {
            label: 'Recall',
            data: metrics.value.map(m => m.recall),
            borderColor: 'rgb(54, 162, 235)',
            tension: 0.1
          },
          {
            label: 'F1 Score',
            data: metrics.value.map(m => m.f1_score),
            borderColor: 'rgb(153, 102, 255)',
            tension: 0.1
          }
        ]
      }
    })
    
    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 1
        }
      }
    }
    
    const fetchMetrics = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await axios.get(`http://localhost:8000/datasets/${props.datasetId}/metrics`)
        metrics.value = response.data
      } catch (e) {
        error.value = 'Error fetching metrics data'
        console.error(e)
      } finally {
        loading.value = false
      }
    }
    
    const formatMetricName = (name: string) => {
      return name.replace(/_/g, ' ')
    }
    
    const formatMetricValue = (value: number) => {
      return (value * 100).toFixed(2) + '%'
    }
    
    onMounted(() => {
      fetchMetrics()
    })
    
    return {
      loading,
      error,
      latestMetrics,
      confusionMatrix,
      chartData,
      chartOptions,
      formatMetricName,
      formatMetricValue
    }
  }
})
</script>

<style scoped>
.v-card {
  max-width: 1200px;
  margin: 0 auto;
}

.chart-container {
  height: 400px;
}
</style> 