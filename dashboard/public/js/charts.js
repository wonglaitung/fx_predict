// Chart rendering functions

let consistencyChart = null;

// Render consistency chart (radar chart)
function renderConsistencyChart(consistencyData) {
  const ctx = document.getElementById('consistencyChart');
  if (!ctx) return;
  
  // Destroy existing chart
  if (consistencyChart) {
    consistencyChart.destroy();
  }
  
  // Prepare data
  const pairs = Object.keys(consistencyData);
  const labels = ['1d', '5d', '20d', 'Overall'];
  const datasets = [];
  
  pairs.forEach((pair, index) => {
    const data = consistencyData[pair];
    const score = data.score || 0;
    
    // Generate radar data
    const radarData = [
      score, // 1d
      score, // 5d
      score, // 20d
      score  // Overall
    ];
    
    // Use different colors for each pair
    const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
    const color = colors[index % colors.length];
    
    datasets.push({
      label: pair,
      data: radarData,
      backgroundColor: color + '33', // 20% opacity
      borderColor: color,
      borderWidth: 2
    });
  });
  
  // Create chart
  consistencyChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          grid: {
            color: '#334155'
          },
          angleLines: {
            color: '#334155'
          },
          pointLabels: {
            color: '#f1f5f9',
            font: {
              size: 12
            }
          },
          ticks: {
            color: '#94a3b8',
            backdropColor: 'transparent'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#f1f5f9'
          }
        }
      }
    }
  });
}

// Note: Price and indicator charts will be added in Task 13
// This is a placeholder for now