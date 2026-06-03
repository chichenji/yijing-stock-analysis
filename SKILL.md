# 易经多卦象股票分析 Skill

> 目标：用梅花易数、六十四卦、八卦象意、五行生克、互卦、错卦、综卦和简化六爻，对股票走势、风险、节奏和市场情绪做辅助研判，并用行情、新闻流量和宏观数据校验。

## 用法

- CLI: `python scripts/run_yijing_stock.py 600519.SH --question "未来三天走势"`
- JSON: `python scripts/run_yijing_stock.py 600519.SH --output json`
- HTML: `python scripts/run_yijing_stock.py 600519.SH --output html`
- 只用易经: `python scripts/run_yijing_stock.py 600519.SH --pure-yijing`
- 记录预测: `yijing-stock 600519.SH --output json --record records/predictions.jsonl`
- 批量分析: `yijing-stock batch examples/tickers.txt --pure-yijing --output html`
- 个股画像: `yijing-stock profile 600519.SH --records records/predictions.jsonl`
- 复盘: `python scripts/backtest.py records/predictions.jsonl examples/prices.json`

## 说明

- 时间起卦是主模型。
- 报数起卦可选；股票代码起卦、行情起卦不作为默认断法。
- 行情、新闻、宏观数据只用于现实校验，不用于默认起卦。
- 结果必须带来源追踪、缺失字段和置信度。
- 结果必须带经典摘义、动爻爻位、评分拆解和数据源状态。
- 报告必须展示五卦细断、起卦来源细断和完整六十四卦全象参考。
- 六十四卦全象参考必须统计偏多、偏空、中性、警示等偏性数量，以及各阶段数量。
- 总断必须用传统时序：综卦/互卦看来路，本卦/动爻看现在，变卦看未来，错卦看反证风险。
- HTML 报告必须用折叠区展示起卦和卦象关系算法。
- 默认不做自动交易。
