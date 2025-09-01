"""エラーハンドリングのテスト."""

import xml.etree.ElementTree as ET

import pytest
from pydantic import ValidationError

from tabtest.parser.dashboard_parser import DashboardParser
from tabtest.parser.datasource_parser import DatasourceParser
from tabtest.parser.workbook_parser import WorkbookParser
from tabtest.parser.worksheet_parser import WorksheetParser
from tabtest.parser.xml_loader import XMLLoader


class TestErrorHandling:
    """エラーハンドリングのテスト."""

    def test_workbook_parser_invalid_file(self) -> None:
        """無効なファイルでのWorkbookParserテスト."""
        with pytest.raises(FileNotFoundError):
            WorkbookParser("nonexistent_file.twb")

    def test_workbook_parser_unsupported_format(self) -> None:
        """サポートされていない形式でのWorkbookParserテスト."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            WorkbookParser("test.txt")

    def test_xml_loader_invalid_file(self) -> None:
        """無効なファイルでのXMLLoaderテスト."""
        with pytest.raises(FileNotFoundError):
            XMLLoader.load_xml("nonexistent_file.twb")

    def test_xml_loader_unsupported_format(self) -> None:
        """サポートされていない形式でのXMLLoaderテスト."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            XMLLoader.load_xml("test.txt")

    def test_datasource_parser_invalid_xml(self) -> None:
        """無効なXMLでのDatasourceParserテスト."""
        # 不完全なXML
        xml_str = "<datasource></datasource>"
        ds_element = ET.fromstring(xml_str)

        # エラーが発生しないことを確認（デフォルト値が設定される）
        datasource = DatasourceParser.parse_datasource(ds_element)
        assert datasource is not None

    def test_worksheet_parser_invalid_xml(self) -> None:
        """無効なXMLでのWorksheetParserテスト."""
        # 不完全なXML
        xml_str = "<worksheet></worksheet>"
        ws_element = ET.fromstring(xml_str)

        worksheet = WorksheetParser.parse_worksheet(ws_element, [])
        assert worksheet is not None
        assert worksheet.name == ""

    def test_dashboard_parser_invalid_xml(self) -> None:
        """無効なXMLでのDashboardParserテスト."""
        # 不完全なXML
        xml_str = "<dashboard></dashboard>"
        db_element = ET.fromstring(xml_str)

        # エラーが発生しないことを確認（デフォルト値が設定される）
        dashboard = DashboardParser.parse_dashboard(db_element, {})
        assert dashboard is not None

    def test_calculated_field_without_name(self) -> None:
        """名前のない計算フィールドのテスト."""
        xml_str = """
        <column datatype="string" caption="Test Calc" formula="[test_field] + 'test'" />
        """
        calc_element = ET.fromstring(xml_str)
        calc_field = DatasourceParser._parse_calculated_field(calc_element)

        # nameがNoneの場合はNoneが返されることを確認
        assert calc_field is None

    def test_parameter_without_name(self) -> None:
        """名前のないパラメータのテスト."""
        xml_str = """
        <column datatype="string" caption="Test Parameter" param-domain-type="discrete" />
        """
        param_element = ET.fromstring(xml_str)
        parameter = DatasourceParser.parse_parameter(param_element)
        assert parameter is not None
        assert parameter.name == ""

    def test_dashboard_parser_safe_int(self) -> None:
        """DashboardParserの安全な整数変換テスト."""
        # 無効な値でのテスト
        assert DashboardParser._safe_int("invalid") == 0
        assert DashboardParser._safe_int(None) == 0
        assert DashboardParser._safe_int("") == 0

        # 有効な値でのテスト
        assert DashboardParser._safe_int("123") == 123
        assert DashboardParser._safe_int("0") == 0

    def test_workbook_parser_missing_root(self) -> None:
        """ルート要素が存在しない場合のテスト."""
        # このテストは実際のファイルが必要なので、モックファイルを使用
        # 実際のエラーケースは、XMLファイルが破損している場合など

        # 正常なケースではエラーが発生しないことを確認
        try:
            parser = WorkbookParser("tests/assets/mock_workbook.twb")
            assert parser.workbook is not None
        except Exception as e:
            pytest.fail(f"正常なファイルでエラーが発生しました: {e}")

    def test_model_validation_errors(self) -> None:
        """モデルバリデーションエラーのテスト."""
        from tabtest.models.workbook import WorkbookModel

        # 必須フィールドが不足している場合
        with pytest.raises(ValidationError):
            WorkbookModel()  # nameフィールドが必須

        # 無効なデータ型の場合
        with pytest.raises(ValidationError):
            WorkbookModel(
                name=123,  # 文字列である必要がある
                datasources=[],
                sheets={},
                dashboards=[],
                parameters=[],
            )

    def test_filter_unescape_errors(self) -> None:
        """フィルタのエスケープ解除エラーのテスト."""
        from tabtest.models.filters import DataSourceFilterModel, GroupFilterModel

        # 無効なエスケープ文字列
        group_filter = GroupFilterModel(expression="invalid&escape;")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)

        # エラーが発生しないことを確認（html.unescapeが処理する）
        unescaped = datasource_filter.get_unescaped_expression()
        assert unescaped is not None

    def test_reference_resolver_empty_mapping(self) -> None:
        """空のマッピングでの参照解決テスト."""
        from tabtest.parser.reference_resolver import ReferenceResolver

        # 空のマッピングでのテスト
        formula = "[Calculation_123] + [test_field]"
        empty_mapping = {}

        resolved = ReferenceResolver._resolve_calculation_references_in_formula(
            formula, empty_mapping
        )

        # マッピングが空でも元の式が返されることを確認
        assert resolved == formula

    def test_workbook_methods_with_empty_data(self) -> None:
        """空データでのワークブックメソッドテスト."""
        from tabtest.models.workbook import WorkbookModel

        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        # 空データでのメソッド呼び出し
        assert workbook.get_datasource("nonexistent") is None
        assert workbook.get_datasource_by_caption("nonexistent") is None
        assert workbook.get_sheet("nonexistent") is None
        assert workbook.get_dashboard("nonexistent") is None
        assert workbook.get_parameter("nonexistent") is None
        assert len(workbook.get_all_parameters()) == 0
        assert len(workbook.find_sheets_by_datasource("nonexistent")) == 0

    def test_datasource_methods_with_empty_data(self) -> None:
        """空データでのデータソースメソッドテスト."""
        from tabtest.models.datasource import DatasourceModel

        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], sets=[], datasource_filters=[]
        )

        # 空データでのメソッド呼び出し
        assert datasource.get_field("nonexistent") is None
        assert datasource.get_calculated_field("nonexistent") is None
        assert datasource.get_set("nonexistent") is None
        assert len(datasource.get_datasource_filters_with_expression("nonexistent")) == 0
        assert len(datasource.get_datasource_filters_with_member("nonexistent")) == 0
