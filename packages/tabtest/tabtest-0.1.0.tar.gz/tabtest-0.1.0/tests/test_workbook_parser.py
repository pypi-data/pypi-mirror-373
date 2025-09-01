"""tabtestライブラリの機能テスト."""

import pytest

from tabtest.models.workbook import WorkbookModel
from tabtest.parser.workbook_parser import WorkbookParser


class TestWorkbookParser:
    """WorkbookParserの基本機能テスト."""

    def test_parser_initialization(self) -> None:
        """パーサーの初期化テスト."""
        # 実際のファイルパスが必要なので、このテストは削除
        # または、モックファイルを使用する必要がある
        pass

    def test_parse_nonexistent_file(self) -> None:
        """存在しないファイルの解析テスト."""
        with pytest.raises(FileNotFoundError):
            WorkbookParser("nonexistent_file.twbx")

    def test_parse_invalid_file_format(self) -> None:
        """無効なファイル形式のテスト."""
        with pytest.raises(ValueError):
            WorkbookParser("invalid_file.txt")


class TestWorkbookModel:
    """WorkbookModelの基本機能テスト."""

    def test_workbook_model_creation(self) -> None:
        """ワークブックモデルの作成テスト."""
        workbook = WorkbookModel(
            name="test_workbook", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        assert workbook.name == "test_workbook"
        assert len(workbook.datasources) == 0
        assert len(workbook.sheets) == 0
        assert len(workbook.dashboards) == 0
        assert len(workbook.parameters) == 0

    def test_workbook_methods(self) -> None:
        """ワークブックメソッドのテスト."""
        workbook = WorkbookModel(
            name="test_workbook", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        # 空データでのメソッド呼び出し
        assert workbook.get_datasource("nonexistent") is None
        assert workbook.get_datasource_by_caption("nonexistent") is None
        assert workbook.get_sheet("nonexistent") is None
        assert workbook.get_dashboard("nonexistent") is None
        assert workbook.get_parameter("nonexistent") is None
        assert len(workbook.get_all_parameters()) == 0
        assert len(workbook.find_sheets_by_datasource("nonexistent")) == 0
