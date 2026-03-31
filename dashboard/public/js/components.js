// UI Components rendering functions

// Global state for sidebar management
let currentSidebarTrigger = null; // 'card' | 'strategy'
let currentSidebarData = null;
let currentActiveTab = null;      // 'llm' | 'indicators'

// Initialize tab click event listeners
function initializeTabListeners() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;
      if (tabName) {
        switchTab(tabName);
      }
    });
  });
}

// Render overview cards
function renderOverviewCards(pairs) {
  const container = document.getElementById('overviewCards');
  container.innerHTML = '';
  
  pairs.forEach(pair => {
    const card = document.createElement('div');
    card.className = 'card card-clickable';
    
    // Get multi-horizon predictions
    const predictions = pair.predictions || {};
    const pred1d = predictions['1d'] || {};
    const pred5d = predictions['5d'] || {};
    const pred20d = predictions['20d'] || {};
    
    // Helper function to get icon and class
    const getIconInfo = (predictionText) => {
      const predictionMap = {
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有',
        '上涨': '上涨',
        '下跌': '下跌'
      };
      const displayPrediction = predictionMap[predictionText] || predictionText;
      
      if (displayPrediction === '买入' || displayPrediction === '上涨') {
        return { icon: '↗', iconClass: 'prediction-up' };
      } else if (displayPrediction === '卖出' || displayPrediction === '下跌') {
        return { icon: '↘', iconClass: 'prediction-down' };
      } else {
        return { icon: '→', iconClass: 'prediction-neutral' };
      }
    };
    
    const icon1d = getIconInfo(pred1d.prediction);
    const icon5d = getIconInfo(pred5d.prediction);
    const icon20d = getIconInfo(pred20d.prediction);
    
    // Translate confidence to Chinese
    const confidenceMap = {
      'high': '高',
      'medium': '中',
      'low': '低',
      'unknown': '未知'
    };
    
    // Get analysis summary (truncate if too long)
    const summary = pair.llm_analysis?.summary || '暂无分析';
    const truncatedSummary = summary.length > 50 ? summary.substring(0, 50) + '...' : summary;
    
    // Format probability and confidence for each horizon
    const formatPredictionInfo = (pred) => {
      const probabilityPercent = (pred.probability * 100).toFixed(4) + '%';
      const displayConfidence = confidenceMap[pred.confidence] || 'unknown';
      return `${probabilityPercent} (${displayConfidence})`;
    };
    
    card.innerHTML = `
      <div class="card-title">${pair.pair_name}</div>
      <div class="card-price">${pair.current_price.toFixed(4)}</div>
      <div class="card-predictions">
        <div class="prediction-item">
          <span class="prediction-label">1天</span>
          <span class="prediction-icon ${icon1d.iconClass}">${icon1d.icon}</span>
          <span class="prediction-info">${formatPredictionInfo(pred1d)}</span>
        </div>
        <div class="prediction-item">
          <span class="prediction-label">5天</span>
          <span class="prediction-icon ${icon5d.iconClass}">${icon5d.icon}</span>
          <span class="prediction-info">${formatPredictionInfo(pred5d)}</span>
        </div>
        <div class="prediction-item">
          <span class="prediction-label">20天</span>
          <span class="prediction-icon ${icon20d.iconClass}">${icon20d.icon}</span>
          <span class="prediction-info">${formatPredictionInfo(pred20d)}</span>
        </div>
      </div>
      <div class="card-summary">${truncatedSummary}</div>
      <div class="card-footer">
        <div class="card-date">${pair.last_update}</div>
        <div class="card-hint">查看详情 →</div>
      </div>
    `;
    
    // Add click event to open sidebar
    card.addEventListener('click', () => {
      openAnalysisSidebar(pair);
    });
    
    container.appendChild(card);
  });
}

// Render strategies table
function renderStrategiesTable(strategies, pairs) {
  const tbody = document.querySelector('#strategiesTable tbody');
  tbody.innerHTML = '';
  
  // Create a map of pair code to pair name
  const pairNameMap = {};
  if (pairs && Array.isArray(pairs)) {
    pairs.forEach(p => {
      pairNameMap[p.pair] = p.pair_name || p.pair;
    });
  }
  
  Object.entries(strategies).forEach(([pair, pairStrategies]) => {
    const pairName = pairNameMap[pair] || pair;
    pairStrategies.forEach(strategy => {
      const row = document.createElement('tr');
      // Add data attributes for row click handler
      row.dataset.pair = pair;
      row.dataset.horizon = strategy.horizon;
      row.innerHTML = `
        <td>${pairName}</td>
        <td>${strategy.horizon}</td>
        <td><span class="strategy-direction strategy-${strategy.direction}">${strategy.direction}</span></td>
        <td>${strategy.confidence}</td>
        <td>${strategy.entry_price.toFixed(4)}</td>
        <td>${strategy.stop_loss.toFixed(4)}</td>
        <td>${strategy.take_profit.toFixed(4)}</td>
      `;
      tbody.appendChild(row);
    });
  });
}

// Render risk warnings
function renderRiskWarnings(risks, pairs) {
  const container = document.getElementById('riskWarnings');
  container.innerHTML = '';
  
  // Create a map of pair code to pair name
  const pairNameMap = {};
  if (pairs && Array.isArray(pairs)) {
    pairs.forEach(p => {
      pairNameMap[p.pair] = p.pair_name || p.pair;
    });
  }
  
  let hasWarnings = false;
  
  Object.entries(risks).forEach(([pair, risk]) => {
    if (risk.warnings && risk.warnings.length > 0) {
      hasWarnings = true;
      const pairName = pairNameMap[pair] || pair;
      risk.warnings.forEach(warning => {
        const warningEl = document.createElement('div');
        warningEl.className = 'risk-warning';
        warningEl.innerHTML = `
          <span class="risk-icon">⚠️</span>
          <span>${pairName}: ${warning}</span>
        `;
        container.appendChild(warningEl);
      });
    }
  });
  
  if (!hasWarnings) {
    container.innerHTML = '<p>暂无风险提示</p>';
  }
}

// Open analysis sidebar
function openAnalysisSidebar(pair) {
  const sidebar = document.getElementById('analysisSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  renderSidebarContent(pair);
  
  sidebar.classList.add('sidebar-open');
  overlay.classList.add('sidebar-overlay-open');
}

// Render sidebar content (LLM Analysis)
function renderSidebarContent(pair) {
  const container = document.getElementById('llmTab');
  const analysis = pair.llm_analysis || {};
  const currentPrice = pair.current_price !== undefined && pair.current_price !== null 
    ? pair.current_price.toFixed(4) 
    : 'N/A';
  
  container.innerHTML = `
    <div class="sidebar-section">
      <h3 class="sidebar-section-title">基本信息</h3>
      <div class="sidebar-info-grid">
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">货币对</span>
          <span class="sidebar-info-value">${pair.pair_name || '未知'}</span>
        </div>
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">当前价格</span>
          <span class="sidebar-info-value">${currentPrice}</span>
        </div>
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">整体评估</span>
          <span class="sidebar-info-value">${analysis.overall_assessment || '未知'}</span>
        </div>
      </div>
    </div>
    
    <div class="sidebar-section">
      <h3 class="sidebar-section-title">分析摘要</h3>
      <p class="sidebar-text">${analysis.summary || '暂无分析'}</p>
    </div>
    
    <div class="sidebar-section">
      <h3 class="sidebar-section-title">关键因素</h3>
      ${analysis.key_factors && analysis.key_factors.length > 0 
        ? '<ul class="sidebar-list">' + 
          analysis.key_factors.map(factor => `<li class="sidebar-list-item">${factor}</li>`).join('') + 
          '</ul>' 
        : '<p class="sidebar-text">暂无关键因素</p>'}
    </div>
    
    <div class="sidebar-section">
      <h3 class="sidebar-section-title">各周期分析</h3>
      ${renderHorizonAnalysis(analysis.horizon_analysis)}
    </div>
  `;
}

// Render horizon analysis
function renderHorizonAnalysis(horizonAnalysis) {
  if (!horizonAnalysis || Object.keys(horizonAnalysis).length === 0) {
    return '<p class="sidebar-text">暂无周期分析</p>';
  }
  
  const horizonNames = {
    '1': '短线（1天）',
    '5': '中线（5天）',
    '20': '长线（20天）'
  };
  
  const recommendationMap = {
    'buy': '买入',
    'sell': '卖出',
    'hold': '持有'
  };
  
  const confidenceMap = {
    'high': '高',
    'medium': '中',
    'low': '低',
    'unknown': '未知'
  };
  
  return Object.entries(horizonAnalysis).map(([horizon, analysis]) => `
    <div class="horizon-card">
      <div class="horizon-header">
        <span class="horizon-name">${horizonNames[horizon] || horizon}</span>
        <span class="horizon-recommendation horizon-${analysis.recommendation}">${recommendationMap[analysis.recommendation] || analysis.recommendation}</span>
        <span class="horizon-confidence">置信度: ${confidenceMap[analysis.confidence] || analysis.confidence}</span>
      </div>
      <p class="horizon-analysis">${analysis.analysis || '暂无分析'}</p>
      ${analysis.key_points && analysis.key_points.length > 0 
        ? '<ul class="horizon-points">' + 
          analysis.key_points.map(point => `<li>${point}</li>`).join('') + 
          '</ul>' 
        : ''}
    </div>
  `).join('');
}

// Setup strategy table row click handlers
function setupStrategyTableRowClick() {
  const tbody = document.querySelector('#strategiesTable tbody');
  if (!tbody) return;
  
  tbody.addEventListener('click', (e) => {
    const row = e.target.closest('tr');
    if (!row) return;
    
    const pair = row.dataset.pair;
    const horizon = row.dataset.horizon;
    
    if (pair && horizon) {
      openStrategyIndicators(pair, horizon);
    }
  });
}

// Open strategy indicators sidebar
function openStrategyIndicators(pair, horizon) {
  const sidebar = document.getElementById('analysisSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  // Update sidebar title
  const title = document.getElementById('sidebarTitle');
  title.textContent = '技术指标详情';
  
  // Show tabs
  const tabs = document.getElementById('sidebarTabs');
  tabs.style.display = 'flex';
  
  // Show loading state
  showLoadingState();
  
  // Update state
  currentSidebarTrigger = 'strategy';
  
  // Fetch data from API
  fetch(`/api/v1/strategies/${pair}/${horizon}/indicators`)
    .then(response => response.json())
    .then(data => {
      currentSidebarData = data;
      
      // Render strategy indicators
      renderStrategyIndicators(data);
      
      // Switch to indicators tab by default
      switchTab('indicators');
      
      hideLoadingState();
      
      // Open sidebar
      sidebar.classList.add('sidebar-open');
      overlay.classList.add('sidebar-overlay-open');
    })
    .catch(error => {
      console.error('Error fetching strategy indicators:', error);
      hideLoadingState();
      document.getElementById('sidebarContent').innerHTML = `
        <p class="sidebar-text">加载技术指标失败: ${error.message}</p>
      `;
      sidebar.classList.add('sidebar-open');
      overlay.classList.add('sidebar-overlay-open');
    });
}

// Show loading state
function showLoadingState() {
  const indicatorsTab = document.getElementById('indicatorsTab');
  indicatorsTab.innerHTML = `
    <div class="loading-container">
      <div class="loader"></div>
      <p class="sidebar-text">加载中...</p>
    </div>
  `;
}

// Hide loading state
function hideLoadingState() {
  // Loading state is removed when content is rendered
}

// Render strategy indicators
function renderStrategyIndicators(data) {
  const container = document.getElementById('indicatorsTab');
  const { pair_name, horizon_name, current_price, overall_summary, key_indicators } = data;
  
  container.innerHTML = `
    <div class="strategy-indicators-header">
      <div class="strategy-info">
        <h3>${pair_name} - ${horizon_name}</h3>
        <div class="current-price">当前价格: ${current_price.toFixed(4)}</div>
      </div>
    </div>
    
    <div class="overall-summary">
      <strong>整体分析：</strong>${overall_summary}
    </div>
    
    <div class="indicator-cards">
      ${renderIndicatorCard('支撑与阻力', key_indicators.support_resistance)}
      ${renderIndicatorCard('趋势强度', key_indicators.trend_strength)}
      ${renderIndicatorCard('动量指标', key_indicators.momentum)}
      ${renderIndicatorCard('波动性', key_indicators.volatility)}
      ${renderIndicatorCard('关键均线', key_indicators.key_ma)}
      ${renderIndicatorCard('交易信号', key_indicators.signals)}
    </div>
  `;
}

// Render single indicator card
function renderIndicatorCard(title, indicators) {
  // Handle object format (from backend API)
  const indicatorsHtml = Object.entries(indicators)
    .filter(([key, value]) => key !== 'interpretation')
    .map(([key, value]) => {
      const label = formatIndicatorLabel(key);
      
      // Format numeric values to 4 decimal places
      let formattedValue = value;
      if (typeof value === 'number') {
        formattedValue = value.toFixed(4);
      }
      
      return `
        <div class="indicator-row">
          <span class="label">${label}</span>
          <span class="value">${formattedValue}</span>
        </div>
      `;
    }).join('');
  
  return `
    <div class="indicator-card">
      <div class="card-title">${title}</div>
      <div class="indicator-values">
        ${indicatorsHtml}
      </div>
      ${indicators.interpretation ? `
        <div class="card-interpretation">
          ${indicators.interpretation}
        </div>
      ` : ''}
    </div>
  `;
}

// Format indicator label (English to Chinese)
function formatIndicatorLabel(label) {
  const labelMap = {
    'MA_Alignment': '均线排列',
    'ADX': 'ADX趋势强度',
    'DI_Plus': '上升方向线',
    'DI_Minus': '下降方向线',
    'RSI14': 'RSI相对强弱',
    'Williams_R': '威廉指标',
    'MACD': 'MACD柱状图',
    'ATR14': '平均真实波幅',
    'BB_Position': '布林带位置',
    'Volatility_20d': '20日波动率',
    'SMA5': '5日均线',
    'SMA20': '20日均线',
    'SMA50': '50日均线',
    'SMA5_cross_SMA20': '5/20日均线交叉',
    'Price_vs_MA120': '价格相对120日均线',
    'Buy_Signals': '买入信号数量',
    'Sell_Signals': '卖出信号数量'
  };
  
  return labelMap[label] || label;
}

// Unified sidebar opening function
function openSidebar(trigger, data) {
  const sidebar = document.getElementById('analysisSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const title = document.getElementById('sidebarTitle');
  const tabs = document.getElementById('sidebarTabs');
  
  // Update state
  currentSidebarTrigger = trigger;
  currentSidebarData = data;
  
  if (trigger === 'card') {
    // Triggered by card click - show LLM analysis only
    title.textContent = '大模型分析详情';
    tabs.style.display = 'none';
    
    // Render LLM content
    renderSidebarContent(data.pair);
    
    // Ensure LLM tab is the only content visible
    document.getElementById('llmTab').classList.add('active');
    document.getElementById('indicatorsTab').classList.remove('active');
    currentActiveTab = 'llm';
    
  } else if (trigger === 'strategy') {
    // Triggered by strategy table click - show tabs
    title.textContent = '技术指标详情';
    tabs.style.display = 'flex';
    
    // Switch to indicators tab by default
    switchTab('indicators');
  }
  
  // Open sidebar
  sidebar.classList.add('sidebar-open');
  overlay.classList.add('sidebar-overlay-open');
}

// Modified openAnalysisSidebar to use unified function
function openAnalysisSidebar(pair) {
  // Store LLM data in a structure that can be accessed later
  const sidebarData = {
    type: 'llm',
    pair: pair
  };
  
  openSidebar('card', sidebarData);
}

// Tab switching function
function switchTab(tabName) {
  // Update tab buttons
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    if (btn.dataset.tab === tabName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  
  // Update tab content visibility
  const tabContents = document.querySelectorAll('.tab-content');
  tabContents.forEach(content => {
    content.classList.remove('active');
  });
  
  const targetTab = document.getElementById(`${tabName}Tab`);
  if (targetTab) {
    targetTab.classList.add('active');
  }
  
  // Update state
  currentActiveTab = tabName;
  
  // Render content based on tab
  if (tabName === 'llm') {
    // Render LLM content - work for both card and strategy triggers
    // For strategy trigger, we need to fetch the pair data first
    if (currentSidebarTrigger === 'strategy' && currentSidebarData) {
      // Fetch pair data for LLM analysis
      fetch(`/api/v1/pairs/${currentSidebarData.pair}`)
        .then(response => response.json())
        .then(pairData => {
          renderSidebarContent(pairData);
        })
        .catch(error => {
          console.error('Error fetching pair data:', error);
          document.getElementById('llmTab').innerHTML = `
            <p class="sidebar-text">加载大模型分析失败: ${error.message}</p>
          `;
        });
    } else if (currentSidebarTrigger === 'card' && currentSidebarData) {
      // Render LLM content from stored data
      renderSidebarContent(currentSidebarData.pair);
    }
  } else if (tabName === 'indicators' && currentSidebarTrigger === 'strategy' && currentSidebarData) {
    // Indicators already rendered
    // No action needed
  }
}

// Initialize tab click event listeners
function initializeTabListeners() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;
      if (tabName) {
        switchTab(tabName);
      }
    });
  });
}