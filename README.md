# 易经六十四卦股票研判系统

观股如观象，先察其时，再审其位，继而验其气。这个项目以《易经》六十四卦为骨，以梅花易数时间起卦为门，以本卦、动爻、变卦、互卦、错卦、综卦、八卦五行和体用生克为法，专看一只股票在当下所呈现的趋势、节奏、风险、转折和资金情绪。

卦象看势，行情验象；古法定其纲，数据验其应。技术面、资金面、新闻面、宏观面不反过来夺主，只用来校验卦象是否有现实承接。最终输出 Markdown、JSON 或 HTML 报告，既能给人读，也能给 Agent 调用和复盘。

本项目不是自动交易系统，也不是投资建议生成器。它更像一套可复盘的“易象投研案卷”：每一次起卦、断卦、评分、风险提示和后续表现都能留下痕迹，方便日后回看“象从何来，验在何处，错在何因”。

## 断法纲领

- 本卦为主：本卦定当下大势，是本局的正眼。
- 动爻为机：动爻看变化发动之处，是进退、迟速、成败的关节。
- 变卦为势：变卦看后续趋向，判断事情将往哪里走。
- 互卦为里：互卦看内在结构，偏看筹码、分歧、暗线和未明之因。
- 错卦为险：错卦看反证风险，提醒另一面会在什么条件下显形。
- 综卦为观：综卦看反观与来路气象，不直接等同过去，而是换位看局。
- 六十四卦全谱只作背景，不作简单多空投票。
- 技术、资金、新闻、宏观只作验象，不替代卦象主断。
- 默认以时间起卦；报数起卦可选。股票代码和行情数据不作为默认起卦，避免把现代数据包装成古法。

## 功能

- 梅花易数时间起卦。
- 报数起卦。
- 本卦、动爻、变卦分析。
- 互卦、错卦、综卦辅助分析。
- 八卦五行、体用生克关系。
- 六十四卦股票象意参考库。
- 多空偏性和阶段分布统计。
- 技术面、资金面、新闻面、宏观面校验。
- 周易序号、上下经、卦辞摘义、象辞摘义和动爻爻位解释。
- 可解释评分拆解：展示权重、贡献和加减分理由。
- 数据源状态追踪：展示成功、缺失、字段覆盖率和错误说明。
- Markdown、JSON、HTML 三种输出。
- 预测记录 JSONL、复盘统计、批量分析和个股卦象画像。
- Agent 输入/输出 Schema、调用模板和示例数据。

## 安装

需要 Python 3.11 或更高版本。

```bash
pip install -e .
```

安装测试依赖后可运行：

```bash
python -m pytest -q
```

## Agent 安装命令

以下命令只安装本项目本身，适合让各类 Agent 通过终端调用 `yijing-stock` 或 `python scripts/run_yijing_stock.py`。

### 通用 CLI 安装

Windows PowerShell：

```powershell
git clone https://github.com/chichenji/yijing-stock-analysis.git
cd yijing-stock-analysis
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
yijing-stock 000725.SZ --output html
```

macOS / Linux：

```bash
git clone https://github.com/chichenji/yijing-stock-analysis.git
cd yijing-stock-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
yijing-stock 000725.SZ --output html
```

### Codex 本地技能目录

Windows PowerShell：

```powershell
git clone https://github.com/chichenji/yijing-stock-analysis.git "$env:USERPROFILE\.codex\skills\yijing-stock-analysis"
cd "$env:USERPROFILE\.codex\skills\yijing-stock-analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

macOS / Linux：

```bash
git clone https://github.com/chichenji/yijing-stock-analysis.git ~/.codex/skills/yijing-stock-analysis
cd ~/.codex/skills/yijing-stock-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Claude Code 本地技能目录

Windows PowerShell：

```powershell
git clone https://github.com/chichenji/yijing-stock-analysis.git "$env:USERPROFILE\.claude\skills\yijing-stock-analysis"
cd "$env:USERPROFILE\.claude\skills\yijing-stock-analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

macOS / Linux：

```bash
git clone https://github.com/chichenji/yijing-stock-analysis.git ~/.claude/skills/yijing-stock-analysis
cd ~/.claude/skills/yijing-stock-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 其他 Agent 通用接入

对 Gemini CLI、Cursor、Continue、本地 Agent Runner 等能调用终端命令的工具，可以安装到任意固定目录：

```bash
git clone https://github.com/chichenji/yijing-stock-analysis.git ~/agents/yijing-stock-analysis
cd ~/agents/yijing-stock-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
yijing-stock 000725.SZ --question "未来三天走势如何？" --output markdown
```

Agent 调用时可使用：

```bash
yijing-stock 000725.SZ --output markdown
yijing-stock 000725.SZ --output json
yijing-stock 000725.SZ --output html
yijing-stock 000725.SZ --record records/predictions.jsonl --output json
yijing-stock batch examples/tickers.txt --pure-yijing --output html
yijing-stock profile 000725.SZ --records records/predictions.jsonl --output json
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

记录预测：

```bash
yijing-stock 000725.SZ --output json --record records/predictions.jsonl
```

批量分析：

```bash
yijing-stock batch examples/tickers.txt --pure-yijing --output html > batch_report.html
```

个股卦象画像：

```bash
yijing-stock profile 000725.SZ --records records/predictions.jsonl --output markdown
```

复盘 JSONL 记录：

```bash
python scripts/backtest.py records/predictions.jsonl examples/prices.json
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
- `--record`：把本次分析追加写入 JSONL 记录文件。

批量命令：

- `yijing-stock batch <tickers_file>`：读取股票列表，输出横向对比。
- `--output`：批量输出可选 `markdown`、`json`、`html`。
- `--record`：把批量结果逐条追加到 JSONL。

画像命令：

- `yijing-stock profile <ticker>`：从记录文件生成个股卦象画像。
- `--records`：JSONL 记录路径，默认 `records/predictions.jsonl`。
- `--output`：画像输出可选 `markdown`、`json`。

## 报告结构

一份完整 HTML 报告，按“先总断、后细断；先卦象、后验象；先判断、后复盘”的次第展开：

- 首屏总断、方向、综合分和全谱背景统计。
- 来路与内因：综卦与互卦合参。
- 当前主象：本卦与动爻。
- 后势变局：变卦。
- 反证风险：错卦。
- 五卦细断：本卦、变卦、互卦、错卦、综卦。
- 经典摘义：周易序号、上下经、卦辞摘义、象辞摘义。
- 动爻爻位：位置含义、股票白话、确认信号、风险信号。
- 评分拆解：易经、技术、资金、新闻、宏观的权重、贡献和理由。
- 来源状态：行情、新闻、宏观的 provider、状态、字段覆盖率和错误说明。
- 现实校验：技术、资金、新闻、宏观。
- 体用与五行。
- 六十四卦全象参考。
- 卦象算法与实际计算过程。

每个核心卦象都会落到可读、可验、可复盘的层面：

- 卦名。
- 上卦、下卦。
- 五行。
- 动爻。
- 周易序号与上下经。
- 卦辞摘义和象辞摘义。
- 动爻爻位、确认信号和风险信号。
- 卦象短语。
- 股市象意。
- 白话解释。
- 倾向与阶段。

## 易经方法说明

默认起卦采用梅花易数时间起卦口径。取时不取巧，取象不离理：

- 年、月、日合数取上卦。
- 年、月、日、时合数取下卦。
- 同一合数取动爻。
- 八卦逢八归八，六爻逢六归六。
- 动爻阴阳反转得到变卦。
- 二三四爻成下互，三四五爻成上互。
- 六爻阴阳全反为错卦。
- 六爻上下倒置为综卦。

这里的股票分析属于现代象意应用，不是古籍原样的证券预测法。正确用法不是问“明天必涨还是必跌”，而是看：此股当前气象如何，变化发动在哪里，后势是否有承接，风险从哪一面来，现实量价资金是否与卦象相应。

## 数据输入

行情、新闻和宏观数据可以通过 JSON 输入。数据只是验象之器，不是起卦之主。缺失字段不会被静默伪造，报告会展示来源状态、字段覆盖率、缺失字段和错误说明，方便复盘时知道“此断有几分凭卦，有几分凭数”。

示例：

```bash
python scripts/run_yijing_stock.py 000725.SZ \
  --market-json examples/market.json \
  --news-json examples/news.json \
  --macro-json examples/macro.json \
  --output html
```

这些示例文件已经包含在 `examples/` 目录。Agent 可参考：

- `schemas/analysis_input.schema.json`
- `schemas/analysis_result.schema.json`
- `prompts/agent_usage.md`

## 复盘

易占贵在有验，投研贵在能复盘。项目支持把每次研判写入 JSONL，用于记录输入、卦象、评分、建议、来源状态和后续实际表现。长期按同一股票、同一周期回看，才能知道哪些卦象常应、哪些断语过急、哪些风险被忽略。

```bash
yijing-stock 000725.SZ --output json --record records/predictions.jsonl
python scripts/backtest.py records/predictions.jsonl examples/prices.json
yijing-stock profile 000725.SZ --records records/predictions.jsonl
```

## 项目结构

```text
src/yijing_stock_analysis/
  cast.py              起卦逻辑
  cast_trace.py        起卦过程说明
  classic_text.py      周易序号、经典摘义、动爻解释
  hexagrams.py         六十四卦基础映射
  hexagram_reference.py 六十四卦股票象意参考
  relations.py         互卦、错卦、综卦、体用关系
  scoring.py           综合评分
  score_breakdown.py   评分拆解
  records.py           JSONL 预测记录
  batch.py             批量分析
  profile.py           个股卦象画像
  report.py            Markdown / JSON 输出
  report_html.py       HTML 报告入口
  html_sections.py     HTML 报告结构
  html_styles.py       HTML 样式
  engine.py            分析引擎
```

## 边界声明

易有象，市有变；象可启思，不可代人决断。本项目仅用于研究、学习、复盘和辅助分析，不构成任何投资建议。股票市场受政策、流动性、基本面、情绪和突发事件影响，任何卦象分析都不能替代独立判断、仓位纪律和风险控制。
