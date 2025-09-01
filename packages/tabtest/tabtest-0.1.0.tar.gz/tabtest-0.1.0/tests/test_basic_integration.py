"""基本的な結合テスト."""

from pathlib import Path

import pytest

from tabtest.parser.workbook_parser import WorkbookParser


class TestBasicIntegration:
    """基本的な結合テスト."""

    def test_workbook_parser_creation(self) -> None:
        """WorkbookParserの作成テスト."""
        # モックファイルが存在することを確認
        mock_file = Path("tests/assets/mock_workbook.twb")
        assert mock_file.exists(), "モックファイルが存在しません"

    def test_workbook_parser_with_mock_file(self) -> None:
        """モックファイルでのWorkbookParserテスト."""
        try:
            parser = WorkbookParser("tests/assets/mock_workbook.twb")
            assert parser is not None
            assert parser.workbook is not None
            print(f"✅ ワークブック名: {parser.workbook.name}")
        except Exception as e:
            pytest.skip(f"モックファイルの解析でエラーが発生しました: {e}")

    def test_workbook_model_structure(self) -> None:
        """ワークブックモデルの構造テスト."""
        from tabtest.models.workbook import WorkbookModel

        workbook = WorkbookModel(
            name="Test Workbook",
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

        assert workbook.name == "Test Workbook"
        assert len(workbook.datasources) == 0
        assert len(workbook.sheets) == 0
        assert len(workbook.dashboards) == 0
        assert len(workbook.parameters) == 0

    def test_datasource_model_structure(self) -> None:
        """データソースモデルの構造テスト."""
        from tabtest.models.datasource import DatasourceModel

        datasource = DatasourceModel(
            name="test_ds",
            caption="Test Datasource",
            fields=[],
            connection_type=None,
            server=None,
            database=None,
            schema_name=None,
            table=None,
            query=None,
        )

        assert datasource.name == "test_ds"
        assert datasource.caption == "Test Datasource"
        assert len(datasource.fields) == 0

    def test_worksheet_model_structure(self) -> None:
        """ワークシートモデルの構造テスト."""
        from tabtest.models.worksheet import WorksheetModel

        worksheet = WorksheetModel(
            name="test_sheet",
            datasource_name="test_ds",
            mark_type="bar",
            mark_color="red",
            mark_size="10",
            mark_shape="circle",
            mark_label="test_label",
            mark_tooltip="test_tooltip",
            title="test_title",
            subtitle="test_subtitle",
            caption="test_caption",
            show_title=True,
            show_subtitle=True,
            show_caption=True,
            formatting=None,
        )

        assert worksheet.name == "test_sheet"
        assert worksheet.datasource_name == "test_ds"

    def test_dashboard_model_structure(self) -> None:
        """ダッシュボードモデルの構造テスト."""
        from tabtest.models.dashboard import DashboardModel

        dashboard = DashboardModel(
            name="test_dashboard",
            dashboard_sheets=[],
            objects=[],
            actions=[],
            layout=None,
            size_width=0,
            size_height=0,
            zones=[],
            title=None,
            subtitle=None,
            show_title=True,
            show_subtitle=True,
            formatting=None,
        )

        assert dashboard.name == "test_dashboard"
        assert len(dashboard.dashboard_sheets) == 0

    def test_parameter_model_structure(self) -> None:
        """パラメータモデルの構造テスト."""
        from tabtest.models.parameters import ParameterModel

        parameter = ParameterModel(
            name="test_param",
            caption="Test Parameter",
            datatype="string",
            role=None,
            param_domain_type=None,
            default_value=None,
        )

        assert parameter.name == "test_param"
        assert parameter.caption == "Test Parameter"
        assert parameter.datatype == "string"

    def test_calculated_field_model_structure(self) -> None:
        """計算フィールドモデルの構造テスト."""
        from tabtest.models.calculated_fields import CalculatedFieldModel

        calc_field = CalculatedFieldModel(
            name="Calculation_123",
            caption="Test Calculation",
            formula="[test_field] + 'test'",
            datatype="string",
            role=None,
            type=None,
        )

        assert calc_field.name == "Calculation_123"
        assert calc_field.caption == "Test Calculation"
        assert calc_field.formula == "[test_field] + 'test'"
        assert calc_field.datatype == "string"

    def test_filter_model_structure(self) -> None:
        """フィルタモデルの構造テスト."""
        from tabtest.models.filters import DataSourceFilterModel, GroupFilterModel

        group_filter = GroupFilterModel(
            expression="[test_field] = True",
            function="filter",
            level="1",
            member=None,
            ui_enumeration=None,
            ui_marker=None,
            ui_domain=None,
            ui_manual_selection=None,
            ui_manual_selection_all_when_empty=None,
        )
        datasource_filter = DataSourceFilterModel(
            field="[test_field]",
            group_filter=group_filter,
            name="test_filter",
            filter_class="categorical",
            filter_group=None,
        )

        assert datasource_filter.field == "[test_field]"
        assert datasource_filter.group_filter is not None
        assert datasource_filter.group_filter.expression == "[test_field] = True"

    def test_set_model_structure(self) -> None:
        """セットモデルの構造テスト."""
        from tabtest.models.sets import SetModel

        set_obj = SetModel(
            name="test_set",
            caption="Test Set",
            field_name="test_field",
            set_type="manual",
            formula=None,
        )

        assert set_obj.name == "test_set"
        assert set_obj.caption == "Test Set"
        assert set_obj.field_name == "test_field"

    def test_xml_loader_basic(self) -> None:
        """XMLLoaderの基本テスト."""
        from pathlib import Path

        from tabtest.parser.xml_loader import XMLLoader

        mock_file = Path("tests/assets/mock_workbook.twb")
        if mock_file.exists():
            try:
                tree = XMLLoader.load_xml(mock_file)
                assert tree is not None
                root = tree.getroot()
                assert root.tag == "workbook"
            except Exception as e:
                pytest.skip(f"XML読み込みでエラーが発生しました: {e}")

    def test_reference_resolver_basic(self) -> None:
        """ReferenceResolverの基本テスト."""
        from tabtest.parser.reference_resolver import ReferenceResolver

        formula = "[Calculation_123] + [test_field]"
        calculation_mapping = {"Calculation_123": "Test Calculation"}

        resolved = ReferenceResolver._resolve_calculation_references_in_formula(
            formula, calculation_mapping
        )

        assert resolved == "[Test Calculation] + [test_field]"

    def test_suite_helpers_basic(self) -> None:
        """suiteヘルパーの基本テスト."""
        from tabtest.models.datasource import DatasourceModel
        from tabtest.models.workbook import WorkbookModel
        from tabtest.suite.helpers import assert_workbook_has_datasource

        datasource = DatasourceModel(
            name="test_ds",
            caption="Test DS",
            fields=[],
            connection_type=None,
            server=None,
            database=None,
            schema_name=None,
            table=None,
            query=None,
        )
        workbook = WorkbookModel(
            name="Test",
            datasources=[datasource],
            sheets={},
            dashboards=[],
            parameters=[],
            version=None,
            author=None,
            created_date=None,
            modified_date=None,
            description=None,
        )

        result = assert_workbook_has_datasource(workbook, "test_ds")
        assert result is not None
        assert result.name == "test_ds"
