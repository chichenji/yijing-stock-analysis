import yijing_stock_analysis.engine as engine_module

from yijing_stock_analysis import AnalysisInput, YijingStockEngine
from yijing_stock_analysis.report import render_markdown, render_json
from yijing_stock_analysis.report_html import render_html


def sample_input():
    return AnalysisInput(
        ticker="600519.SH",
        question="未来三天走势如何？",
        horizon="3d",
        cast_method="time",
        market={
            "trend": "up",
            "ma5": 100,
            "ma20": 98,
            "ma60": 95,
            "macd": 1.2,
            "macd_dif": 1.3,
            "macd_dea": 1.0,
            "rsi6": 61,
            "kdj_k": 62,
            "kdj_d": 58,
            "boll_position": "中轨上方",
            "volume_ratio": 1.3,
            "main_fund_inflow": 8,
            "northbound_inflow": 5,
            "sector_strength": 7,
            "turnover_rate": 3.5,
            "amount": 1500000000,
            "change_pct": 2.4,
        },
        news={
            "sentiment_index": 64,
            "sentiment_class": "积极",
            "flow_score": 72,
            "viral_k": 1.4,
        },
        macro={
            "macro_score": 58,
            "macro_bias": "中性",
            "index_trend": "up",
        },
    )


def test_engine_full_result():
    result = YijingStockEngine().analyze(sample_input())
    payload = result.as_dict()
    assert payload["ticker"] == "600519.SH"
    assert payload["partial"] is False
    assert payload["scores"]["final_score"] > 0
    assert payload["main_hexagram"]["name"]
    assert payload["recommendation"]["action"]
    assert set(payload["cast_trace"]["casts"]) == {"time"}


def test_report_renderers():
    payload = YijingStockEngine().analyze(sample_input()).as_dict()
    markdown = render_markdown(payload)
    html = render_html(payload)
    json_text = render_json(payload)
    assert "600519.SH" in markdown
    assert "总断" in markdown
    assert "传统六十四卦时序" in markdown
    assert "完整六十四卦全象合参" in markdown
    assert "本卦" in markdown
    assert "断语短句" in markdown
    assert "白话解释" in markdown
    assert "起卦来源细断" in markdown
    assert "时间卦" in markdown
    assert "代码卦" not in markdown
    assert "行情卦" not in markdown
    assert "六十四卦全象参考" in markdown
    assert "多空偏性统计" in markdown
    assert "阶段分布统计" in markdown
    assert "山天大畜" in markdown
    assert "技术面解读" in markdown
    assert "新闻面解读" in markdown
    assert "复盘窗口" in markdown
    assert "<details class=\"algorithm\">" in html
    assert "传统六十四卦时序" in html
    assert "完整六十四卦全象合参" in html
    assert "起卦来源细断" in html
    assert "时间卦" in html
    assert "代码卦" not in html
    assert "行情卦" not in html
    assert "六十四卦全象参考" in html
    assert "多空偏性统计" in html
    assert "阶段分布统计" in html
    assert "地泽临" in html
    assert "卦象算法与实际计算过程" in html
    assert '"ticker": "600519.SH"' in json_text


def test_market_cast_graceful_fallback(monkeypatch):
    monkeypatch.setattr(engine_module, "optional_market_snapshot", lambda ticker: {})
    monkeypatch.setattr(engine_module, "optional_news_snapshot", lambda ticker: {})
    monkeypatch.setattr(engine_module, "optional_macro_snapshot", lambda: {})
    result = YijingStockEngine().analyze(
        AnalysisInput(
            ticker="600519.SH",
            cast_method="market",
            market={},
        )
    ).as_dict()
    assert result["partial"] is True
    assert any(item.startswith("cast:market") for item in result["missing_fields"])
    assert result["recommendation"]["cast_issue"]


def test_engine_uses_optional_sources(monkeypatch):
    monkeypatch.setattr(
        engine_module,
        "optional_market_snapshot",
        lambda ticker: {
            "data_source": "tencent+akshare",
            "trend": "up",
            "ma5": 101,
            "ma20": 99,
            "ma60": 95,
            "macd": 1.2,
            "macd_dif": 1.3,
            "macd_dea": 1.0,
            "rsi6": 61,
            "kdj_k": 62,
            "kdj_d": 58,
            "boll_position": "中轨上方",
            "volume_ratio": 1.3,
            "amount": 1500000000,
            "turnover_rate": 3.5,
            "change_pct": 2.4,
        },
    )
    monkeypatch.setattr(
        engine_module,
        "optional_news_snapshot",
        lambda ticker: {
            "data_source": "akshare:stock_news_em",
            "sentiment_index": 64,
            "sentiment_class": "积极",
            "flow_score": 72,
            "viral_k": 1.4,
        },
    )
    monkeypatch.setattr(
        engine_module,
        "optional_macro_snapshot",
        lambda: {
            "data_source": "akshare:macro",
            "macro_score": 58,
            "macro_bias": "中性",
            "index_trend": "up",
        },
    )

    result = YijingStockEngine().analyze(
        AnalysisInput(
            ticker="600519.SH",
            cast_method="market",
            market={},
        )
    ).as_dict()

    assert result["partial"] is False
    assert result["source_trace"]["market"]["provider"] == "tencent+akshare"
    assert result["source_trace"]["news"]["provider"] == "akshare:stock_news_em"
    assert result["source_trace"]["macro"]["provider"] == "akshare:macro"
