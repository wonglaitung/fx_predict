// Main application logic
let autoRefreshInterval;
let countdownInterval;
let remainingSeconds = 5 * 60; // 5 minutes in seconds
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
  console.log('🔄 开始刷新数据...', new Date().toLocaleTimeString());
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
    
    // Reset countdown timer
    remainingSeconds = 5 * 60;
    updateCountdown();
    
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

// Update countdown display
function updateCountdown() {
  const countdownElement = document.getElementById('refreshCountdown');
  if (countdownElement) {
    countdownElement.textContent = `${remainingSeconds} 秒后刷新`;
  }
}

// Start countdown timer
function startCountdown() {
  // Clear existing intervals
  if (countdownInterval) {
    clearInterval(countdownInterval);
  }
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
  
  // Start countdown timer (every second)
  countdownInterval = setInterval(() => {
    remainingSeconds--;
    if (remainingSeconds <= 0) {
      // Time to refresh
      refreshData();
    }
    updateCountdown();
  }, 1000);
}

// Stop countdown timer
function stopCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
  
  const countdownElement = document.getElementById('refreshCountdown');
  if (countdownElement) {
    countdownElement.textContent = '';
  }
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
  
  // Start countdown
  startCountdown();
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

// Stop countdown when page is hidden
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopCountdown();
  } else {
    startCountdown();
  }
});

// File Upload Functionality
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const submitUploadBtn = document.getElementById('submitUploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
let selectedFile = null;

// Handle file selection button click
uploadBtn.addEventListener('click', () => {
  fileInput.click();
});

// Handle file input change
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    // Validate file type
    if (!file.name.endsWith('.xlsx')) {
      showUploadStatus('error', '只接受 .xlsx 格式的文件');
      selectedFile = null;
      submitUploadBtn.disabled = true;
      uploadBtn.textContent = '选择文件';
      return;
    }
    
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      showUploadStatus('error', '文件大小不能超过 10MB');
      selectedFile = null;
      submitUploadBtn.disabled = true;
      uploadBtn.textContent = '选择文件';
      return;
    }
    
    selectedFile = file;
    uploadBtn.textContent = `已选择: ${file.name}`;
    submitUploadBtn.disabled = false;
    hideUploadStatus();
  }
});

// Handle upload button click
submitUploadBtn.addEventListener('click', async () => {
  if (!selectedFile) {
    showUploadStatus('error', '请先选择文件');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', selectedFile);
  
  showUploadStatus('loading', '正在上传文件...');
  showUploadProgress(0);
  
  try {
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
      progress += 10;
      if (progress < 90) {
        showUploadProgress(progress);
      }
    }, 200);
    
    const response = await fetch('/api/v1/upload', {
      method: 'POST',
      body: formData
    });
    
    clearInterval(progressInterval);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || '上传失败');
    }
    
    const result = await response.json();
    showUploadProgress(100);
    
    // Success message
    showUploadStatus('success', `文件上传成功: ${result.file.filename} (${(result.file.size / 1024).toFixed(2)} KB)`);
    
    // Reset file selection
    selectedFile = null;
    fileInput.value = '';
    uploadBtn.textContent = '选择文件';
    submitUploadBtn.disabled = true;
    
    // Hide progress after 2 seconds
    setTimeout(() => {
      hideUploadProgress();
    }, 2000);
    
    // Refresh data after successful upload
    setTimeout(async () => {
      await refreshData();
    }, 1000);
    
  } catch (error) {
    console.error('Upload error:', error);
    showUploadStatus('error', `上传失败: ${error.message}`);
    hideUploadProgress();
  }
});

// Show upload status message
function showUploadStatus(type, message) {
  uploadStatus.textContent = message;
  uploadStatus.className = `upload-status show ${type}`;
}

// Hide upload status message
function hideUploadStatus() {
  uploadStatus.className = 'upload-status';
}

// Show upload progress
function showUploadProgress(percent) {
  uploadProgress.classList.add('show');
  progressFill.style.width = `${percent}%`;
  progressText.textContent = `${percent}%`;
}

// Hide upload progress
function hideUploadProgress() {
  uploadProgress.classList.remove('show');
  progressFill.style.width = '0%';
  progressText.textContent = '0%';
}