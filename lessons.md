# FX Predict 项目经验教训

## 开发经验

### 1. 数据泄漏防范

**问题**：在时间序列预测中，如果使用未来数据，会导致模型在实际应用中失效。

**解决方案**：
- 所有技术指标和特征计算必须使用 `.shift(1)` 使用滞后数据
- 在测试中验证至少 70% 的指标在第一行是 NaN
- 目标变量使用 `shift(-horizon)` 仅用于训练阶段，预测时不可用

**验证方法**：
```python
# 检查第一行是否为 NaN（验证数据泄漏防范）
assert indicators.iloc[0].isna().sum() / len(indicators.columns) >= 0.7
```

### 2. 硬性约束的重要性

**问题**：机器学习模型预测可能存在不确定性，需要添加硬性约束来控制风险。

**实现**：
- ML probability ≤ 0.50 时绝对禁止买入
- ML probability ≥ 0.60 且预测为 1 时推荐买入
- 在集成测试中验证硬性约束是否生效

**代码示例**：
```python
if ml_probability <= 0.50:
    recommendation = 'hold'
    reason = 'ML 概率过低，违反硬性约束'
```

### 3. 配置管理的模块化

**经验**：将所有配置集中管理，避免硬编码。

**最佳实践**：
- 使用 `config.py` 集中管理所有配置
- 使用环境变量（.env）存储敏感信息（API 密钥）
- 实现配置验证函数
- 使用类型提示提高代码可读性

### 4. 数据文件路径的三级配置

**问题**：数据文件过期时需要更新，硬编码在多个地方导致修改困难。

**解决方案**：实现三级配置优先级
1. 命令行参数（最高优先级）
2. 环境变量（中等优先级）
3. 配置文件默认值（最低优先级）

**实现方式**：
```python
# config.py 中添加默认值
DATA_CONFIG = {
    'data_file': 'FXRate_20260320.xlsx',
    # ...
}

# 命令行参数使用配置作为默认值
parser.add_argument('--data_file', type=str, default=DATA_CONFIG['data_file'])

# Shell 脚本从环境变量读取
DATA_FILE="${DATA_FILE:-FXRate_20260320.xlsx}"
```

**使用场景**：
- 临时使用新数据：命令行参数 `--data-file`
- 经常使用同一个数据：环境变量 `.env`
- 永久性更改：修改 `config.py`

**优势**：
- 更新数据时无需修改代码
- 灵活性高，适应不同使用场景
- 向后兼容，不影响现有代码

### 4. 测试驱动的开发（TDD）

**经验**：先写测试，再写实现代码。

**优势**：
- 确保代码质量
- 提前发现问题
- 便于重构
- 提供使用文档

**流程**：
1. 编写失败的测试
2. 实现最小代码使测试通过
3. 重构优化
4. 提交代码

### 5. 模型持久化

**经验**：训练好的模型需要保存和加载，避免重复训练。

**实现**：
- 使用 pickle 序列化模型
- 为每个货币对创建独立的模型文件
- 文件命名规范：`{pair}_{model_name}.pkl`
- 实现 BaseModelProcessor 统一管理

### 6. 错误处理和日志记录

**经验**：完善的错误处理和日志记录对于生产环境至关重要。

**最佳实践**：
- 所有 API 调用都有异常处理
- 使用 logging 模块记录日志
- 区分日志级别（INFO、WARNING、ERROR）
- 记录关键操作和错误信息

### 7. 集成测试的重要性

**经验**：单元测试只能测试单个模块，集成测试可以验证端到端工作流。

**集成测试覆盖**：
- 完整工作流：数据加载 → 技术指标 → 特征工程 → 模型训练 → 预测 → 综合分析
- 多货币对测试
- 硬性约束验证
- 数据泄漏防范验证
- 错误处理和边界情况

### 8. 技术指标的选择

**经验**：从经过验证的技术指标集合中选择，避免过度拟合。

**选择原则**：
- 基于金融理论
- 经过广泛验证（如 fortune 项目的指标）
- 覆盖不同类别（趋势、动量、波动、成交量）
- 避免使用过多相似指标

**结果**：选择 35 个指标，分为 6 类

### 9. 特征工程的平衡

**经验**：特征数量要适中，避免维度灾难和过拟合。

**策略**：
- 选择相关性强的特征
- 避免多重共线性
- 使用滞后特征防止数据泄漏
- 添加市场环境特征提高模型鲁棒性

**结果**：创建 16 个特征，分为 6 类

### 10. Python 模块的主函数入口

**问题**：使用了相对导入（`from ml_services.xxx import`）的 Python 模块需要添加 `if __name__ == "__main__":` 主函数入口才能直接运行。

**解决方案**：
1. 为需要命令行运行的模块添加主函数入口
2. 使用 `python3 -m module_name` 方式运行，而不是 `python3 module_name.py`
3. 在主函数中使用 `argparse` 解析命令行参数

**代码示例**：
```python
if __name__ == "__main__":
    import argparse
    from data_services.excel_loader import FXDataLoader

    parser = argparse.ArgumentParser(description="外汇交易模型")
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'predict'])
    parser.add_argument('--pair', type=str, required=True)
    args = parser.parse_args()

    # 处理逻辑...
```

**运行方式**：
```bash
# 错误方式（会因为相对导入失败）
python3 ml_services/fx_trading_model.py --mode train

# 正确方式
python3 -m ml_services.fx_trading_model --mode train --pair EUR
```

**教训**：在设计项目结构时，如果计划提供命令行接口，应该从一开始就规划好主函数入口和运行方式。

### 11. Git 工作流

**经验**：频繁提交和小步提交有助于代码管理。

**最佳实践**：
- 每个 Task 完成后立即提交
- 提交信息清晰规范（使用 Conventional Commits）
- 提交前运行测试确保通过
- 推送到远程仓库备份

## 代码质量问题

### 1. 测试覆盖率不均

**问题**：部分模块测试覆盖率低于目标（70%）。

**影响模块**：
- ml_services/feature_engineering.py: 62%
- llm_services/qwen_engine.py: 0%
- config.py: 29%

**解决方案**：
- 添加更多特征验证测试
- 实现大模型模块的 mock 测试
- 添加配置验证测试

### 2. 命名不一致

**问题**：指标名称与设计文档略有差异。

**示例**：
- 设计文档：`Williams_R`
- 实际实现：`WilliamsR_14`

**解决方案**：统一命名规范

### 3. 缺少文档注释

**问题**：部分方法缺少详细的文档字符串。

**解决方案**：为所有公共方法添加完整的 docstring

## 性能优化建议

### 1. 缓存机制

**建议**：缓存技术指标计算结果，避免重复计算。

**实现**：
```python
@lru_cache(maxsize=128)
def compute_sma(period):
    # ...
```

### 2. 并行计算

**建议**：使用多进程并行计算多个货币对的预测。

**实现**：
```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(analyze_pair, pairs)
```

### 3. 数据预处理优化

**建议**：使用更高效的数据处理库（如 Polars）。

## 部署考虑

### 1. 容器化

**建议**：使用 Docker 容器化应用。

**Dockerfile 示例**：
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 2. 环境变量管理

**建议**：使用环境变量管理配置。

**实现**：
- 使用 python-dotenv 加载 .env 文件
- 敏感信息不提交到 Git
- 提供环境变量模板（.env.example）

### 3. 日志管理

**建议**：使用日志轮转和集中管理。

**实现**：
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('fx_predict.log', maxBytes=10*1024*1024, backupCount=5)
```

## 用户反馈和改进

### 1. 命令行界面

**建议**：提供更友好的 CLI 接口。

**实现**：使用 argparse 或 click 库

### 2. 可视化

**建议**：添加图表可视化功能。

**实现**：使用 matplotlib 或 plotly

### 3. 实时更新

**建议**：支持实时数据更新和预测。

**实现**：集成实时数据源 API

## 总结

### 成功因素
1. 严格的数据泄漏防范
2. 完善的测试覆盖（85%）
3. 硬性约束控制风险
4. 模块化的代码结构
5. 详细的文档和注释

### 待改进
1. 提高部分模块测试覆盖率
2. 统一命名规范
3. 添加性能优化
4. 完善部署流程
5. 增强用户体验

### 关键教训
1. **数据质量**：数据泄漏防范是时间序列预测的关键
2. **测试驱动**：TDD 方法确保代码质量
3. **风险控制**：硬性约束比模型预测更重要
4. **模块化**：清晰的模块结构便于维护和扩展
5. **文档**：完善的文档是项目成功的基础

## 最后更新

- 日期：2026-03-27（第九次更新 - Dashboard 缓存问题和显示优化）
- 作者：iFlow CLI
- 版本：9.0 (Dashboard 缓存修复 + 显示优化)
- 更新内容：
  - **后端缓存陷阱**：
    - 问题：Dashboard 服务器缓存了旧数据，导致前端无法获取最新字段
    - 现象：后端代码已更新添加 `predictions` 字段，但前端收到的是旧数据
    - 排查过程：
      1. 检查后端代码：确认 server.js 第109-125行添加了 `predictions` 字段
      2. 检查前端代码：确认 components.js 正确读取 `predictions` 字段
      3. 测试 API：使用 curl 检查返回数据，发现 `predictions` 字段缺失
      4. 检查服务器日志：发现 "Cache hit for key: pairs"（缓存命中）
    - 解决方案：重启 Dashboard 服务器清除缓存
    - 验证方法：
      ```bash
      # 重启服务器
      pkill -f "node.*server.js"
      nohup node server.js > logs/server.log 2>&1 &
      
      # 验证 API 返回
      curl -s http://localhost:3000/api/v1/pairs | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"{p['pair']}: predictions={p.get('predictions', 'MISSING')}\") for p in data['pairs']]"
      ```
    - 教训：**后端数据结构更新后，必须重启服务器或清除缓存，前端才能获取到最新数据**
  
  - **前端数据完整性验证**：
    - 问题：前端直接使用 `pair.predictions['1d']`，没有验证字段是否存在
    - 影响：当 `predictions` 字段缺失时，会抛出错误 "Cannot read properties of undefined"
    - 解决方案：使用可选链和默认值
    - 代码示例：
      ```javascript
      // 修复前
      const pred1d = predictions['1d'] || {};
      
      // 修复后（更健壮）
      const pred1d = pair.predictions?.['1d'] || {};
      const icon1d = getIconInfo(pred1d.prediction || 'hold');
      ```
    - 教训：**前端应该使用防御性编程，验证数据结构完整性**
  
  - **信息展示的UX原则**：
    - 问题：卡片底部只显示1天的置信度，用户无法看到其他周期的信息
    - 原因：设计时假设用户主要关注1天预测，但实际需要多周期对比
    - 解决方案：在每个预测项中显示对应的概率和置信度
    - 显示逻辑：
      ```
      [图标] [预测文本]
      [概率% (置信度)]
      ```
    - 代码实现：
      ```javascript
      const formatPredictionInfo = (pred) => {
        const probabilityPercent = (pred.probability * 100).toFixed(1) + '%';
        const displayConfidence = confidenceMap[pred.confidence] || 'unknown';
        return `${probabilityPercent} (${displayConfidence})`;
      };
      ```
    - 教训：**关键信息应该在对应的位置显示，避免用户跨区域查找信息**
  
  - **浏览器缓存和硬刷新**：
    - 问题：代码更新后，浏览器仍显示旧版本的静态资源
    - 原因：浏览器缓存了 .js 和 .css 文件
    - 解决方案：硬刷新浏览器
    - 操作方法：
      - Windows/Linux: `Ctrl + Shift + R` 或 `Ctrl + F5`
      - Mac: `Cmd + Shift + R`
    - 教训：**前端静态资源更新后，用户需要硬刷新浏览器才能看到最新版本**
  
  - **CSS Flex 布局的等宽分布**：
    - 问题：三个预测项宽度不一致，导致显示不美观
    - 原因：默认 flex 布局根据内容宽度分配空间
    - 解决方案：为每个预测项添加 `flex: 1` 使其等宽分布
    - 代码示例：
      ```css
      .prediction-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        flex: 1;  /* 等宽分布 */
      }
      ```
    - 教训：**Flex 布局中需要明确指定 flex 属性，确保元素按预期分布**
  
  - **字体大小的层级关系**：
    - 问题：概率和置信度信息占用过多空间，导致卡片过长
    - 原因：使用了与标签相同的字体大小（0.875rem）
    - 解决方案：减小字体大小到 0.625rem，与标签字体大小一致
    - 代码示例：
      ```css
      .prediction-label {
        font-size: 0.625rem;
      }
      
      .prediction-icon {
        font-size: 1.5rem;
      }
      
      .prediction-info {
        font-size: 0.625rem;  /* 与标签大小一致 */
      }
      ```
    - 教训：**字体大小应该有明确的层级关系，信息密度和可读性需要平衡**
  
  - **中文化映射的维护**：
    - 代码中已有中文化映射：`confidenceMap = { 'high': '高', 'medium': '中', 'low': '低', 'unknown': '未知' }`
    - 新增显示复用了现有映射，无需额外修改
    - 教训：**中文化映射应该集中管理，避免分散在多个地方**
  
  - **后端数据结构的向后兼容**：
    - 问题：旧版本的前端代码可能不包含 `predictions` 字段
    - 解决方案：后端提供默认值，确保向后兼容
    - 代码示例：
      ```javascript
      predictions: {
        '1d': {
          prediction: predictions1d.prediction_text || 'hold',  // 默认值
          probability: predictions1d.probability || 0.5,         // 默认值
          confidence: predictions1d.confidence || 'unknown'      // 默认值
        },
        // ...
      }
      ```
    - 教训：**后端应该提供合理的默认值，确保向后兼容性**
  
  - **API 端点验证的重要性**：
    - 问题：前端显示异常，无法确定是前端还是后端问题
    - 解决方案：直接测试 API 端点，排除前端问题
    - 验证方法：
      ```bash
      # 测试所有货币对的 predictions 字段
      curl -s http://localhost:3000/api/v1/pairs | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"{p['pair']}: predictions={p.get('predictions', 'MISSING')}\") for p in data['pairs']]"
      ```
    - 输出示例：
      ```
      NZD: predictions={'1d': {'prediction': '下跌', ...}, '5d': {...}, '20d': {...}}
      JPY: predictions={'1d': {'prediction': '上涨', ...}, '5d': {...}, '20d': {...}}
      ...
      ```
    - 教训：**使用 API 测试工具（curl, Postman）可以快速定位问题，排除前端或后端问题**