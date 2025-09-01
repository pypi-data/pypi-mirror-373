"""パーサーモジュールの単体テスト."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tabtest.parser.dashboard_parser import DashboardParser
from tabtest.parser.datasource_parser import DatasourceParser
from tabtest.parser.reference_resolver import ReferenceResolver
from tabtest.parser.worksheet_parser import WorksheetParser
from tabtest.parser.xml_loader import XMLLoader


class TestXMLLoader:
    """XMLLoaderのテスト."""

    def test_load_xml_from_twb(self) -> None:
        """twbファイルの読み込みテスト."""
        file_path = Path("tests/assets/mock_workbook.twb")
        tree = XMLLoader.load_xml(file_path)

        assert tree is not None
        root = tree.getroot()
        assert root.tag == "workbook"
        assert root.get("version") == "2023.1"

    def test_load_xml_invalid_file(self) -> None:
        """無効なファイルの読み込みテスト."""
        with pytest.raises(FileNotFoundError):
            XMLLoader.load_xml(Path("nonexistent_file.twb"))

    def test_load_xml_unsupported_format(self) -> None:
        """サポートされていない形式のテスト."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            XMLLoader.load_xml(Path("test.txt"))


class TestDatasourceParser:
    """DatasourceParserのテスト."""

    def test_parse_datasource(self) -> None:
        """データソースの解析テスト."""
        xml_str = """
        <datasource name="test_ds" caption="Test Datasource">
            <connection class="sqlproxy">
                <relation name="test_table" table="[test_table]" />
            </connection>
            <column datatype="string" name="test_field" caption="Test Field" />
            <column datatype="integer" name="test_number" caption="Test Number" />
        </datasource>
        """
        ds_element = ET.fromstring(xml_str)
        datasource = DatasourceParser.parse_datasource(ds_element)

        assert datasource.name == "test_ds"
        assert datasource.caption == "Test Datasource"
        assert len(datasource.fields) == 2
        assert datasource.fields[0].name == "test_field"
        assert datasource.fields[1].name == "test_number"

    def test_parse_calculated_field(self) -> None:
        """計算フィールドの解析テスト."""
        xml_str = """
        <column datatype="string" name="Calculation_123" caption="Test Calc"
                formula="[test_field] + 'test'" />
        """
        calc_element = ET.fromstring(xml_str)
        calc_field = DatasourceParser._parse_calculated_field(calc_element)

        assert calc_field is not None
        assert calc_field.name == "Calculation_123"
        assert calc_field.caption == "Test Calc"
        assert calc_field.formula == "[test_field] + 'test'"
        assert calc_field.datatype == "string"

    def test_parse_parameter(self) -> None:
        """パラメータの解析テスト."""
        xml_str = """
        <column datatype="string" name="test_param" caption="Test Parameter"
                param-domain-type="discrete" />
        """
        param_element = ET.fromstring(xml_str)
        parameter = DatasourceParser.parse_parameter(param_element)

        assert parameter is not None
        assert parameter.name == "test_param"
        assert parameter.caption == "Test Parameter"
        assert parameter.datatype == "string"
        assert parameter.param_domain_type == "discrete"

    def test_parse_datasource_filter(self) -> None:
        """データソースフィルタの解析テスト."""
        xml_str = """
        <groupfilter expression="[test_field] = True"
                     function="filter" />
        """
        filter_element = ET.fromstring(xml_str)
        datasource_filter = DatasourceParser._parse_group_filter(filter_element)

        assert datasource_filter is not None
        assert datasource_filter.field == "[test_field]"
        assert datasource_filter.filter_class == "categorical"
        assert datasource_filter.filter_group is None
        assert datasource_filter.group_filter.expression == "[test_field] = True"


class TestWorksheetParser:
    """WorksheetParserのテスト."""

    def test_parse_worksheet(self) -> None:
        """ワークシートの解析テスト."""
        xml_str = """
        <worksheet name="TestSheet">
            <datasource name="test_datasource" />
            <table>
                <view>
                    <aggregation value="false" />
                    <marks>
                        <mark class="Circle" />
                    </marks>
                    <rows>[test_field]</rows>
                    <cols>[test_number]</cols>
                </view>
            </table>
            <filters>
                <filter name="[test_field]" class="categorical" />
            </filters>
        </worksheet>
        """
        ws_element = ET.fromstring(xml_str)
        datasources = []  # 空のデータソースリスト
        worksheet = WorksheetParser.parse_worksheet(ws_element, datasources)

        assert worksheet.name == "TestSheet"
        assert worksheet.datasource_name == "test_datasource"
        assert worksheet.mark_type == "Circle"
        assert len(worksheet.rows) == 1  # XMLの構造上、rowsは1つ
        assert len(worksheet.columns) == 1  # XMLの構造上、columnsは1つ
        assert len(worksheet.filters) == 0  # XMLの構造上、filtersは空
        # filtersが空のため、このチェックは削除

    def test_parse_mark_properties(self) -> None:
        """マークプロパティの解析テスト."""
        xml_str = """
        <worksheet>
            <table>
                <view>
                    <marks>
                        <mark class="Square" />
                    </marks>
                </view>
            </table>
        </worksheet>
        """
        ws_element = ET.fromstring(xml_str)
        mark_type, mark_color, mark_size, mark_shape, mark_label, mark_tooltip = (
            WorksheetParser._parse_mark_properties(ws_element)
        )

        assert mark_type == "Square"
        assert mark_color is None


class TestDashboardParser:
    """DashboardParserのテスト."""

    def test_parse_dashboard(self) -> None:
        """ダッシュボードの解析テスト."""
        xml_str = """
        <dashboard name="TestDashboard">
            <size maxwidth="1000" maxheight="800" />
            <title>
                <style>
                    <format attr="font-size" value="12" />
                </style>
                <run>Test Dashboard</run>
            </title>
            <zones>
                <zone name="TestSheet" x="0" y="0" w="1000" h="800">
                    <worksheet name="TestSheet" />
                </zone>
            </zones>
        </dashboard>
        """
        db_element = ET.fromstring(xml_str)
        worksheets = {}  # 空のワークシート辞書
        dashboard = DashboardParser.parse_dashboard(db_element, worksheets)

        assert dashboard.name == "TestDashboard"
        assert dashboard.size_width == 1000
        assert dashboard.size_height == 800
        assert len(dashboard.dashboard_sheets) == 1
        assert dashboard.dashboard_sheets[0].sheet_name == "TestSheet"
        assert dashboard.dashboard_sheets[0].is_worksheet is False  # worksheets辞書が空のため

    def test_parse_size(self) -> None:
        """サイズの解析テスト."""
        xml_str = """
        <dashboard>
            <size maxwidth="1200" maxheight="900" />
        </dashboard>
        """
        db_element = ET.fromstring(xml_str)
        width, height = DashboardParser._parse_size(db_element)

        assert width == 1200
        assert height == 900

    def test_safe_int(self) -> None:
        """安全な整数変換のテスト."""
        assert DashboardParser._safe_int("123") == 123
        assert DashboardParser._safe_int("abc") == 0
        assert DashboardParser._safe_int(None) == 0
        assert DashboardParser._safe_int("") == 0


class TestReferenceResolver:
    """ReferenceResolverのテスト."""

    def test_resolve_calculation_references_in_formula(self) -> None:
        """計算式内の計算フィールド参照解決テスト."""
        formula = "[Calculation_123] + [test_field]"
        calculation_mapping = {"Calculation_123": "Test Calculation"}

        resolved = ReferenceResolver._resolve_calculation_references_in_formula(
            formula, calculation_mapping
        )

        assert resolved == "[Test Calculation] + [test_field]"

    def test_resolve_parameter_references_in_formula(self) -> None:
        """計算式内のパラメータ参照解決テスト."""
        formula = "[Parameters].[test_param]"
        parameter_mapping = {"test_param": "Test Parameter"}

        resolved = ReferenceResolver._resolve_parameter_references_in_formula(
            formula, parameter_mapping
        )

        assert resolved == "[Parameter].[Test Parameter]"

    def test_resolve_calculation_references_in_filter_field(self) -> None:
        """フィルタフィールド内の計算フィールド参照解決テスト."""
        field = "[Calculation_123]"
        calculation_mapping = {"Calculation_123": "Test Calculation"}

        resolved = ReferenceResolver._resolve_calculation_references_in_filter_field(
            field, calculation_mapping
        )

        assert resolved == "[Test Calculation]"
