"""pytest用の汎用フィクスチャ."""

from pathlib import Path
from typing import Any

import pytest

from tabtest.models.workbook import WorkbookModel
from tabtest.parser.workbook_parser import WorkbookParser


@pytest.fixture
def workbook_parser(request: object) -> WorkbookParser:
    """
    ワークブックパーサーのフィクスチャ.

    使用方法:
    @pytest.mark.parametrize("workbook_parser", ["./path/to/your/workbook.twbx"], indirect=True)
    def test_workbook(workbook_parser):
        assert workbook_parser.workbook.name == "Expected Name"
    """
    # テストファイルのパスを取得
    test_file: Any = getattr(request, "param", None)
    if test_file is None:
        pytest.skip(
            "テストファイルが指定されていません。@pytest.mark.parametrizeでファイルパスを指定してください。"
        )

    test_file_str = str(test_file)

    # ファイルが存在するかチェック
    if not Path(test_file_str).exists():
        pytest.skip(f"テストファイルが見つかりません: {test_file}")

    return WorkbookParser(test_file_str)


@pytest.fixture
def workbook(workbook_parser: WorkbookParser) -> WorkbookModel:
    """
    解析済みワークブックのフィクスチャ.

    使用方法:
    @pytest.mark.parametrize("workbook_parser", ["./path/to/your/workbook.twbx"], indirect=True)
    def test_workbook(workbook):
        assert workbook.name == "Expected Name"
        assert len(workbook.datasources) > 0
    """
    return workbook_parser.workbook or WorkbookModel(
        name="",
        datasources=[],
        sheets={},
        dashboards=[],
        parameters=[],
        version=None,
        author=None,
        created_date=None,
        modified_date=None,
        description=None,
    )
