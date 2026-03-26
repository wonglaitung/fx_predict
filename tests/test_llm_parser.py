import pytest
from ml_services.llm_parser import LLMAnalysisParser


def test_parser_initialization():
    """测试 Parser 初始化"""
    parser = LLMAnalysisParser()
    assert parser is not None


def test_parse_valid_json():
    """测试解析有效的 JSON"""
    parser = LLMAnalysisParser()

    valid_json = '''{
        "summary": "测试摘要",
        "overall_assessment": "中性",
        "key_factors": ["因素1", "因素2"],
        "horizon_analysis": {
            "1": {"recommendation": "buy", "confidence": "medium", "analysis": "理由1", "key_points": ["关键点1"]},
            "5": {"recommendation": "hold", "confidence": "low", "analysis": "理由2", "key_points": ["关键点2"]},
            "20": {"recommendation": "sell", "confidence": "medium", "analysis": "理由3", "key_points": ["关键点3"]}
        }
    }'''

    result = parser.parse(valid_json)

    # 验证必需字段
    assert 'summary' in result
    assert 'overall_assessment' in result
    assert 'key_factors' in result
    assert 'horizon_analysis' in result
    assert len(result['horizon_analysis']) == 3


def test_parse_invalid_json():
    """测试解析无效的 JSON"""
    parser = LLMAnalysisParser()

    invalid_json = '{ invalid json }'
    result = parser.parse(invalid_json)

    # 应该返回默认值
    assert 'summary' in result
    assert result['summary'] == '分析失败，使用默认建议'