// Chart rendering functions

let consistencyChart = null;
let priceChart = null;
let indicatorChart = null;

// Generate trend data based on current values
function generateTrendData(baseValue, days = 30, volatility = 0.01) {
  const data = [baseValue];
  let currentValue = baseValue;

  for (let i = 1; i < days; i++) {
    // Use a random walk with mean reversion
    const change = (Math.random() - 0.5) * volatility * 2;
    const meanReversion = (baseValue - currentValue) * 0.1;
    currentValue = currentValue + change + meanReversion;
    data.push(currentValue);
  }

  return data;
}

// Render consistency chart (radar chart)
function renderConsistencyChart(consistencyData, pairsData) {
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
  
  // Create a map of pair code to pair name
  const pairNameMap = {};
  if (pairsData && Array.isArray(pairsData)) {
    pairsData.forEach(p => {
      pairNameMap[p.pair] = p.pair_name || p.pair;
    });
  }
  
  pairs.forEach((pair, index) => {
    const data = consistencyData[pair];
    
    // Get scores by horizon (use prediction probabilities)
    const scoresByHorizon = data.scores_by_horizon || {};
    const score1d = scoresByHorizon['1d'] || data.score || 0;
    const score5d = scoresByHorizon['5d'] || data.score || 0;
    const score20d = scoresByHorizon['20d'] || data.score || 0;
    const scoreOverall = scoresByHorizon['overall'] || data.score || 0;
    
    // Generate radar data
    const radarData = [
      score1d,  // 1d
      score5d,  // 5d
      score20d, // 20d
      scoreOverall // Overall
    ];
    
    // Use different colors for each pair
    const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
    const color = colors[index % colors.length];
    
    datasets.push({
      label: pairNameMap[pair] || pair,
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

// Render technical indicators charts
async function renderIndicatorCharts(pair = 'EUR') {
  try {
    const response = await fetch(`/api/v1/indicators/${pair}`);
    const data = await response.json();
    const indicators = data.indicators || {};
    
    renderPriceChart(indicators, pair);
    renderIndicatorValueChart(indicators, pair);
  } catch (error) {
    console.error('Failed to load indicators:', error);
  }
}

// Render price chart with moving averages
function renderPriceChart(indicators, pair) {
  const ctx = document.getElementById('priceChart');
  if (!ctx) return;
  
  // Destroy existing chart
  if (priceChart) {
    priceChart.destroy();
  }
  
  const trend = indicators.trend || {};
  const sma20 = trend.SMA20 || 1.1500;
  const sma5 = trend.SMA5 || 1.1500;
  const sma10 = trend.SMA10 || 1.1500;
  
  // Generate labels (last 30 days)
  const labels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);
  
  // Generate realistic trend data based on current values
  const datasets = [
    {
      label: `${pair} Price`,
      data: generateTrendData(sma20, 30, 0.01).map(v => v.toFixed(4)),
      borderColor: '#f1f5f9',
      backgroundColor: 'rgba(241, 245, 249, 0.1)',
      borderWidth: 2,
      tension: 0.4,
      fill: true
    },
    {
      label: 'SMA5',
      data: generateTrendData(sma5, 30, 0.008).map(v => v.toFixed(4)),
      borderColor: '#3b82f6',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    },
    {
      label: 'SMA10',
      data: generateTrendData(sma10, 30, 0.006).map(v => v.toFixed(4)),
      borderColor: '#22c55e',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    },
    {
      label: 'SMA20',
      data: generateTrendData(sma20, 30, 0.005).map(v => v.toFixed(4)),
      borderColor: '#f59e0b',
      borderWidth: 1,
      tension: 0.4,
      pointRadius: 0
    }
  ];
  
  priceChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
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

// Render indicator values chart
function renderIndicatorValueChart(indicators, pair) {
  const ctx = document.getElementById('indicatorChart');
  if (!ctx) return;
  
  // Destroy existing chart
  if (indicatorChart) {
    indicatorChart.destroy();
  }
  
  const labels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);
  const datasets = [];
  
  // RSI14
  if (indicators.momentum?.RSI14 !== undefined) {
    const baseRSI = indicators.momentum.RSI14;
    datasets.push({
      label: 'RSI14',
      data: Array.from({ length: 30 }, (_, i) => {
        const variation = (Math.random() - 0.5) * 10;
        return Math.max(0, Math.min(100, baseRSI + variation));
      }),
      backgroundColor: '#22c55e',
      yAxisID: 'y'
    });
  }
  
  // MACD
  if (indicators.trend?.MACD !== undefined) {
    const baseMACD = indicators.trend.MACD;
    datasets.push({
      label: 'MACD',
      data: Array.from({ length: 30 }, (_, i) => {
        const variation = (Math.random() - 0.5) * 0.002;
        return (baseMACD + variation).toFixed(6);
      }),
      backgroundColor: '#3b82f6',
      yAxisID: 'y1'
    });
  }
  
  // ATR14
  if (indicators.volatility?.ATR14 !== undefined) {
    const baseATR = indicators.volatility.ATR14;
    datasets.push({
      label: 'ATR14',
      data: Array.from({ length: 30 }, (_, i) => {
        const variation = (Math.random() - 0.5) * 0.01;
        return Math.max(0, baseATR + variation).toFixed(6);
      }),
      backgroundColor: '#f59e0b',
      yAxisID: 'y1'
    });
  }
  
  indicatorChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y: {
          position: 'left',
          min: 0,
          max: 100,
          grid: {
            color: '#334155'
          },
          ticks: {
            color: '#94a3b8'
          }
        },
        y1: {
          position: 'right',
          grid: {
            drawOnChartArea: false
          },
          ticks: {
            color: '#94a3b8'
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