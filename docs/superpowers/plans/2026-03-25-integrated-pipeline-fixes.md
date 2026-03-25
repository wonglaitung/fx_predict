# 实施计划修复说明

## 日期
2026-03-25

## 审查发现的问题

### 1. 预测结果字段缺失 ❌
**问题**：`predict()` 方法返回的字典中缺少 `recommendation`, `stop_loss`, `take_profit` 字段

**影响**：报告生成会失败，测试无法通过

**修复方案**：在 `fx_trading_model.py` 的 `predict()` 方法中添加这些字段的生成逻辑

**修复代码**：
```python
# 在 predict 方法中添加（在计算 target_date 之后）

# 生成建议
if prediction == 1 and probability >= 0.60:
    recommendation = 'buy'
elif prediction == 0 and probability <= 0.40:
    recommendation = 'sell'
else:
    recommendation = 'hold'

# 计算止损止盈（使用 ATR 或固定比例）
if 'ATR14' in data.columns and not pd.isna(data['ATR14'].iloc[-1]):
    atr = data['ATR14'].iloc[-1]
    stop_loss = current_price - atr * 2
    take_profit = current_price + atr * 2
else:
    # 固定比例（1%）
    stop_loss = current_price * 0.99
    take_profit = current_price * 1.01

# 在 result 字典中添加
result = {
    'pair': pair,
    'current_price': float(current_price),
    'prediction': int(prediction),
    'probability': float(probability),
    'confidence': confidence,
    'recommendation': recommendation,  # 添加
    'stop_loss': float(stop_loss),     # 添加
    'take_profit': float(take_profit),  # 添加
    'horizon': predict_horizon,
    'data_date': data_date.strftime('%Y-%m-%d'),
    'target_date': target_date.strftime('%Y-%m-%d')
}
```

### 2. 向后兼容问题 ❌
**问题**：修改 `__init__` 方法添加 `horizon` 参数后，`comprehensive_analysis.py` 中调用会失败

**影响**：现有功能会被破坏

**修复方案**：
1. 确保 `horizon` 参数有默认值 `20`
2. 更新 `comprehensive_analysis.py` 中的 `ComprehensiveAnalyzer.__init__` 方法

**修复代码**：
```python
# comprehensive_analysis.py
class ComprehensiveAnalyzer:
    def __init__(self, horizon: int = 20):  # 添加 horizon 参数
        """
        初始化分析器
        
        Args:
            horizon: 预测周期（天），默认 20 天
        """
        self.logger = logger
        self.horizon = horizon
        self.technical_analyzer = TechnicalAnalyzer()
        self.model = FXTradingModel(horizon=horizon)  # 传递 horizon 参数
```

### 3. 依赖缺失 ❌
**问题**：`requirements.txt` 缺少 `tqdm` 和 `jinja2`

**影响**：脚本无法运行

**修复方案**：已修复，已添加到 requirements.txt

### 4. 测试代码不匹配 ❌
**问题**：测试代码使用了不存在的字段

**影响**：测试会失败

**修复方案**：更新测试中的模拟数据，确保包含所有字段

**修复代码**：
```python
# tests/test_run_pipeline.py
# 模拟预测结果时包含所有字段
predictions = {
    'EUR': {
        20: {
            'pair': 'EUR',
            'prediction': 1,
            'probability': 0.65,
            'confidence': 'high',
            'recommendation': 'buy',       # 添加
            'current_price': 1.0850,       # 修改（原为 entry_price）
            'stop_loss': 1.0750,
            'take_profit': 1.0950,
            'data_date': '2026-03-25',
            'target_date': '2026-04-14'
        }
    }
}
```

### 5. 命令行参数不一致 ⚠️
**问题**：文档中示例使用逗号分隔，但 argparse 使用空格分隔

**影响**：用户会困惑

**修复方案**：统一使用空格分隔（argparse 的默认行为）

**修改文档**：
```bash
# 正确的命令（使用空格分隔）
python3 run_pipeline.py --horizons 1 5 20

# 而不是
python3 run_pipeline.py --horizons 1,5,20  # 错误
```

## 执行优先级

**必须修复**（阻塞）：
1. ✅ 更新 `fx_trading_model.py` 的 `predict()` 方法
2. ✅ 更新 `comprehensive_analysis.py` 的 `__init__` 方法
3. ✅ 更新 `requirements.txt`（已完成）
4. ✅ 更新测试代码

**建议修复**（可选）：
5. 更新文档中的命令行示例
6. 添加更多测试用例

## 下一步

实施计划文档需要重新生成，包含所有修复。或者可以按照修复说明直接实施。

---

**审查状态**：已发现问题并制定修复方案  
**下一步**：用户确认是否需要重新生成完整的实施计划文档