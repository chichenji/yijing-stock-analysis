# Agent 调用模板

## 单股分析

```bash
yijing-stock 000725.SZ --output json
```

Agent 读取 JSON 时优先使用：

- `scores.direction`
- `scores.breakdown.components`
- `main_hexagram.classic`
- `main_hexagram.moving_line_detail`
- `source_trace`
- `risk_notes`
- `review_windows`

## 带手工数据分析

```bash
yijing-stock 000725.SZ \
  --market-json examples/market.json \
  --news-json examples/news.json \
  --macro-json examples/macro.json \
  --output json
```

## 记录预测

```bash
yijing-stock 000725.SZ --output json --record records/predictions.jsonl
```

## 批量分析

```bash
yijing-stock batch examples/tickers.txt --pure-yijing --output html > batch_report.html
```

## 个股画像

```bash
yijing-stock profile 000725.SZ --records records/predictions.jsonl --output json
```

## 复盘

```bash
python scripts/backtest.py records/predictions.jsonl examples/prices.json
```

## 约束

- 默认起卦使用时间卦。
- 行情、新闻、宏观只作现实验象。
- 缺失数据必须读取 `source_trace`，不要把缺失当作成功。
- 输出不得解释成投资建议或自动交易信号。
