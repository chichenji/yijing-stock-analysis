# 易经六十四卦股票研判系统

这是一个把《易经》象意分析与股票现实数据校验结合起来的辅助研判工具。它以传统时间起卦为主，通过本卦、动爻、变卦、互卦、错卦、综卦、八卦五行和体用关系，分析股票的趋势、节奏、风险、转折和资金情绪，再用技术面、资金面、新闻面、宏观面做现实校验。

本项目不是自动交易系统，也不是投资建议生成器。它更像一个可复盘的“易象投研报告引擎”：卦象负责看势，数据负责验象，最终输出 Markdown、JSON 或 HTML 报告。

## 核心原则

- 本卦为主，动爻为机，变卦为势。
- 互卦看内在结构，错卦看反证风险，综卦看反观与来路气象。
- 六十四卦全谱统计只作背景参考，不作多空投票。
- 技术面、资金面、新闻面和宏观面只作现实校验，不替代卦象主断。
- 默认使用时间起卦；报数起卦可选。
- 股票代码和行情数据不作为默认起卦方法，避免把现代数据包装成传统古法。

## 功能

- 梅花易数时间起卦。
- 报数起卦。
- 本卦、动爻、变卦分析。
- 互卦、错卦、综卦辅助分析。
- 八卦五行、体用生克关系。
- 六十四卦股票象意参考库。
- 多空偏性和阶段分布统计。
- 技术面、资金面、新闻面、宏观面校验。
- Markdown、JSON、HTML 三种输出。
- 预测记录与复盘数据结构。

## 安装

需要 Python 3.11 或更高版本。

```bash
pip install -e .
```

安装测试依赖后可运行：

```bash
python -m pytest -q
```

## 快速使用

生成 Markdown 报告：

```bash
python scripts/run_yijing_stock.py 000725.SZ
```

生成 HTML 报告：

```bash
python scripts/run_yijing_stock.py 000725.SZ --output html > boe_yijing_report.html
```

生成 JSON：

```bash
python scripts/run_yijing_stock.py 000725.SZ --output json
```

只用易经，不加入现实校验权重：

```bash
python scripts/run_yijing_stock.py 000725.SZ --pure-yijing
```

报数起卦：

```bash
python scripts/run_yijing_stock.py 000725.SZ --cast-method numbers --numbers 7 3 5
```

## CLI 参数

- `ticker`：股票代码，例如 `000725.SZ`、`600519.SH`。
- `--question`：提问内容，默认是“未来三天走势如何？”。
- `--horizon`：研判周期，默认 `3d`。
- `--cast-method`：起卦方式，默认 `time`。
- `--numbers`：报数起卦数字。
- `--pure-yijing`：只用易经评分。
- `--output`：输出格式，可选 `markdown`、`json`、`html`。
- `--market-json`：外部行情数据。
- `--news-json`：外部新闻数据。
- `--macro-json`：外部宏观数据。

## 报告结构

HTML 报告包含：

- 首屏总断、方向、综合分和全谱背景统计。
- 来路与内因：综卦与互卦合参。
- 当前主象：本卦与动爻。
- 后势变局：变卦。
- 反证风险：错卦。
- 五卦细断：本卦、变卦、互卦、错卦、综卦。
- 现实校验：技术、资金、新闻、宏观。
- 体用与五行。
- 六十四卦全象参考。
- 卦象算法与实际计算过程。

每个核心卦象会输出：

- 卦名。
- 上卦、下卦。
- 五行。
- 动爻。
- 卦象短语。
- 股市象意。
- 白话解释。
- 倾向与阶段。

## 易经方法说明

默认起卦采用梅花易数时间起卦口径：

- 年、月、日合数取上卦。
- 年、月、日、时合数取下卦。
- 同一合数取动爻。
- 八卦逢八归八，六爻逢六归六。
- 动爻阴阳反转得到变卦。
- 二三四爻成下互，三四五爻成上互。
- 六爻阴阳全反为错卦。
- 六爻上下倒置为综卦。

这里的股票分析属于现代象意应用，不是古籍原样的证券预测法。正确用法是把卦象当作趋势、结构、节奏和风险的象意框架，再用现实数据校验。

## 数据输入

行情、新闻和宏观数据可以通过 JSON 输入。缺失字段不会被静默伪造，报告会展示来源追踪和缺失字段，方便复盘。

示例：

```bash
python scripts/run_yijing_stock.py 000725.SZ \
  --market-json examples/market.json \
  --news-json examples/news.json \
  --macro-json examples/macro.json \
  --output html
```

## 复盘

项目保留复盘数据结构，用于记录每次研判的输入、卦象、评分、建议和后续实际表现。建议按同一股票、同一周期持续复盘，观察卦象判断与现实走势之间的偏差。

## 项目结构

```text
src/yijing_stock_analysis/
  cast.py              起卦逻辑
  cast_trace.py        起卦过程说明
  hexagrams.py         六十四卦基础映射
  hexagram_reference.py 六十四卦股票象意参考
  relations.py         互卦、错卦、综卦、体用关系
  scoring.py           综合评分
  report.py            Markdown / JSON 输出
  report_html.py       HTML 报告输出
  engine.py            分析引擎
```

## 边界声明

本项目仅用于研究、学习、复盘和辅助分析，不构成任何投资建议。股票市场受政策、流动性、基本面、情绪和突发事件影响，任何卦象分析都不能替代独立判断和风险控制。
