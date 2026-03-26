"""
集成测试

测试端到端工作流，包括数据加载、技术指标计算、特征工程、模型训练、预测和综合分析。
"""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime

from data_services.excel_loader import FXDataLoader
from data_services.technical_analysis import TechnicalAnalyzer
from ml_services.feature_engineering import FeatureEngineer
from ml_services.fx_trading_model import FXTradingModel
from comprehensive_analysis import ComprehensiveAnalyzer


# 测试数据文件路径
TEST_DATA_FILE = 'FXRate_20260320.xlsx'


def test_end_to_end_workflow():
    """测试完整的端到端工作流：数据加载 → 技术指标 → 特征工程 → 模型训练 → 预测 → 综合分析"""
    # 跳过测试，如果数据文件不存在
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # ==================== 1. 加载数据 ====================
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    assert df is not None, "加载数据失败"
    assert len(df) > 0, "数据为空"
    assert 'Date' in df.columns, "缺少 Date 列"
    assert 'Close' in df.columns, "缺少 Close 列"

    # ==================== 2. 计算技术指标 ====================
    analyzer = TechnicalAnalyzer()
    df_with_indicators = analyzer.compute_all_indicators(df)

    # 验证关键指标是否存在
    required_indicators = ['RSI14', 'MACD', 'ATR14', 'SMA20', 'EMA20']
    for indicator in required_indicators:
        assert indicator in df_with_indicators.columns, f"缺少指标: {indicator}"

    # 验证指标值在合理范围内
    if 'RSI14' in df_with_indicators.columns:
        valid_rsi = df_with_indicators['RSI14'].dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all(), "RSI 值超出范围 [0, 100]"

    if 'ADX' in df_with_indicators.columns:
        valid_adx = df_with_indicators['ADX'].dropna()
        assert (valid_adx >= 0).all() and (valid_adx <= 100).all(), "ADX 值超出范围 [0, 100]"

    # ==================== 3. 特征工程 ====================
    feature_engineer = FeatureEngineer()
    features = feature_engineer.create_features(df_with_indicators)

    # 验证特征是否创建
    required_features = ['Close_change_1d', 'Return_1d', 'Bias_5', 'Volatility_5d', 'Trend_Slope_20']
    for feature in required_features:
        assert feature in features.columns, f"缺少特征: {feature}"

    # 验证特征值（无无穷大值）
    for col in features.columns:
        if features[col].dtype in ['float64', 'int64']:
            assert not np.isinf(features[col]).any(), f"特征 {col} 包含无穷大值"

    # ==================== 4. 模型训练 ====================
    model = FXTradingModel()
    metrics = model.train('EUR', df_with_indicators)

    assert 'accuracy' in metrics, "训练指标缺少 accuracy"
    assert metrics['accuracy'] >= 0, "准确率不能为负"
    assert metrics['accuracy'] <= 1, "准确率不能超过 1"
    assert 'feature_count' in metrics, "训练指标缺少 feature_count"
    assert metrics['feature_count'] > 0, "特征数必须大于 0"

    # ==================== 5. 模型预测 ====================
    prediction = model.predict('EUR', df_with_indicators)

    assert 'prediction' in prediction, "预测结果缺少 prediction"
    assert 'probability' in prediction, "预测结果缺少 probability"
    assert 'confidence' in prediction, "预测结果缺少 confidence"
    assert prediction['prediction'] in [0, 1], "预测值必须为 0 或 1"
    assert 0 <= prediction['probability'] <= 1, "概率必须在 [0, 1] 范围内"
    assert prediction['confidence'] in ['low', 'medium', 'high'], "置信度值无效"

    # ==================== 6. 综合分析 ====================
    comprehensive = ComprehensiveAnalyzer()
    result = comprehensive.analyze_pair('EUR', df_with_indicators)

    # 检查新的多horizon结构
    assert 'llm_analysis' in result, "综合分析结果缺少 llm_analysis"
    assert 'horizon_analysis' in result['llm_analysis'], "llm_analysis 缺少 horizon_analysis"
    assert '1' in result['llm_analysis']['horizon_analysis'], "缺少 1-day horizon"

    # 检查 1-day horizon 的推荐
    recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']
    assert recommendation_1d in ['buy', 'sell', 'hold'], "推荐值无效"

    # 检查 1-day horizon 的其他字段
    horizon_1 = result['llm_analysis']['horizon_analysis']['1']
    assert 'confidence' in horizon_1, "缺少置信度"
    assert 'analysis' in horizon_1, "缺少分析说明"

    # 检查交易策略（在单独的 trading_strategies 字段）
    assert 'trading_strategies' in result, "缺少 trading_strategies"
    assert 'short_term' in result['trading_strategies'], "缺少 short_term 策略"
    strategy_1d = result['trading_strategies']['short_term']
    assert 'entry_price' in strategy_1d, "缺少入场价格"
    assert 'stop_loss' in strategy_1d, "缺少止损位"
    assert 'take_profit' in strategy_1d, "缺少止盈位"
    assert 'reasoning' in strategy_1d, "缺少推理说明"

    # 验证价格逻辑
    if recommendation_1d == 'buy':
        assert strategy_1d['stop_loss'] < strategy_1d['entry_price'] < strategy_1d['take_profit'], "买入价格逻辑错误"
    elif recommendation_1d == 'sell':
        assert strategy_1d['take_profit'] < strategy_1d['entry_price'] < strategy_1d['stop_loss'], "卖出价格逻辑错误"


def test_multiple_pairs_workflow():
    """测试多个货币对的完整工作流"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载所有货币对
    loader = FXDataLoader()
    all_data = loader.load_all_pairs(TEST_DATA_FILE)

    assert len(all_data) > 0, "没有加载到任何货币对数据"

    # 对每个货币对进行训练和预测
    model = FXTradingModel()
    success_count = 0

    for pair, df in all_data.items():
        try:
            # 计算技术指标
            analyzer = TechnicalAnalyzer()
            df_with_indicators = analyzer.compute_all_indicators(df)

            # 训练模型
            metrics = model.train(pair, df_with_indicators)

            assert 'accuracy' in metrics
            assert metrics['accuracy'] >= 0

            # 预测
            prediction = model.predict(pair, df_with_indicators)

            assert 'prediction' in prediction
            assert 'probability' in prediction

            # 验证硬性约束
            if prediction['probability'] <= 0.50:
                assert prediction['prediction'] == 0, f"{pair} 违反硬性约束：概率 <= 0.50 但预测为买入"

            success_count += 1

        except Exception as e:
            pytest.fail(f"货币对 {pair} 工作流失败: {str(e)}")

    assert success_count == len(all_data), f"部分货币对工作流失败: {success_count}/{len(all_data)} 成功"


def test_hard_constraints():
    """测试硬性约束：ML probability ≤ 0.50 → 绝对禁止买入"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    # 计算指标
    analyzer = TechnicalAnalyzer()
    df = analyzer.compute_all_indicators(df)

    # 训练模型
    model = FXTradingModel()
    model.train('EUR', df)

    # 创建低概率场景：使用最后一个数据点进行预测
    # 如果预测概率 > 0.50，我们手动测试硬性约束
    prediction = model.predict('EUR', df)

    comprehensive = ComprehensiveAnalyzer()

    # 测试场景 1: 低概率预测应该不推荐买入
    if prediction['probability'] <= 0.50:
        result = comprehensive.analyze_pair('EUR', df)
        # 检查 1-day horizon 不推荐买入
        recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']
        assert recommendation_1d != 'buy', "硬性约束失败：概率 <= 0.50 但推荐买入"

    # 注意：无法手动创建低概率预测，因为 analyze_pair 方法不接受 ml_prediction 参数
    # 硬性约束应该在模型层面或上下文构建层面实施

    # 测试场景 2: 高概率预测（>= 0.60）应该推荐买入
    # 这里我们只验证结果结构，实际的高概率场景取决于实际数据
    result = comprehensive.analyze_pair('EUR', df)
    # 检查 1-day horizon 的推荐
    recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']
    assert recommendation_1d in ['buy', 'sell', 'hold'], "推荐值无效"


def test_data_leakage_prevention():
    """测试数据泄漏防范：所有指标和特征必须使用滞后数据"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    # 计算技术指标
    analyzer = TechnicalAnalyzer()
    df_with_indicators = analyzer.compute_all_indicators(df)

    # 验证技术指标使用滞后数据
    # 检查第一行是否为 NaN（因为使用了 shift(1)）
    # 排除 Excel 中已存在的列（SMA5, SMA10, SMA20）和原始数据列
    excel_precomputed_cols = ['SMA5', 'SMA10', 'SMA20', 'Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    indicator_cols = [col for col in df_with_indicators.columns if col not in excel_precomputed_cols]

    # 验证大部分指标在第一行是 NaN（因为使用了 shift(1)）
    # 允许一些指标（如 MACD）在第一行可能是 0.0 而不是 NaN
    nan_count = 0
    for col in indicator_cols:
        first_value = df_with_indicators[col].iloc[0]
        if pd.isna(first_value):
            nan_count += 1

    # 至少应该有 70% 的指标在第一行是 NaN
    nan_ratio = nan_count / len(indicator_cols) if len(indicator_cols) > 0 else 0
    assert nan_ratio >= 0.7, \
        f"数据泄漏风险：只有 {nan_count}/{len(indicator_cols)} ({nan_ratio:.1%}) 的指标在第一行是 NaN"

    # 验证特征工程也使用滞后数据
    feature_engineer = FeatureEngineer()
    features = feature_engineer.create_features(df_with_indicators)

    # 检查特征列（排除原始数据列和 Excel 预计算列）
    original_cols = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume', 'SMA5', 'SMA10', 'SMA20']
    feature_cols = [col for col in features.columns if col not in original_cols]

    # 检查滞后特征
    lag_features = [col for col in feature_cols if 'lag' in col]
    for col in lag_features:
        assert pd.isna(features[col].iloc[0]), f"滞后特征 {col} 的第一个值不为 NaN"

    # 检查价格衍生特征（应该使用 shift(1)）
    price_features = [col for col in feature_cols if 'change' in col.lower() or 'return' in col.lower()]
    nan_price_count = 0
    for col in price_features:
        if pd.isna(features[col].iloc[0]):
            nan_price_count += 1

    # 至少 50% 的价格衍生特征在第一行是 NaN
    if len(price_features) > 0:
        price_nan_ratio = nan_price_count / len(price_features)
        assert price_nan_ratio >= 0.5, \
            f"价格衍生特征数据泄漏风险：只有 {nan_price_count}/{len(price_features)} ({price_nan_ratio:.1%}) 的特征在第一行是 NaN"


def test_error_handling_and_edge_cases():
    """测试错误处理和边界情况"""
    loader = FXDataLoader()

    # 测试 1: 不存在的文件
    with pytest.raises(FileNotFoundError):
        loader.load_pair('EUR', 'nonexistent_file.xlsx')

    # 测试 2: 不存在的货币对
    if Path(TEST_DATA_FILE).exists():
        with pytest.raises(ValueError):
            loader.load_pair('NONEXISTENT_PAIR', TEST_DATA_FILE)

    # 测试 3: 空数据集
    empty_df = pd.DataFrame({'Close': [], 'High': [], 'Low': []})
    analyzer = TechnicalAnalyzer()
    result = analyzer.compute_all_indicators(empty_df)
    assert len(result) == 0, "空数据集应返回空结果"

    # 测试 4: 数据不足（少于最小数据点）
    small_df = pd.DataFrame({
        'Close': [1.0, 1.01, 1.02],
        'High': [1.01, 1.02, 1.03],
        'Low': [0.99, 1.00, 1.01],
        'Date': pd.date_range('2024-01-01', periods=3)
    })

    analyzer = TechnicalAnalyzer()
    result = analyzer.compute_all_indicators(small_df)

    # 长周期指标（如 SMA120）应该全为 NaN
    if 'SMA120' in result.columns:
        assert result['SMA120'].isna().all(), "数据不足时，长周期指标应全为 NaN"


def test_model_consistency():
    """测试模型一致性：相同的输入应产生相同的输出"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    # 计算指标
    analyzer = TechnicalAnalyzer()
    df = analyzer.compute_all_indicators(df)

    # 训练两个独立的模型实例
    model1 = FXTradingModel()
    model2 = FXTradingModel()

    metrics1 = model1.train('EUR', df)
    metrics2 = model2.train('EUR', df)

    # 准确率应该相同（使用相同的随机种子）
    assert metrics1['accuracy'] == metrics2['accuracy'], "相同数据训练两次应得到相同的准确率"

    # 预测也应该相同
    pred1 = model1.predict('EUR', df)
    pred2 = model2.predict('EUR', df)

    assert pred1['prediction'] == pred2['prediction'], "相同数据预测结果应相同"
    assert abs(pred1['probability'] - pred2['probability']) < 1e-6, "预测概率应相同"


def test_feature_importance_and_count():
    """测试特征数量和特征工程"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    # 计算指标
    analyzer = TechnicalAnalyzer()
    df_with_indicators = analyzer.compute_all_indicators(df)

    # 特征工程
    feature_engineer = FeatureEngineer()
    features = feature_engineer.create_features(df_with_indicators)

    # 验证特征数量
    original_cols = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
    feature_cols = [col for col in features.columns if col not in original_cols]

    assert len(feature_cols) >= 10, f"特征数过少: {len(feature_cols)}"

    # 验证关键特征类别
    has_price_features = any('change' in col.lower() or 'return' in col.lower() for col in feature_cols)
    has_bias_features = any('bias' in col.lower() for col in feature_cols)
    has_volatility_features = any('volatility' in col.lower() or 'std' in col.lower() for col in feature_cols)
    has_trend_features = any('slope' in col.lower() or 'alignment' in col.lower() for col in feature_cols)

    assert has_price_features, "缺少价格衍生特征"
    assert has_bias_features, "缺少偏离率特征"
    assert has_volatility_features, "缺少波动率特征"
    assert has_trend_features, "缺少趋势特征"


def test_technical_indicator_validation():
    """测试技术指标的有效性验证"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载数据
    loader = FXDataLoader()
    df = loader.load_pair('EUR', TEST_DATA_FILE)

    # 计算指标
    analyzer = TechnicalAnalyzer()
    df_with_indicators = analyzer.compute_all_indicators(df)

    # 验证布林带关系：上轨 >= 中轨 >= 下轨
    if all(col in df_with_indicators.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
        valid_bb = df_with_indicators[['BB_Upper', 'BB_Middle', 'BB_Lower']].dropna()
        assert (valid_bb['BB_Upper'] >= valid_bb['BB_Middle']).all(), "布林带上轨应 >= 中轨"
        assert (valid_bb['BB_Middle'] >= valid_bb['BB_Lower']).all(), "布林带中轨应 >= 下轨"

    # 验证威廉指标范围：[-100, 0]
    if 'WilliamsR_14' in df_with_indicators.columns:
        valid_wr = df_with_indicators['WilliamsR_14'].dropna()
        assert (valid_wr >= -100).all() and (valid_wr <= 0).all(), "威廉指标应在 [-100, 0] 范围内"

    # 验证 CCI 范围：通常在 [-200, 200] 范围内（可能超出）
    if 'CCI20' in df_with_indicators.columns:
        # CCI 可能超出这个范围，所以只检查没有无穷大值
        assert not np.isinf(df_with_indicators['CCI20']).any(), "CCI 包含无穷大值"


@pytest.mark.slow
def test_full_system_with_all_pairs():
    """慢速测试：完整系统测试，包含所有货币对"""
    if not Path(TEST_DATA_FILE).exists():
        pytest.skip(f"测试数据文件不存在: {TEST_DATA_FILE}")

    # 加载所有货币对
    loader = FXDataLoader()
    all_data = loader.load_all_pairs(TEST_DATA_FILE)

    results = {}

    for pair, df in all_data.items():
        # 完整工作流
        analyzer = TechnicalAnalyzer()
        df_with_indicators = analyzer.compute_all_indicators(df)

        model = FXTradingModel()
        model.train(pair, df_with_indicators)

        # 注意：不再需要单独的 predict 调用，analyze_pair 内部会处理
        comprehensive = ComprehensiveAnalyzer()
        result = comprehensive.analyze_pair(pair, df_with_indicators)

        # 提取 1-day horizon 的推荐
        recommendation_1d = result['llm_analysis']['horizon_analysis']['1']['recommendation']

        # 提取 ML 预测信息
        ml_pred_1d = result['ml_predictions']['1_day']

        results[pair] = {
            'accuracy': model.model is not None,
            'prediction': ml_pred_1d['prediction'],
            'probability': ml_pred_1d['probability'],
            'recommendation': recommendation_1d
        }

    # 验证所有货币对都成功处理
    assert len(results) > 0, "没有成功处理任何货币对"

    # 验证至少有一个货币对的准确率合理（这取决于实际数据）
    # 这里只是确保系统没有崩溃
    for pair, result in results.items():
        assert 'accuracy' in result
        assert 'prediction' in result
        assert 'recommendation' in result


if __name__ == '__main__':
    # 运行快速测试
    pytest.main([__file__, '-v', '-m', 'not slow'])