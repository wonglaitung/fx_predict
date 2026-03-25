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

- 日期：2026-03-25
- 作者：iFlow CLI
- 版本：1.1 (MVP + 命令行支持)
- 更新内容：
  - 添加 Python 模块主函数入口的经验教训
  - 记录相对导入和命令行运行的问题及解决方案
  - 强调项目结构设计时应提前规划命令行接口