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

### 5. 测试驱动的开发（TDD）

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

### 6. 模型持久化

**经验**：训练好的模型需要保存和加载，避免重复训练。

**实现**：
- 使用 pickle 序列化模型
- 为每个货币对创建独立的模型文件
- 文件命名规范：`{pair}_{model_name}.pkl`
- 实现 BaseModelProcessor 统一管理

### 7. 错误处理和日志记录

**经验**：完善的错误处理和日志记录对于生产环境至关重要。

**最佳实践**：
- 所有 API 调用都有异常处理
- 使用 logging 模块记录日志
- 区分日志级别（INFO、WARNING、ERROR）
- 记录关键操作和错误信息

### 8. 集成测试的重要性

**经验**：单元测试只能测试单个模块，集成测试可以验证端到端工作流。

**集成测试覆盖**：
- 完整工作流：数据加载 → 技术指标 → 特征工程 → 模型训练 → 预测 → 综合分析
- 多货币对测试
- 硬性约束验证
- 数据泄漏防范验证
- 错误处理和边界情况

### 9. 技术指标的选择

**经验**：从经过验证的技术指标集合中选择，避免过度拟合。

**选择原则**：
- 基于金融理论
- 经过广泛验证（如 fortune 项目的指标）
- 覆盖不同类别（趋势、动量、波动、成交量）
- 避免使用过多相似指标

**结果**：选择 35 个指标，分为 6 类

### 10. 特征工程的平衡

**经验**：特征数量要适中，避免维度灾难和过拟合。

**策略**：
- 选择相关性强的特征
- 避免多重共线性
- 使用滞后特征防止数据泄漏
- 添加市场环境特征提高模型鲁棒性

**结果**：创建 18 个特征，分为 6 类

### 11. Python 模块的主函数入口

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

### 12. Git 工作流

**经验**：频繁提交和小步提交有助于代码管理。

**最佳实践**：
- 每个 Task 完成后立即提交
- 提交信息清晰规范（使用 Conventional Commits）
- 提交前运行测试确保通过
- 推送到远程仓库备份

### 13. 前端状态管理的重要性

**经验**：复杂的交互需要维护全局状态，记录触发源和当前数据。

**实现**：
- 使用全局变量记录当前状态（`currentSidebarTrigger`, `currentSidebarData`, `currentActiveTab`）
- 根据触发源执行不同的逻辑（卡片点击 vs 表格行点击）
- 标签页切换时获取对应数据

**代码示例**：
```javascript
let currentSidebarTrigger = null; // 'card' | 'strategy'
let currentSidebarData = null;
let currentActiveTab = null;      // 'llm' | 'indicators'

if (tabName === 'llm') {
  if (currentSidebarTrigger === 'strategy' && currentSidebarData) {
    // Fetch pair data for LLM analysis
    fetch(`/api/v1/pairs/${currentSidebarData.pair}`)
      .then(response => response.json())
      .then(pairData => {
        renderSidebarContent(pairData);
      });
  }
}
```

**教训**：复杂的交互功能需要清晰的状态管理，避免逻辑混乱。

### 14. 前端防御性编程

**经验**：前端应该验证数据完整性，使用可选链和默认值。

**实现**：
- 使用可选链操作符 `?.` 避免访问 undefined 的属性
- 提供默认值确保代码健壮性
- 验证必需字段是否存在

**代码示例**：
```javascript
// 修复前
const pred1d = predictions['1d'] || {};

// 修复后（更健壮）
const pred1d = pair.predictions?.['1d'] || {};
const icon1d = getIconInfo(pred1d.prediction || 'hold');

const currentPrice = pair.current_price !== undefined && pair.current_price !== null 
  ? pair.current_price.toFixed(4) 
  : 'N/A';
```

**教训**：防御性编程可以避免很多运行时错误，提高代码健壮性。

### 15. 数据结构设计的重要性

**经验**：不同的 API 端点可能需要不同的数据结构。

**问题**：
- `loadPair()` 返回标准化数据（仅包含前端展示所需的字段）
- `loadPairRaw()` 返回原始数据（包含完整的 metadata, technical_indicators 等）
- 某些功能需要详细的技术指标，某些功能只需要基本信息

**解决方案**：
- 根据使用场景设计合适的数据结构
- 标准化数据适合前端展示
- 原始数据适合需要详细信息的功能

**教训**：API 设计应该根据使用场景灵活调整，不要强制统一所有端点的返回格式。

### 16. HTML 结构对 CSS 布局的影响

**经验**：标签页应该放在标题容器外部，避免布局问题。

**问题**：
- 标签页放在 `sidebar-header` 内部时，样式不正确
- 标签页与标题和关闭按钮混在一起

**解决方案**：
```html
<!-- 修复前 -->
<div class="sidebar-header">
  <h2 class="sidebar-title">...</h2>
  <div class="sidebar-tabs">...</div>
  <button class="close-btn">&times;</button>
</div>

<!-- 修复后 -->
<div class="sidebar-header">
  <h2 class="sidebar-title">...</h2>
  <button class="close-btn">&times;</button>
</div>
<div class="sidebar-tabs">...</div>
```

**教训**：HTML 结构直接影响 CSS 布局，应该根据设计需求合理组织 DOM 结构。

### 17. 多轮修复的必要性

**经验**：复杂功能通常需要多轮迭代，逐步修复发现的问题。

**策略指标详情功能修复历程**：
1. 第一轮：实现基本功能（后端 API + 前端 HTML）
2. 第二轮：修复标签页样式（从按钮改为传统 TAB 页）
3. 第三轮：修复标签页位置（从 header 内部移出）
4. 第四轮：修复数据加载错误（renderIndicatorCard, renderSidebarContent）
5. 第五轮：修复交易策略表格为空（添加 trading_strategies 字段）
6. 第六轮：修复 API 数据缺失（添加 loadPairRaw 方法）
7. 第七轮：修复大模型分析不显示（传递正确的参数）

**教训**：复杂功能的实现不是一蹴而就的，需要多轮迭代和用户反馈。

### 18. 设计先行的重要性

**经验**：详细的设计文档和实现计划可以减少后期返工。

**策略指标详情功能设计流程**：
1. 创建设计文档：`docs/superpowers/specs/2026-03-27-strategy-indicators-detail-design.md`
2. 设计文档包含：API 设计、UI 结构、指标提取逻辑、触发源区分机制
3. 创建实现计划：`docs/superpowers/plans/2026-03-27-strategy-indicators-detail.md`
4. 实现计划包含：8个任务，涵盖后端 API、前端 HTML、CSS、JavaScript
5. 逐个完成任务，每完成一个任务验证功能

**教训**：设计先行可以明确需求，减少后期返工，提高开发效率。

### 19. 浏览器缓存和硬刷新

**经验**：前端静态资源更新后，用户需要硬刷新浏览器才能看到最新版本。

**硬刷新方法**：
- Windows/Linux: `Ctrl + Shift + R` 或 `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**或者手动清除缓存**：
1. 按 `F12` 打开开发者工具
2. 右键点击浏览器地址栏旁边的刷新按钮
3. 选择"清空缓存并硬性重新加载"

**教训**：浏览器缓存是前端开发的常见陷阱，需要提醒用户硬刷新。

### 20. 后端缓存陷阱

**经验**：后端数据结构更新后，必须重启服务器或清除缓存。

**问题**：
- 后端代码添加了 `predictions` 字段
- 服务器缓存了旧数据
- 前端收到的是旧数据，导致显示错误

**解决方案**：
```bash
# 重启服务器
pkill -f "node.*server.js"
nohup node server.js > logs/server.log 2>&1 &

# 验证 API 返回
curl -s http://localhost:3000/api/v1/pairs | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"{p['pair']}: predictions={p.get('predictions', 'MISSING')}\") for p in data['pairs']]"
```

**教训**：缓存机制可以提高性能，但也可能导致数据不一致，需要及时清除。

## 代码质量问题

### 1. 代码修改后必须进行语法检查

**问题**：在删除 `/api/v1/upload-config` 端点时，留下了孤立的代码块（重复的右大括号和残留的 catch 块），导致 Dashboard 服务器启动失败。

**错误信息**：
```javascript
/app/dashboard/server.js:649
      });
      ^
SyntaxError: Unexpected token '}'
```

**根本原因**：
- 删除代码时没有检查是否有残留的代码块
- 没有在修改后运行语法检查工具
- 直接尝试启动服务器，而不是先验证语法

**解决方案**：
1. 使用 Node.js 的语法检查工具：`node -c server.js`
2. 在每次修改后立即运行语法检查
3. 确保没有语法错误后再启动服务器
4. 使用 ESLint 等静态代码分析工具

**正确的修改流程**：
```bash
# 1. 修改代码
vim server.js

# 2. 检查语法
node -c server.js

# 3. 如果语法正确，启动服务器
npm start

# 4. 验证服务器运行正常
curl http://localhost:3000/health
```

**预防措施**：
- 在 git 提交前运行语法检查
- 在 CI/CD 流程中添加语法检查步骤
- 使用 pre-commit hook 自动检查语法
- 配置编辑器实时语法检查（VSCode, WebStorm 等）

**教训**：**代码修改后必须进行语法检查，特别是对于 JavaScript 这样的动态类型语言。语法错误会导致运行时失败，影响开发效率和用户体验。**

### 2. 测试覆盖率不均

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
2. 完善的测试覆盖（77%）
3. 硬性约束控制风险
4. 模块化的代码结构
5. 详细的文档和注释
6. 灵活的配置管理
7. 完整的 Docker 部署方案

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
6. **状态管理**：复杂的交互需要清晰的状态管理
7. **防御性编程**：前端应该验证数据完整性
8. **数据结构设计**：根据使用场景设计合适的数据结构
9. **多轮修复**：复杂功能需要多轮迭代和用户反馈
10. **设计先行**：详细的设计文档可以减少后期返工

## 最后更新

- 日期：2026-03-27（第十三次更新 - 数据质量修复和UI优化）
- 作者：iFlow CLI
- 版本：13.0 (数据去重 + API修复 + UI优化)
- 更新内容：
  - **数据去重的重要性**：
    - 问题：布林带、ADX等技术指标显示为0
    - 根本原因：数据文件包含重复的日期行（相同日期、相同价格）
    - 分析过程：
      1. 检查数据文件：发现最后10行日期相同（2026-03-20）
      2. 手动计算布林带：当最后20天价格相同时，标准差为0
      3. 确认问题：重复日期导致技术指标计算异常
    - 解决方案：在 `excel_loader.py` 中添加自动去重
    - 实现代码：
      ```python
      df = df.drop_duplicates(subset=['Date'], keep='first')
      ```
    - 处理流程：先排序 → 再去重 → 确保保留正确的那一行
    - 验证结果：数据从338行减少到283行，技术指标正常计算
    - 教训：**数据质量直接影响技术指标计算，必须在数据加载时清理重复数据**

  - **自动去重的必要性**：
    - 用户需求："系统自动去重"
    - 用户不应该手动编辑数据文件
    - 系统应该自动处理数据质量问题
    - 实现代码：
      ```python
      if before_count > after_count:
          self.logger.warning(f"发现并删除了 {before_count - after_count} 条重复日期数据")
          self.logger.info(f"去重后数据量: {after_count} 条记录")
      ```
    - 教训：**系统应该自动处理数据质量问题，减少用户手动操作**

  - **数据顺序的处理**：
    - 数据文件中的日期可能不按顺序排列
    - 系统必须自动按日期排序
    - 重要顺序：先排序 → 再去重
    - 实现代码：
      ```python
      df = df.sort_values('Date', ascending=True).reset_index(drop=True)
      df = df.drop_duplicates(subset=['Date'], keep='first')
      ```
    - 教训：**处理顺序很重要，先排序再去重可以确保保留正确的数据行**

  - **API 数据结构的完整性**：
    - 问题：`/api/v1/indicators/EUR` 返回空对象
    - 根本原因：`loadPair()` 方法缺少 `technical_indicators` 和 `risk_analysis` 字段
    - 分析过程：
      1. 检查前端代码：charts.js 正确实现
      2. 检查 API 返回：`{"pair": "EUR", "indicators": {}}`
      3. 检查 JSON 文件：确认包含 `technical_indicators` 字段
      4. 检查后端代码：`loadPair()` 方法缺少字段
    - 解决方案：在 `loadPair()` 返回对象中添加缺失字段
    - 实现代码：
      ```javascript
      return {
        // ... 其他字段
        technical_indicators: data.technical_indicators || {},
        risk_analysis: data.risk_analysis || {}
      };
      ```
    - 教训：**不同的 API 端点需要不同的数据结构，要根据使用场景设计返回格式**

  - **UI 可读性的重要性**：
    - 问题：页面上的日期显示不够显眼
    - 用户需求："页面上的日期要显眼一些"
    - 解决方案：增强日期显示的样式
    - 样式改进：
      1. 添加背景色和边框
      2. 增大字体（0.875rem → 0.95rem）
      3. 加粗字体（600）
      4. 改变颜色（灰色 → 白色）
    - 显示效果：浅蓝色标签，深色背景下非常显眼
    - 教训：**关键信息（如日期）应该显眼显示，提高用户体验**

  - **CSS 样式的层次感**：
    - 使用背景色、边框、字体粗细创建视觉层次
    - 标签式设计：背景色 + 边框 + 圆角
    - 颜色对比：浅蓝色背景 + 白色文字
    - 教训：**CSS 样式应该有层次感，使用多种样式元素创建视觉对比**

  - **用户反馈的价值**：
    - 用户问题1："为什么数据为零" → 发现数据质量问题
    - 用户问题2："系统自动去重" → 实现自动数据清理
    - 用户问题3："技术指标数值图为什么没有数据" → 发现 API 数据结构问题
    - 用户问题4："页面上的日期要显眼一些" → 优化 UI 可读性
    - 用户问题5："Auto-refresh: 5min 有生效吗" → 验证功能正常
    - 用户问题6："如果数据文件排序不一定对..." → 确认系统已自动处理
    - 教训：**用户的问题往往揭示了需要改进的地方，应该认真对待并积极解决**

  - **验证的重要性**：
    - 每个修复都需要验证，确保问题真正解决
    - 验证方法：
      1. 检查数据文件：确认数据量变化
      2. 检查 API 返回：确认数据结构正确
      3. 检查前端显示：确认 UI 效果符合预期
      4. 检查日志输出：确认操作成功执行
    - 教训：**验证是问题解决的关键步骤，不能假设修复成功**

  - **日志记录的重要性**：
    - 在去重操作中记录日志，告知用户发生了什么
    - 实现代码：
      ```python
      if before_count > after_count:
          self.logger.warning(f"发现并删除了 {before_count - after_count} 条重复日期数据")
          self.logger.info(f"去重后数据量: {after_count} 条记录")
      ```
    - 教训：**日志记录有助于用户了解系统行为，便于问题排查**

- 日期：2026-03-27（第十二次更新 - 策略指标详情功能实现）
- 作者：iFlow CLI
- 版本：12.0 (策略指标详情功能 + 多轮修复经验)
- 更新内容：
  - **前端状态管理的重要性**：
    - 复杂的交互需要维护全局状态
    - 记录触发源（card/strategy）和当前数据
    - 根据状态执行不同的逻辑
    - 标签页切换时获取对应数据
  
  - **前端防御性编程**：
    - 使用可选链操作符 `?.` 避免访问 undefined
    - 提供默认值确保代码健壮性
    - 验证必需字段是否存在
    - 示例：`pair.current_price?.toFixed(4) || 'N/A'`
  
  - **数据结构设计的重要性**：
    - 不同的 API 端点需要不同的数据结构
    - `loadPair()` 返回标准化数据（前端展示）
    - `loadPairRaw()` 返回原始数据（详细信息）
    - 根据使用场景灵活设计
  
  - **HTML 结构对 CSS 布局的影响**：
    - 标签页应该放在标题容器外部
    - 避免与标题和关闭按钮混在一起
    - DOM 结构直接影响 CSS 布局
  
  - **多轮修复的必要性**：
    - 复杂功能需要多轮迭代（策略指标详情功能：7轮修复）
    - 每轮修复解决特定问题
    - 用户反馈驱动优化
  
  - **设计先行的重要性**：
    - 详细的设计文档减少后期返工
    - 实现计划明确任务步骤
    - 逐个完成任务验证功能
  
  - **浏览器缓存和硬刷新**：
    - 前端更新后需要硬刷新
    - 提醒用户使用 Ctrl+Shift+R
    - 或者手动清除缓存
  
  - **后端缓存陷阱**：
    - 数据结构更新后必须重启服务器
    - 缓存机制可能导致数据不一致
    - 及时清除缓存确保最新数据

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
## 最后更新

- 日期：2026-03-27（第十四次更新 - Yahoo Finance 数据集成和布林带修复）
- 作者：iFlow CLI
- 版本：14.0 (Yahoo Finance 数据集成 + 布林带修复)
- 更新内容：
  - **数据分类的重要性**：
    - 技术指标应该按照类别正确分类
    - 布林带属于 volatility 类别，不是 trend 类别
    - 数据结构混乱会导致读取错误和数据丢失
    - 示例：从 `trend.BB_Upper` 读取应该是 `volatility.BB_Upper`
  
  - **API 数据结构验证**：
    - 使用 API 后应该验证返回的数据结构
    - 使用 `curl` 或其他工具检查 API 返回
    - 确认数据的组织方式和字段名称
    - 示例：`curl http://localhost:3000/api/v1/indicators/EUR | python3 -m json.tool`
  
  - **交易日数据的特性**：
    - 金融市场只在交易日开放（周一至周五）
    - 周末和节假日没有交易数据
    - Yahoo Finance 只返回交易日数据
    - 最后交易日：03/26/2026（周四）
    - 03/27/2026 是周六，市场休市，没有数据（这是正常的）
  
  - **外部数据源的优势**：
    - 自动数据更新减少手动工作
    - 数据量大（6年历史，1622 行）
    - 数据新鲜度更高
    - 免费使用，无需付费
    - 示例：yfinance 库访问 Yahoo Finance
  
  - **数据量的影响**：
    - 更多历史数据可以提高模型的泛化能力
    - 数据量从 283 行增加到 1622 行
    - 模型准确率普遍提升
    - JPY 5天准确率：85.71%（最高）
  
  - **模型准确率对比**：
    - 新数据训练的模型准确率普遍提升
    - 原因：数据量更大，时间跨度更长
    - 部分货币对表现优异（JPY, GBP, CAD）
    - 部分货币对需要进一步优化（AUD）
  
  - **自动化的价值**：
    - 数据获取脚本可以集成到定时任务
    - 实现完全自动化的数据更新
    - 减少人工干预
    - 提高系统可靠性
    - 示例：cron 定时任务每天凌晨运行数据更新
  
  - **错误的隐蔽性**：
    - 从错误的对象读取数据可能不会立即被发现
    - 只在特定功能使用时才会暴露
    - 需要全面测试才能发现
    - 示例：布林带数据读取错误只在显示详情时才被发现
  
  - **数据验证的重要性**：
    - 每次更新数据源后都应该验证数据完整性
    - 验证数据量、日期范围、字段完整性
    - 验证技术指标计算是否正确
    - 示例：检查 JSON 文件中的布林带数值
  
  - **Yahoo Finance 的可靠性**：
    - 免费且稳定的数据源
    - 适合作为主要数据源
    - yfinance 库易用
    - 支持多种时间周期（日线、周线、月线）

- 作者：iFlow CLI
- 版本：15.0 (run_full_pipeline.sh 增强 + Yahoo Finance 集成)
- 更新内容：
  - **Shell 脚本的灵活性**：
    - 通过添加参数扩展功能，而不是创建新脚本
    - 示例：添加 `--fetch-yahoo` 参数，而不是创建新脚本 `fetch_and_run.sh`
    - 保持脚本的功能集中和易于维护
    - 避免脚本数量爆炸
  
  - **默认值的重要性**：
    - 合理的默认值可以减少用户输入
    - START_DATE：2020-01-01（获取 6 年历史数据）
    - END_DATE：$(date +%Y-%m-%d)（自动使用今天）
    - YAHOO_PAIRS：所有货币对（EUR JPY AUD GBP CAD NZD）
    - 示例：用户只需运行 `./run_full_pipeline.sh --fetch-yahoo` 即可
  
  - **参数解析的健壮性**：
    - 需要正确处理可变数量的参数
    - `--yahoo-pairs` 可以接受 1 到多个货币对
    - 正确处理参数中的空格
    - 示例：`--yahoo-pairs EUR JPY GBP CAD`（4个货币对）
  
  - **工作流程的优化**：
    - 在合适的位置插入新步骤
    - 数据获取应该在训练之前（step 0）
    - 获取完成后自动更新 DATA_FILE 变量
    - 示例：先获取数据，再训练模型，确保使用最新数据
  
  - **向后兼容性**：
    - 新增功能不应破坏现有功能
    - 仍然支持使用已有的 Excel 数据文件
    - 仍然支持通过 Dashboard 上传数据文件
    - 示例：`./run_full_pipeline.sh --data-file FXRate_20260320.xlsx` 仍然有效
  
  - **帮助文档的重要性**：
    - 详细的文档可以提高易用性
    - 添加所有新参数的说明
    - 提供多个使用示例
    - 示例：用户可以通过 `-h` 或 `--help` 快速了解所有功能
  
  - **错误处理的必要性**：
    - 关键步骤失败时应立即退出
    - 提供清晰的错误信息
    - 不应继续执行后续步骤
    - 示例：数据获取失败，立即退出，不进行训练
  
  - **时间统计的价值**：
    - 帮助用户了解每个步骤的耗时
    - 数据获取：2-3 秒
    - 训练：10 秒
    - 预测：7 秒
    - 分析：9 秒
    - 总计：30 秒（完整流程）
  
  - **自动化流程的价值**：
    - 一键完成所有步骤大大提高了效率
    - 无需手动操作多个命令
    - 减少人为错误
    - 示例：`./run_full_pipeline.sh --fetch-yahoo` 完成所有工作
  
  - **参数设计的清晰性**：
    - 参数名称应该直观且易于理解
    - `--fetch-yahoo`：明确表示从 Yahoo Finance 获取数据
    - `--start-date` 和 `--end-date`：明确表示日期范围
    - 示例：用户看到参数名称就知道它的作用
  
  - **集成的重要性**：
    - 将数据获取集成到主流程中
    - 而不是让用户手动运行多个命令
    - 减少用户的学习成本
    - 示例：用户只需要学习一个命令，而不是多个命令

## 最后更新

- 日期：2026-03-30（第十六次更新 - Dashboard 文件上传功能）
- 作者：iFlow CLI
- 版本：16.0 (Dashboard 文件上传功能 + 用户体验优化)
- 更新内容：
  - **用户体验的重要性**：
    - 清晰的视觉反馈让用户了解系统状态
    - 进度条显示上传进度，减少用户等待焦虑
    - 成功/失败使用不同颜色，一目了然
    - 按钮状态变化（禁用/启用）引导用户操作
    - 示例：上传中显示蓝色加载状态，成功显示绿色，失败显示红色
  
  - **状态管理的必要性**：
    - 复杂的交互需要维护多个状态
    - 按钮状态：根据文件选择和上传进度变化
    - 上传状态：idle → uploading → success/error → idle
    - 进度状态：显示 0-100% 的上传进度
    - 错误状态：记录和显示各种错误信息
    - 示例：selectedFile 变量跟踪当前选择的文件
  
  - **文件验证的重要性**：
    - 前端验证可以减少无效请求
    - 文件格式验证：只接受 .xlsx 文件
    - 文件大小验证：不超过 10MB
    - 验证失败立即提示用户，不发送请求
    - 减少服务器负担和网络流量
    - 示例：`if (!file.name.endsWith('.xlsx')) { showUploadStatus('error', '只接受 .xlsx 格式的文件'); }`
  
  - **进度反馈的价值**：
    - 用户需要了解上传进度
    - 模拟进度动画让用户感知系统在工作
    - 进度百分比具体显示
    - 完成后自动隐藏进度条
    - 示例：`setInterval(() => { progress += 10; showUploadProgress(progress); }, 200);`
  
  - **自动化的优势**：
    - 上传成功后自动刷新 Dashboard
    - 用户无需手动刷新页面
    - 减少用户操作步骤
    - 提高系统易用性
    - 示例：`setTimeout(async () => { await refreshData(); }, 1000);`
  
  - **错误处理的完整性**：
    - 处理各种可能的错误情况
    - 文件格式错误
    - 文件大小超限
    - 上传失败（网络错误、服务器错误）
    - 未选择文件就点击上传
    - 清晰的错误信息帮助用户理解问题
    - 示例：`showUploadStatus('error', '文件大小不能超过 10MB');`
  
  - **CSS 样式的统一性**：
    - 新功能应该与现有风格保持一致
    - 使用相同的颜色变量（var(--color-info), var(--color-success), var(--color-danger)）
    - 使用相同的圆角、边框、字体大小
    - 保持整体视觉一致性
    - 示例：`.upload-btn { background-color: var(--color-info); }`
  
  - **响应式设计的重要性**：
    - 移动端体验同样重要
    - 小屏幕上按钮全宽，垂直排列
    - 媒体查询适配不同屏幕尺寸
    - 触摸友好的按钮大小
    - 示例：`@media (max-width: 768px) { .upload-container { flex-direction: column; } }`
  
  - **现有接口的复用**：
    - 使用已有的 API 接口减少开发工作
    - `/api/v1/upload` 接口已实现文件上传功能
    - 前端只需要调用接口，无需修改后端
    - 减少重复代码
    - 示例：`fetch('/api/v1/upload', { method: 'POST', body: formData });`
  
  - **代码组织的清晰性**：
    - HTML、CSS、JavaScript 分离
    - 功能模块化，易于维护
    - 事件监听器集中管理
    - 辅助函数封装复用逻辑
    - 示例：`showUploadStatus()`, `hideUploadStatus()`, `showUploadProgress()`
  
  - **按钮状态的设计**：
    - 按钮应该有明确的状态指示
    - 未选择文件：上传按钮禁用（灰色）
    - 已选择文件：上传按钮启用（蓝色）
    - 上传中：上传按钮禁用（灰色）
    - 上传后：重置为初始状态
    - 示例：`submitUploadBtn.disabled = !selectedFile;`
  
  - **隐藏原生文件输入框**：
    - 使用自定义按钮替代原生文件输入框
    - 原生文件输入框隐藏（display: none）
    - 通过 JavaScript 触发文件选择
    - 提供更好的视觉体验
    - 示例：`uploadBtn.addEventListener('click', () => { fileInput.click(); });`
  
  - **表单数据的使用**：
    - 使用 FormData 对象上传文件
    - FormData 可以处理二进制数据
    - 自动设置正确的 Content-Type
    - 简化文件上传代码
    - 示例：`const formData = new FormData(); formData.append('file', selectedFile);`
  
  - **异步操作的处理**：
    - 文件上传是异步操作
    - 使用 async/await 处理 Promise
    - 正确处理成功和错误情况
    - 避免阻塞主线程
    - 示例：`const response = await fetch('/api/v1/upload', { method: 'POST', body: formData });`
  
  - **定时器的管理**：
    - 进度动画使用 setInterval
    - 上传完成后清除定时器
    - 避免内存泄漏
    - 示例：`clearInterval(progressInterval);`
  
  - **延迟执行的使用**：
    - 使用 setTimeout 延迟执行某些操作
    - 进度条完成后延迟隐藏
    - 上传成功后延迟刷新数据
    - 给用户足够时间看到反馈
    - 示例：`setTimeout(() => { hideUploadProgress(); }, 2000);`
  
  - **DOM 元素的获取**：
    - 使用 document.getElementById 获取元素
    - 在页面加载完成后初始化
    - 避免访问不存在的元素
    - 示例：`const fileInput = document.getElementById('fileInput');`
  
  - **事件监听器的添加**：
    - 为交互元素添加事件监听器
    - 处理用户操作
    - 示例：`uploadBtn.addEventListener('click', () => { fileInput.click(); });`
  
  - **CSS 过渡效果的使用**：
    - 进度条填充使用过渡效果
    - 平滑的动画提升用户体验
    - 示例：`transition: width 0.3s ease;`
  
  - **CSS 变量的优势**：
    - 使用 CSS 变量管理颜色和样式
    - 便于统一修改主题
    - 提高代码可维护性
    - 示例：`background-color: var(--color-info);`
  
  - **Git 提交的规范**：
    - 使用 Conventional Commits 规范
    - 清晰的提交信息
    - feat: 新功能
    - fix: 修复
    - refactor: 重构
    - 示例：`feat: add file upload functionality to dashboard`

## 最后更新

- 日期：2026-03-30（第十七次更新 - Docker 配置文件可编辑功能）
- 作者：iFlow CLI
- 版本：17.0 (Docker 配置可编辑 + 接口简化)
- 更新内容：
  - **接口简化的原则**：
    - 避免功能重复，每个接口只做一件事
    - 如果一个功能可以通过现有流程实现，不需要单独的接口
    - 减少接口数量，降低维护成本
    - 简化用户操作，减少学习曲线
    - 示例：删除 `/api/v1/upload-config`，因为数据上传已经自动更新 config.py
  
  - **数据流程的优化**：
    - 用户上传数据文件 → 自动更新 config.py → 使用新配置
    - 无需用户手动配置，系统自动处理
    - 减少用户操作步骤，提高效率
    - 降低出错可能性
    - 示例：上传文件后自动更新 DATA_CONFIG['data_file']
  
  - **自动化的重要性**：
    - 自动化流程可以减少用户负担
    - 减少用户需要了解的细节
    - 提高系统易用性
    - 减少人为错误
    - 示例：上传文件后自动更新配置、清除缓存、刷新数据
  
  - **API 设计的简洁性**：
    - API 应该简洁明了，避免过度设计
    - 每个接口应该有明确的单一职责
    - 避免为相似功能创建多个接口
    - 减少不必要的抽象层
    - 示例：只有一个 `/api/v1/upload` 接口，同时处理数据文件和配置更新
  
  - **用户体验的优化**：
    - 用户只需要关心主要任务（上传数据）
    - 系统自动处理相关细节（更新配置、清除缓存）
    - 减少用户需要了解的接口数量
    - 简化用户操作流程
    - 示例：用户只需上传一个文件，系统自动完成所有后续操作
  
  - **代码维护的考虑**：
    - 删除冗余代码减少维护负担
    - 减少测试用例数量
    - 降低出错可能性
    - 提高代码可读性
    - 示例：删除 71 行代码和相关的文档说明
  
  - **文档同步的重要性**：
    - 删除功能时同步更新文档
    - 避免文档与代码不一致
    - 移除过时的使用说明
    - 保持文档的准确性
    - 示例：删除 DOCKER.md 中关于配置文件上传的说明
  
  - **配置管理的简化**：
    - 配置应该通过标准流程更新
    - 避免为配置更新提供特殊接口
    - 配置更新应该是业务流程的一部分
    - 示例：上传数据文件时自动更新配置，而不是单独的配置接口
  
  - **Volume 挂载的实际应用**：
    - config.py 仍然支持双向同步
    - 容器内部和宿主机都可以编辑
    - 提供灵活的配置管理方式
    - 适用于开发调试场景
    - 示例：可以在容器内直接修改配置测试效果
  
  - **功能迭代的方向**：
    - 从功能丰富转向功能精简
    - 删除冗余功能，保留核心功能
    - 提高系统的可维护性
    - 专注于用户体验
    - 示例：删除配置上传接口，简化用户操作流程
  
  - **Git 提交的规范**：
    - 使用 refactor 标签表示重构
    - 清晰说明删除的原因
    - 说明替代方案
    - 保持提交信息的简洁性
    - 示例：refactor: remove /api/v1/upload-config endpoint
  
  - **代码审查的重要性**：
    - 定期审查代码，发现冗余功能
    - 评估每个接口的必要性
    - 考虑是否有更简洁的实现方式
    - 持续优化代码质量
    - 示例：审查发现 upload-config 接口冗余
  
  - **接口职责的明确**：
    - 每个接口应该有明确的单一职责
    - 避免一个接口做太多事情
    - 通过流程设计实现功能组合
    - 示例：数据上传接口负责数据上传和配置更新，配置更新是上传流程的一部分
  
  - **用户反馈的价值**：
    - 用户的反馈揭示了接口设计的冗余
    - 用户只需要上传数据文件，不需要单独上传配置
    - 用户不需要了解配置更新的细节
    - 根据用户反馈简化系统设计
    - 示例：用户反馈只需要上传数据文件，自动更新配置
  
  - **系统设计的进化**：
    - 从多接口方案简化为单接口方案
    - 减少用户的认知负担
    - 提高系统的易用性
    - 持续优化用户体验
    - 示例：从两个上传接口简化为一个上传接口
  
  - **自动化测试的简化**：
    - 删除接口后减少测试用例
    - 降低测试覆盖率要求
    - 减少测试维护成本
    - 提高测试效率
    - 示例：删除 upload-config 接口后，减少相关测试用例
  
  - **API 文档的维护**：
    - 删除接口后及时更新 API 文档
    - 移除过时的接口说明
    - 保持文档的准确性
    - 避免用户困惑
    - 示例：从 DOCKER.md 中移除配置上传接口说明
  
  - **代码删除的艺术**：
    - 删除冗余代码比添加新代码更有价值
    - 减少代码库的复杂度
    - 提高代码的可读性和可维护性
    - 勇于删除不再需要的代码
    - 示例：删除 71 行冗余代码
  
  - **向后兼容性的考虑**：
    - 删除接口前确认没有用户在使用
    - 提供明确的替代方案
    - 在文档中说明变更
    - 逐步废弃，而非突然删除
    - 示例：upload-config 接口是新增的，删除没有向后兼容问题
  
  - **下一步工作**：
    - 继续审查其他可能的冗余功能
    - 优化现有接口的设计
    - 提高系统的简洁性
    - 持续改进用户体验

### 19. 配置管理统一的重要性

**问题**：`.env` 和 `config.py` 都有 `DATA_FILE` 配置，造成重复和混乱。

**根本原因**：
- 配置管理职责不清晰
- 可配置项和固定配置混在一起
- 缺少统一的配置管理规范

**解决方案**：
- 从 `config.py` 的 `DATA_CONFIG` 中删除 `data_file` 字段
- 统一通过 `.env` 文件管理数据文件路径
- 明确配置分层：
  - 环境变量：运行时可配置项（API 密钥、文件路径等）
  - 代码配置：固定系统配置（支持的货币对、参数默认值等）

**配置管理最佳实践**：
- **单一职责原则**：每个配置项只在一个地方定义
- **分层管理**：
  ```python
  # 环境变量（.env）- 运行时可配置
  DATA_FILE=data/raw/FXRate_20260330.xlsx
  QWEN_API_KEY=sk-xxxx
  
  # 代码配置（config.py）- 固定系统配置
  DATA_CONFIG = {
      'supported_pairs': [...],  # 固定的货币对列表
      'min_data_points': 100,     # 固定的最小数据点数
  }
  ```
- **配置优先级**：命令行参数 > 环境变量 > 代码默认值
- **环境变量命名规范**：使用大写和下划线（`DATA_FILE`）
- **代码配置命名规范**：使用小写和下划线（`min_data_points`）

**验证方法**：
```python
# 检查配置结构
print('DATA_CONFIG keys:', list(DATA_CONFIG.keys()))
# 应该只包含：['supported_pairs', 'pair_symbols', 'min_data_points', 'train_test_split']
```

**Dashboard 功能同步更新**：
- 问题：文件上传功能尝试更新 `config.py`（现已无效）
- 解决：更新文件上传功能，改为更新 `.env` 文件
- 代码修改：
  ```javascript
  // 修改前
  const dataFileRegex = /'data_file':\s*'[^']*'/;
  
  // 修改后
  const dataFileRegex = /^DATA_FILE=.*/m;
  ```

**功能修改的全面检查清单**：
1. 检查所有引用该配置的代码文件
2. 检查前端/后端相关功能
3. 检查文档和注释
4. 检查测试用例
5. 运行完整的测试套件
6. 更新相关文档

**经验教训**：
- 配置管理应该单一职责，避免重复配置
- 可配置项应该由环境变量管理
- 固定配置应该放在代码中
- 功能修改需要全面检查所有相关代码
- Dashboard 功能需要与后端配置变更同步更新
- 使用代码搜索工具（grep）查找所有引用

**配置管理的演进方向**：
- 从混合配置到分层配置
- 从多位置配置到单一配置源
- 从硬编码到环境变量
- 从手动配置到自动化管理

**未来改进**：
- 使用配置管理工具（如 pydantic, python-dotenv）
- 实现配置验证（类型检查、范围检查）
- 支持配置文件的热更新
- 提供配置查看和调试工具
- 记录配置变更历史

## 最后更新

- 日期：2026-03-31（第二十次更新 - Dashboard UI 优化和 Docker 镜像增强）
- 作者：iFlow CLI
- 版本：20.0 (UI 优化 + Docker 增强)
- 更新内容：
  - **数据日期显示的重要性**：
    - 用户需要知道数据是什么时候的
    - 数据日期与系统时间应该分开显示
    - 帮助用户理解数据的新鲜度和可信度
    - 示例：在卡片底部显示"数据: 2026-03-27"
  
  - **日期显示的区分**：
    - 页面顶部：今天的日期（最后刷新时间）
    - 卡片底部：数据文件的日期（数据生成时间）
    - 明确区分两个不同的时间概念
    - 避免用户混淆
    - 示例：
      - 今天 2026-03-31：系统今天运行
      - 数据 2026-03-27：Yahoo Finance 的最新交易日
  
  - **交易日数据的理解**：
    - 金融市场只在交易日开放
    - 周末和节假日没有数据
    - Yahoo Finance 只提供交易日数据
    - 这是正常的金融市场行为
    - 示例：2026-03-28/29/30/31 是周末/节假日，市场休市
  
  - **UI 可读性的提升**：
    - 清晰的日期显示帮助用户理解系统状态
    - 使用不同的视觉样式区分不同类型的信息
    - 数据日期使用小字体和浅色背景
    - 不占用过多空间，但足够显眼
    - 示例：`.card-date` 样式（0.75rem, `var(--color-info-bg)`）
  
  - **CSS 样式的复用**：
    - 使用 CSS 变量保持样式一致性
    - `var(--color-info-bg)` 与其他信息提示保持一致
    - `var(--text-secondary)` 与次要文本保持一致
    - 便于全局样式调整
    - 示例：`.card-date { background-color: var(--color-info-bg); }`
  
  - **Flex 布局的优势**：
    - 使用 flex 实现两端对齐的布局
    - `.card-footer` 使用 `justify-content: space-between`
    - 自动适应不同长度的内容
    - 响应式友好
    - 示例：
      ```css
      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      ```
  
  - **Docker 镜像的完整性**：
    - 将所有必要的脚本包含在镜像中
    - `fetch_fx_data.py` 应该在 Docker 镜像中
    - 支持在容器内使用所有功能
    - 提高镜像的独立性和完整性
    - 示例：`COPY fetch_fx_data.py ./`
  
  - **调试日志的价值**：
    - 日志记录有助于问题排查
    - 记录关键操作和数据来源
    - 帮助快速定位问题
    - 示例：`logInfo(`Loading ${pair} from file: ${latestFile}`)`
  
  - **数据获取的时间戳**：
    - 记录数据获取时间有助于追踪数据更新
    - 文件名包含日期：`FXRate_20260331_yahoo.xlsx`
    - 文件修改时间：2026-03-31 16:04
    - 数据最后日期：2026-03-27
    - 三个时间戳各有不同的含义
  
  - **用户反馈的响应**：
    - 根据用户需求优化 UI 显示
    - 用户可能需要了解数据的时效性
    - 在卡片上显示数据日期是最直观的方式
    - 提升用户体验和信任度

### 20. 技能系统的复用价值

**问题**：需要将 Markdown 文档转换为 Word 格式，是否需要从头实现？

**解决方案**：使用项目中已有的 md-to-word skill
- Skill 位置：`.iflow/skills/md-to-word/`
- 脚本路径：`scripts/md_to_word.py`
- 使用方式：`python3 .iflow/skills/md-to-word/scripts/md_to_word.py README.md`
- 输出文件：README.docx

**Skill 系统的优势**：
- 避免重复实现已有功能
- 提高开发效率
- 代码复用和维护性
- 统一的功能接口
- 完整的文档和示例

**Skill 的核心能力**：
- 完整格式保留（标题、段落、列表、代码块、引用、水平线、表格）
- 表格处理（表头自动加粗，应用表格网格样式）
- 批量操作（支持通配符批量转换多个文件）
- 递归处理（递归搜索并转换子目录中的所有 Markdown 文件）
- 灵活输出（保持原文件名或自定义输出路径）

**当前限制**：
- 不支持嵌套列表（列表内套列表）
- 表格对齐格式（左/中/右）会被统一处理为默认样式
- 行内格式（粗体、斜体、代码）会保留 Markdown 标记，不会转换为 Word 格式

**适用场景**：
- 格式转换：将 Markdown 文档转换为 Word 格式，供需要 .docx 文件的场景使用
- 批量处理：一次性转换多个 Markdown 文件
- 报告生成：为团队准备 Word 版本的技术报告或文档
- 内容归档：将项目文档从 Markdown 归档为 Word 格式
- 客户交付：向需要 Word 格式的客户或合作伙伴交付文档

**技术依赖**：
- python-docx >= 1.1.0
- 要求文件：`requirements.txt`

**经验教训**：
- **Skill 系统的价值**：在需要实现某个功能时，先检查项目中是否有相关的 Skill 可以复用
- **文档的重要性**：完整的 SKILL.md 文档可以帮助快速了解功能和使用方法
- **避免重复造轮子**：复用现有代码比重新实现更高效
- **功能的边界**：在使用 Skill 时要注意其限制和边界条件
- **测试的重要性**：使用 Skill 后要验证输出结果是否符合预期

### 21. 路径解析的正确性

**问题**：在子目录中运行代码时，如何确保相对路径解析正确？

**场景**：
- `server.js` 在 `dashboard/` 目录下
- `.env` 文件在项目根目录下
- 需要从 `server.js` 中更新 `.env` 文件

**解决方案**：
- 使用 `path.resolve('../.env')` 而不是 `path.resolve('.env')`
- `..` 表示上级目录
- `path.resolve()` 会将相对路径转换为绝对路径

**验证方法**：
```bash
# 从 dashboard/ 目录测试路径解析
cd dashboard
node -e "const path = require('path'); console.log(path.resolve('../.env'));"
# 输出: /data/fx_predict/.env
```

**路径解析规则**：
- `.` 表示当前目录
- `..` 表示上级目录
- `path.resolve()` 会解析为绝对路径
- 在不同的工作目录下运行代码，路径解析结果不同

**常见错误**：
```javascript
// 错误：假设当前工作目录是项目根目录
const envPath = path.resolve('.env'); // 实际路径：/data/fx_predict/dashboard/.env（错误）

// 正确：相对于当前文件位置解析路径
const envPath = path.resolve('../.env'); // 实际路径：/data/fx_predict/.env（正确）
```

**Docker 环境中的路径**：
- 容器内工作目录：`/app`
- `server.js` 位置：`/app/dashboard/server.js`
- `.env` 位置：`/app/.env`
- 相对路径 `../.env` 解析为 `/app/.env`（正确）

**经验教训**：
- **明确当前工作目录**：编写代码时要清楚代码在哪个目录下运行
- **使用相对路径**：相对于当前文件位置使用相对路径，而不是假设工作目录
- **测试路径解析**：在不同环境下测试路径解析是否正确
- **文档记录**：在代码注释中说明路径的含义
- **避免硬编码**：不要硬编码绝对路径，使用相对路径提高可移植性

### 22. 配置管理的一致性

**问题**：修改功能时要检查是否与项目的配置管理规范一致。

**场景**：
- 文件上传功能需要更新数据文件路径配置
- 项目统一使用 `.env` 环境变量管理 `DATA_FILE`
- `config.py` 的 `DATA_CONFIG` 中没有 `data_file` 字段

**解决方案**：
1. **检查配置管理规范**：
   - 阅读项目文档（README.md, AGENTS.md）
   - 检查 `config.py` 中的配置结构
   - 确认使用环境变量还是代码配置

2. **修改代码以符合规范**：
   ```javascript
   // 修改前（错误）：尝试更新 config.py
   const dataFileRegex = /'data_file':\s*'[^']*'/;
   
   // 修改后（正确）：更新 .env 文件
   const dataFileRegex = /^DATA_FILE=.*/m;
   ```

3. **验证修改正确性**：
   - 检查 `.env` 文件是否包含 `DATA_FILE` 配置
   - 测试文件上传功能是否正确更新配置
   - 确认其他功能是否正常读取配置

**配置管理的最佳实践**：
- **单一职责原则**：每个配置项只在一个地方定义
- **分层管理**：
  - 环境变量（.env）：运行时可配置项（API 密钥、文件路径等）
  - 代码配置（config.py）：固定系统配置（支持的货币对、参数默认值等）
- **配置优先级**：命令行参数 > 环境变量 > 代码默认值
- **环境变量命名规范**：使用大写和下划线（`DATA_FILE`）
- **代码配置命名规范**：使用小写和下划线（`min_data_points`）

**验证清单**：
- [ ] 检查 `.env` 文件中是否有目标配置项
- [ ] 检查 `config.py` 中是否有目标配置项
- [ ] 确认配置项应该放在哪里（环境变量 vs 代码配置）
- [ ] 修改代码以正确更新/读取配置
- [ ] 测试功能是否正常工作
- [ ] 更新相关文档

**经验教训**：
- **理解配置管理规范**：在修改功能前要理解项目的配置管理规范
- **避免重复配置**：不要在多个地方定义同一个配置项
- **明确配置类型**：区分可配置项（环境变量）和固定配置（代码配置）
- **全面检查引用**：修改配置时要检查所有引用该配置的代码
- **保持一致性**：确保所有功能使用相同的配置管理方式

### 23. Docker Volume 挂载方式的影响

**问题**：在 Docker 环境中，Volume 的挂载方式（只读 vs 读写）会影响文件操作。

**场景**：
- 文件上传功能需要更新 `.env` 文件
- 需要确认 `.env` 的挂载方式是否允许写入

**检查方法**：
```bash
# 查看 docker-deploy.sh 中的 volume 配置
-v "$PROJECT_DIR/.env:/app/.env"  # 没有 :ro，表示读写挂载
```

**Volume 挂载方式**：
- **读写挂载**（默认）：`/host/path:/container/path`
  - 容器内可以读取和修改文件
  - 修改会同步到宿主机
- **只读挂载**：`/host/path:/container/path:ro`
  - 容器内只能读取文件
  - 尝试写入会失败

**常见配置**：
```bash
# .env 文件通常挂载为只读（防止容器内意外修改）
-v "$PROJECT_DIR/.env:/app/.env:ro"

# config.py 通常挂载为读写（支持容器内修改）
-v "$PROJECT_DIR/config.py:/app/config.py"

# 数据目录通常挂载为读写
-v "$PROJECT_DIR/data:/app/data"
```

**影响**：
- **只读挂载**：
  - 容器内无法写入文件
  - 写入操作会抛出错误
  - 适用于不希望容器修改的文件（配置文件、代码文件）
- **读写挂载**：
  - 容器内可以读取和修改文件
  - 修改会同步到宿主机
  - 适用于需要在容器内修改的文件（数据文件、日志文件）

**验证挂载方式**：
```bash
# 进入容器
docker exec -it fx-predict-app bash

# 检查文件权限
ls -la /app/.env

# 尝试写入
echo "TEST=value" >> /app/.env
# 如果是只读挂载，会报错：Read-only file system
```

**经验教训**：
- **确认挂载方式**：在容器内操作文件前要确认挂载方式
- **设计考虑**：根据文件用途决定挂载方式（只读 vs 读写）
- **错误处理**：处理只读挂载的写入错误，给出清晰的错误信息
- **文档说明**：在文档中说明哪些文件是只读的，哪些是可写的
- **灵活性**：考虑设计支持两种挂载方式的方案（如果需要）

### 24. 文件系统操作的全面验证

**问题**：涉及文件系统的修改需要全面的验证。

**场景**：
- 文件上传功能需要更新 `.env` 文件
- 需要验证文件存在性、可读写性、路径正确性

**验证清单**：

1. **文件存在性**：
   ```bash
   # 检查文件是否存在
   ls -la .env
   
   # 检查文件是否在预期位置
   node -e "const path = require('path'); console.log(path.resolve('../.env'));"
   ```

2. **文件内容**：
   ```bash
   # 检查文件内容
   cat .env
   
   # 验证配置项是否存在
   grep "DATA_FILE" .env
   ```

3. **文件权限**：
   ```bash
   # 检查文件权限
   ls -la .env
   # 输出：-rw-r--r-- 1 user group 272 Mar 30 18:16 .env
   # 第一个字符：- 表示文件，d 表示目录
   # 后三个字符：rwx 表示所有者权限（读、写、执行）
   ```

4. **可读写性**：
   ```bash
   # 测试读取
   cat .env
   
   # 测试写入（备份文件）
   cp .env .env.backup
   echo "TEST=value" >> .env
   cat .env | grep "TEST"
   # 恢复
   cp .env.backup .env
   rm .env.backup
   ```

5. **路径解析**：
   ```bash
   # 测试相对路径解析
   cd dashboard
   node -e "const path = require('path'); console.log(path.resolve('../.env'));"
   # 应该输出：/data/fx_predict/.env
   ```

6. **Docker 环境**：
   ```bash
   # 进入容器
   docker exec -it fx-predict-app bash
   
   # 检查文件
   ls -la /app/.env
   
   # 测试读写
   cat /app/.env
   echo "TEST=value" >> /app/.env
   cat /app/.env | grep "TEST"
   ```

**错误处理**：
```javascript
try {
  const envContent = fs.readFileSync(envPath, 'utf8');
  // 修改内容
  fs.writeFileSync(envPath, envContent, 'utf8');
  logInfo(`.env updated: DATA_FILE = ${newFilePath}`);
} catch (error) {
  logError(`Failed to update .env: ${error.message}`);
  // 继续执行，即使更新失败
}
```

**经验教训**：
- **全面验证**：文件系统操作需要从多个角度验证（存在性、权限、路径、内容）
- **错误处理**：捕获并处理文件操作错误，提供清晰的错误信息
- **测试环境**：在本地和 Docker 环境中都测试文件操作
- **文档记录**：在代码中注释说明文件操作的预期行为和可能的错误
- **日志记录**：记录文件操作的关键步骤和结果，便于问题排查

## 最后更新

- 日期：2026-04-01（第二十一次更新 - Markdown 转 Word 和配置修复）
- 作者：iFlow CLI
- 版本：21.0 (Skill 复用 + 路径解析 + 配置管理 + Docker 挂载)
- 更新内容：
  - **Skill 系统的价值**：
    - 项目中的 Skill 可以快速完成任务，避免重复开发
    - md-to-word skill 提供完整的 Markdown 到 Word 转换功能
    - 使用现有 Skill 比重新实现更高效
    - 完整的文档和示例帮助快速上手
    - 经验：在需要实现功能时，先检查是否有相关 Skill 可以复用
  
  - **路径解析的正确性**：
    - 在子目录中运行代码时，要特别注意相对路径的解析
    - 使用 `path.resolve('../.env')` 而不是 `path.resolve('.env')`
    - `..` 表示上级目录，`.` 表示当前目录
    - 要明确当前工作目录，避免假设
    - 经验：相对于当前文件位置使用相对路径，而不是假设工作目录
  
  - **配置管理的一致性**：
    - 修改功能时要检查是否与项目的配置管理规范一致
    - 项目统一使用 `.env` 环境变量管理 `DATA_FILE`
    - `config.py` 的 `DATA_CONFIG` 中没有 `data_file` 字段
    - 不要在多个地方定义同一个配置项
    - 经验：理解配置管理规范，避免重复配置
  
  - **Docker Volume 挂载方式**：
    - Volume 挂载方式（只读 vs 读写）会影响文件操作
    - 只读挂载（`:ro`）：容器内只能读取
    - 读写挂载（默认）：容器内可以读取和修改
    - 检查挂载方式：`docker-deploy.sh` 中的 `-v` 配置
    - 经验：在容器内操作文件前要确认挂载方式
  
  - **文件系统操作的全面验证**：
    - 涉及文件系统的修改需要全面的验证
    - 验证清单：存在性、可读写性、路径正确性、文件内容
    - 测试环境：本地和 Docker 环境都测试
    - 错误处理：捕获并处理文件操作错误
    - 经验：从多个角度验证文件系统操作
    - 示例：用户反馈"我想知道数据是什么时候的"
  
  - **代码组织的原则**：
    - HTML、CSS、JavaScript 分离
    - 样式使用 CSS 类管理
    - 逻辑使用 JavaScript 函数封装
    - 便于维护和修改
    - 示例：`.card-date` 样式独立管理
  
  - **信息层次的清晰性**：
    - 主要信息（价格、预测）：大字体、显眼
    - 次要信息（数据日期）：小字体、浅色
    - 操作提示（查看详情）：右对齐
    - 建立清晰的信息层次
    - 示例：卡片布局从上到下：价格 → 预测 → 摘要 → 日期/提示
  
  - **日期格式的统一性**：
    - 使用 ISO 格式：YYYY-MM-DD
    - 页面顶部：`new Date().toISOString().split('T')[0]`
    - 卡片底部：从 JSON 文件读取的日期字符串
    - 保持日期格式的一致性
    - 示例：2026-03-31
  
  - **数据验证的重要性**：
    - 显示数据日期后，用户可以验证数据是否最新
    - 如果数据日期过旧，用户知道需要更新
    - 提高系统的透明度
    - 示例：用户看到数据是 2026-03-27，知道需要等到下周一才有新数据
  
  - **Docker 构建的优化**：
    - 利用 Docker 层缓存加速构建
    - 将不常变化的文件放在前面
    - 将经常变化的文件放在后面
    - 示例：`COPY fetch_fx_data.py ./` 在 COPY Python 代码之前
  
  - **代码注释的价值**：
    - 在关键代码处添加注释
    - 解释为什么这样做，而不是做了什么
    - 帮助其他开发者理解代码意图
    - 示例：`// Update last update time to today's date`
  
  - **用户体验的细节**：
    - 小的改进可以显著提升用户体验
    - 添加数据日期显示是一个小的改进
    - 但可以让用户更清楚地了解系统状态
    - 细节决定成败
    - 示例：在卡片底部添加数据日期显示
  
  - **时间管理的准确性**：
    - 使用 `new Date()` 获取当前时间
    - 使用 `toISOString()` 格式化时间
    - 使用 `split('T')[0]` 提取日期部分
    - 确保时间格式的准确性
    - 示例：
      ```javascript
      const today = new Date();
      const todayStr = today.toISOString().split('T')[0];
      ```
  
  - **数据新鲜度的概念**：
    - 数据新鲜度是指数据与当前时间的接近程度
    - 外汇数据每天更新（交易日）
    - 用户希望数据尽可能新鲜
    - 显示数据日期帮助用户评估新鲜度
    - 示例：数据日期是 2026-03-27，今天是 2026-03-31，数据是 4 天前的
  
  - **Git 提交的粒度**：
    - 每个功能完成后立即提交
    - UI 优化作为一个独立的提交
    - Docker 增强作为一个独立的提交
    - 保持提交的清晰性和可追溯性
    - 示例：feat: add data date display to currency pair cards
  
  - **文档更新的及时性**：
    - 功能完成后立即更新文档
    - 记录经验教训
    - 保持文档与代码的一致性
    - 示例：在 lessons.md 中添加新的经验教训
  
  - **持续改进的态度**：
    - 不断优化用户体验
    - 根据用户反馈调整设计
    - 小步快跑，持续迭代
    - 不满足于现状
    - 示例：从第19次更新到第20次更新，不断优化

## 最后更新

- 日期：2026-04-11（第二十一次更新 - Docker cron 环境变量修复）
- 作者：iFlow CLI
- 版本：21.0 (Docker cron 环境变量修复 + md-to-word 技能 + Git 仓库优化)
- 更新内容：
  - **cron 环境的特殊性**：
    - 问题：Docker 容器中的 cron 任务无法找到 Python 模块
    - 现象：
      - cron 任务执行失败，日志显示 "ModuleNotFoundError"
      - Python 无法找到 `/usr/local/lib/python3.12/site-packages` 中的包
      - 手动运行脚本正常，但 cron 任务失败
    - 根本原因：
      - cron 默认 PATH 很有限（只有 `/usr/bin:/bin`）
      - cron 环境中缺少用户环境变量（PATH、PYTHONPATH、LANG）
      - Python 模块路径需要通过 PYTHONPATH 显式指定
    - 排查过程：
      1. 检查 cron 日志：发现 "ModuleNotFoundError: No module named 'catboost'"
      2. 检查 Python 环境：手动运行 `python3 -m ml_services.fx_trading_model` 正常
      3. 检查 cron 环境：在 crontab 中添加 `env > /tmp/cron_env.log`，发现 PATH 很有限
      4. 分析差异：用户环境中 PATH 包含 `/usr/local/bin`，但 cron 环境中没有
    - 解决方案：在 crontab 文件中显式设置环境变量
      ```bash
      cat > /tmp/crontab << 'EOF'
      # 设置环境变量（cron 默认 PATH 很有限，需要手动设置）
      PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin
      PYTHONPATH=/usr/local/lib/python3.12/site-packages
      LANG=C.UTF-8

      # 定时任务
      0 * * * * cd /app && bash run_full_pipeline.sh >> /app/logs/pipeline.log 2>&1
      EOF
      crontab /tmp/crontab
      ```
    - 验证方法：
      - 在 crontab 中添加调试任务：`* * * * * env > /tmp/cron_env.log`
      - 检查 `/tmp/cron_env.log` 文件，确认环境变量正确
      - 检查 `/app/logs/pipeline.log` 文件，确认任务执行成功
    - 教训：**cron 环境与用户环境不同，需要显式设置环境变量，特别是 PATH 和 PYTHONPATH**

  - **技能系统的设计原则**：
    - 独立性：技能应该独立且可复用，不依赖其他技能
    - 跨平台：支持多种操作系统（Windows/Linux/macOS）
    - 文档完整：提供清晰的使用文档和示例
    - 标准接口：使用标准的命令行参数和输出格式
    - 错误处理：完善的错误处理和日志记录
    - 示例：md-to-word 技能
      - 文档：SKILL.md（274 行）
      - 脚本：md_to_word.bat（Windows）、md_to_word.sh（Linux/macOS）
      - Python：scripts/md_to_word.py（核心转换逻辑）
      - 依赖：requirements.txt（python-docx, markdown）

  - **Git 仓库管理 - 二进制文件处理**：
    - 问题：模型文件（.pkl）是大型二进制文件，提交到 Git 导致仓库体积膨胀
    - 影响：
      - 仓库体积：21 个 .pkl 文件，总大小约 1MB
      - 克隆速度：克隆仓库需要下载所有历史记录
      - Git 历史：二进制文件的 diff 无意义
      - 协作效率：拉取和推送速度变慢
    - 解决方案：
      1. 将模型文件添加到 .gitignore：
         ```
         # Model files (binary files, generated by training)
         data/models/*.pkl
         ```
      2. 从 Git 历史中移除已提交的模型文件：
         ```bash
         git rm --cached data/models/*.pkl
         git commit -m "chore: remove model files from git tracking"
         ```
      3. 保留本地文件，不影响训练和预测：
         - 模型文件在训练时自动生成
         - 首次运行需要训练模型
         - 可以通过 `run_full_pipeline.sh` 训练所有模型
    - 最佳实践：
      - 生成的文件不应该提交到 Git
      - 使用 .gitignore 排除临时文件、缓存文件、日志文件
      - 大型二进制文件使用 Git LFS（如果必须版本控制）
      - 在 README 中说明首次运行需要训练模型
    - 教训：**Git 仓库应该只包含源代码和配置文件，生成的文件应该在运行时创建**

  - **Docker 镜像的独立性**：
    - 问题：Docker 镜像应该能够独立运行，不依赖宿主机的环境
    - 关键要素：
      1. 所有依赖正确安装（Python 包、Node.js 模块）
      2. 环境变量正确设置（PATH、PYTHONPATH、LANG）
      3. 配置文件正确挂载（.env 文件）
      4. 数据目录正确挂载（data/、logs/）
      5. 定时任务能够独立运行（cron 任务）
    - 验证方法：
      - 构建镜像后，不使用 Volume 挂载启动容器
      - 检查所有服务是否正常运行
      - 检查 cron 任务是否能够执行
      - 检查日志输出是否正确
    - 教训：**Docker 镜像应该包含所有必要的组件，能够独立运行，减少对宿主机的依赖**

  - **技能扩展的价值**：
    - 技能系统提供可复用的功能模块
    - 用户可以快速使用现有技能
    - 开发者可以贡献新技能
    - 提高系统的可扩展性
    - 示例：md-to-word 技能可以用于生成项目文档的 Word 版本
    - 使用场景：
      - 将 AGENTS.md 转换为 Word 文档，分享给团队成员
      - 将 progress.txt 转换为 Word 文档，用于项目汇报
      - 将 lessons.md 转换为 Word 文档，用于知识分享

  - **多平台兼容性的重要性**：
    - 用户可能使用不同的操作系统
    - 技能应该支持主流操作系统（Windows、Linux、macOS）
    - 提供不同平台的脚本（.bat、.sh）
    - 在文档中明确说明操作系统要求
    - 示例：md-to-word 技能提供两个脚本
      - Windows 用户：使用 md_to_word.bat
      - Linux/macOS 用户：使用 md_to_word.sh
      - 文档中包含操作系统检测方法
