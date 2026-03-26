// UI Components rendering functions

// Render overview cards
function renderOverviewCards(pairs) {
  const container = document.getElementById('overviewCards');
  container.innerHTML = '';
  
  pairs.forEach(pair => {
    const card = document.createElement('div');
    card.className = 'card card-clickable';
    
    // Determine prediction icon and class
    let icon = '→';
    let iconClass = 'prediction-neutral';
    
    const predictionMap = {
      'buy': '买入',
      'sell': '卖出',
      'hold': '持有',
      '上涨': '上涨',
      '下跌': '下跌'
    };
    
    const displayPrediction = predictionMap[pair.prediction] || pair.prediction;
    
    if (displayPrediction === '买入' || displayPrediction === '上涨') {
      icon = '↗';
      iconClass = 'prediction-up';
    } else if (displayPrediction === '卖出' || displayPrediction === '下跌') {
      icon = '↘';
      iconClass = 'prediction-down';
    }
    
    // Format probability as percentage
    const probabilityPercent = (pair.probability * 100).toFixed(1) + '%';
    
    // Translate confidence to Chinese
    const confidenceMap = {
      'high': '高',
      'medium': '中',
      'low': '低',
      'unknown': '未知'
    };
    const displayConfidence = confidenceMap[pair.confidence] || pair.confidence;
    
    // Get analysis summary (truncate if too long)
    const summary = pair.llm_analysis?.summary || '暂无分析';
    const truncatedSummary = summary.length > 50 ? summary.substring(0, 50) + '...' : summary;
    
    card.innerHTML = `
      <div class="card-title">${pair.pair_name}</div>
      <div class="card-price">${pair.current_price.toFixed(4)}</div>
      <div class="card-prediction">
        <span class="prediction-icon ${iconClass}">${icon}</span>
        <span>${displayPrediction}</span>
      </div>
      <div class="card-probability">${probabilityPercent} (${displayConfidence})</div>
      <div class="card-summary">${truncatedSummary}</div>
      <div class="card-hint">查看详情 →</div>
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
function renderRiskWarnings(risks) {
  const container = document.getElementById('riskWarnings');
  container.innerHTML = '';
  
  let hasWarnings = false;
  
  Object.entries(risks).forEach(([pair, risk]) => {
    if (risk.warnings && risk.warnings.length > 0) {
      hasWarnings = true;
      risk.warnings.forEach(warning => {
        const warningEl = document.createElement('div');
        warningEl.className = 'risk-warning';
        warningEl.innerHTML = `
          <span class="risk-icon">⚠️</span>
          <span>${pair}: ${warning}</span>
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

// Render sidebar content
function renderSidebarContent(pair) {
  const container = document.getElementById('sidebarContent');
  const analysis = pair.llm_analysis || {};
  
  container.innerHTML = `
    <div class="sidebar-section">
      <h3 class="sidebar-section-title">基本信息</h3>
      <div class="sidebar-info-grid">
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">货币对</span>
          <span class="sidebar-info-value">${pair.pair_name}</span>
        </div>
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">当前价格</span>
          <span class="sidebar-info-value">${pair.current_price.toFixed(4)}</span>
        </div>
        <div class="sidebar-info-item">
          <span class="sidebar-info-label">整体评估</span>
          <span class="sidebar-info-value">${analysis.overall_assessment || 'unknown'}</span>
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