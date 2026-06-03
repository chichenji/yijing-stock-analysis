from yijing_stock_analysis.cli import run


def test_cli_json_output(capsys):
    exit_code = run(["600519.SH", "--output", "json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"ticker"' in captured.out


def test_cli_html_output(capsys):
    exit_code = run(["600519.SH", "--output", "html"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "<!doctype html>" in captured.out
    assert "卦象算法与实际计算过程" in captured.out
    assert "代码卦" not in captured.out
    assert "行情卦" not in captured.out
