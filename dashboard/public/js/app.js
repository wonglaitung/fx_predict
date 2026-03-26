// Main application logic
let autoRefreshInterval;
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Fetch data from API
async function fetchAPI(endpoint) {
  try {
    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
}

// Refresh all data
async function refreshData() {
  const refreshBtn = document.getElementById('refreshBtn');
  
  // Disable button and show spinning
  refreshBtn.disabled = true;
  refreshBtn.classList.add('spinning');
  
  try {
    // Fetch all data in parallel
    const [pairsData, strategiesData, consistencyData, riskData] = await Promise.all([
      fetchAPI('/api/v1/pairs'),
      fetchAPI('/api/v1/strategies'),
      fetchAPI('/api/v1/consistency'),
      fetchAPI('/api/v1/risk')
    ]);
    
    // Update UI
    renderOverviewCards(pairsData.pairs);
    renderStrategiesTable(strategiesData.strategies);
    renderConsistencyChart(consistencyData.consistency);
    renderRiskWarnings(riskData.risks);
    
    // Update last update time (use data date, not current time)
    if (pairsData.pairs && pairsData.pairs.length > 0) {
      const dataDate = pairsData.pairs[0].last_update;
      document.getElementById('lastUpdate').textContent = `Last: ${dataDate}`;
    }
    
  } catch (error) {
    console.error('Error refreshing data:', error);
    alert('数据加载失败，请重试');
  } finally {
    // Re-enable button and stop spinning
    refreshBtn.disabled = false;
    refreshBtn.classList.remove('spinning');
  }
}

// Start auto-refresh
function startAutoRefresh() {
  // Clear existing interval
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
  
  // Set new interval
  autoRefreshInterval = setInterval(() => {
    refreshData();
  }, AUTO_REFRESH_INTERVAL);
  
  // Show auto-refresh indicator
  document.getElementById('autoRefresh').textContent = 'Auto-refresh: 5min';
}

// Stop auto-refresh
function stopAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
  
  // Hide auto-refresh indicator
  document.getElementById('autoRefresh').textContent = '';
}

// Initialize application
async function init() {
  // Add event listener to refresh button
  document.getElementById('refreshBtn').addEventListener('click', refreshData);
  
  // Load initial data
  await refreshData();
  
  // Start auto-refresh
  startAutoRefresh();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Stop auto-refresh when page is hidden
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopAutoRefresh();
  } else {
    startAutoRefresh();
  }
});