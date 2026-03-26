// UI Components rendering functions

// Render overview cards
function renderOverviewCards(pairs) {
  const container = document.getElementById('overviewCards');
  container.innerHTML = '';
  
  pairs.forEach(pair => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-title">${pair.pair_name}</div>
      <div class="card-price">${pair.current_price.toFixed(4)}</div>
      <div class="card-prediction">
        <span class="prediction-icon">→</span>
        <span>等待数据...</span>
      </div>
      <div class="card-probability">Last: ${new Date(pair.last_update).toLocaleDateString()}</div>
    `;
    container.appendChild(card);
  });
}

// Render strategies table
function renderStrategiesTable(strategies) {
  const tbody = document.querySelector('#strategiesTable tbody');
  tbody.innerHTML = '';
  
  Object.entries(strategies).forEach(([pair, pairStrategies]) => {
    pairStrategies.forEach(strategy => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${pair}</td>
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