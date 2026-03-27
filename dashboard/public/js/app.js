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
  try {
    // Fetch all data in parallel
    const [pairsData, strategiesData, riskData] = await Promise.all([
      fetchAPI('/api/v1/pairs'),
      fetchAPI('/api/v1/strategies'),
      fetchAPI('/api/v1/risk')
    ]);
    
    // Update UI
    renderOverviewCards(pairsData.pairs);
    renderStrategiesTable(strategiesData.strategies, pairsData.pairs);
    renderRiskWarnings(riskData.risks, pairsData.pairs);
    
    // Populate pair selector
    populatePairSelector(pairsData.pairs);
    
    // Render indicator charts for first pair (EUR if available, otherwise first pair)
    if (pairsData.pairs && pairsData.pairs.length > 0) {
      // Try to find EUR first
      const eurPair = pairsData.pairs.find(p => p.pair === 'EUR');
      const selectedPair = eurPair ? eurPair.pair : pairsData.pairs[0].pair;
      renderIndicatorCharts(selectedPair);
    }
    
    // Update last update time (use data date, not current time)
    if (pairsData.pairs && pairsData.pairs.length > 0) {
      const dataDate = pairsData.pairs[0].last_update;
      document.getElementById('lastUpdate').textContent = dataDate;
    }
    
    // Update last refresh time (current time)
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById('lastRefresh').textContent = `最后刷新: ${timeString}`;
    
  } catch (error) {
    console.error('Error refreshing data:', error);
    alert('数据加载失败，请重试');
  }
}

// Populate pair selector dropdown
function populatePairSelector(pairs) {
  const selector = document.getElementById('pairSelector');
  if (!selector) return;
  
  // Store current selection
  const currentValue = selector.value;
  
  // Clear existing options
  selector.innerHTML = '<option value="">选择货币对...</option>';
  
  // Add options for each pair
  pairs.forEach(pair => {
    const option = document.createElement('option');
    option.value = pair.pair;
    option.textContent = pair.pair_name;
    selector.appendChild(option);
  });
  
  // Restore selection if valid, otherwise select EUR or first pair
  if (currentValue && pairs.find(p => p.pair === currentValue)) {
    selector.value = currentValue;
  } else {
    // Try to select EUR
    const eurPair = pairs.find(p => p.pair === 'EUR');
    if (eurPair) {
      selector.value = 'EUR';
    } else if (pairs.length > 0) {
      selector.value = pairs[0].pair;
    }
  }
}

// Handle pair selection change
function handlePairChange() {
  const selector = document.getElementById('pairSelector');
  if (!selector || !selector.value) return;
  
  renderIndicatorCharts(selector.value);
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
  // Add event listener to pair selector
  const pairSelector = document.getElementById('pairSelector');
  if (pairSelector) {
    pairSelector.addEventListener('change', handlePairChange);
  }
  
  // Add sidebar close events
  const closeBtn = document.getElementById('closeSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  if (closeBtn) {
    closeBtn.addEventListener('click', closeAnalysisSidebar);
  }
  
  if (overlay) {
    overlay.addEventListener('click', closeAnalysisSidebar);
  }
  
  // Initialize strategy table row click handlers
  setupStrategyTableRowClick();
  
  // Initialize tab click event listeners
  initializeTabListeners();
  
  // Load initial data
  await refreshData();
  
  // Start auto-refresh
  startAutoRefresh();
}

// Close analysis sidebar
function closeAnalysisSidebar() {
  const sidebar = document.getElementById('analysisSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  sidebar.classList.remove('sidebar-open');
  overlay.classList.remove('sidebar-overlay-open');
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