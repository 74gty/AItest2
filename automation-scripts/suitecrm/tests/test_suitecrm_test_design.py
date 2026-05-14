import csv
from pathlib import Path


DESIGN_DIR = Path(__file__).resolve().parents[1] / "test_design"
CASE_MATRIX = DESIGN_DIR / "suitecrm_test_case_matrix.csv"
XMIND_OUTLINE = DESIGN_DIR / "suitecrm_xmind_outline.txt"


def load_case_matrix():
    with CASE_MATRIX.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_suitecrm_case_matrix_reaches_target_scale():
    rows = load_case_matrix()
    total_cases = sum(int(row["total_cases"]) for row in rows)
    covered_cases = sum(int(row["covered_cases"]) for row in rows)

    assert 200 <= total_cases <= 240
    assert covered_cases / total_cases >= 0.96


def test_suitecrm_case_matrix_covers_core_modules():
    rows = load_case_matrix()
    modules = {row["module"] for row in rows}

    assert {"Login", "Dashboard", "Accounts", "Contacts", "Leads", "Opportunities", "Activities"}.issubset(modules)


def test_suitecrm_xmind_outline_keeps_design_topics():
    content = XMIND_OUTLINE.read_text(encoding="utf-8")

    for topic in ["登录与会话", "仪表盘", "客户 Accounts", "API", "权限"]:
        assert topic in content
