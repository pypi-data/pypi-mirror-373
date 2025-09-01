"""モデルクラスの単体テスト."""

from tabtest.models.calculated_fields import CalculatedFieldModel
from tabtest.models.dashboard import DashboardModel
from tabtest.models.datasource import DatasourceModel
from tabtest.models.filters import DataSourceFilterModel
from tabtest.models.parameters import ParameterModel
from tabtest.models.sets import SetModel
from tabtest.models.workbook import WorkbookModel
from tabtest.models.worksheet import FilterModel, WorksheetModel


class TestWorkbookModel:
    """WorkbookModelのテスト."""

    def test_workbook_creation(self) -> None:
        """ワークブックモデルの作成テスト."""
        workbook = WorkbookModel(
            name="Test Workbook", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        assert workbook.name == "Test Workbook"
        assert len(workbook.datasources) == 0
        assert len(workbook.sheets) == 0
        assert len(workbook.dashboards) == 0
        assert len(workbook.parameters) == 0

    def test_get_datasource(self) -> None:
        """データソース取得テスト."""
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[])
        workbook = WorkbookModel(
            name="Test", datasources=[datasource], sheets={}, dashboards=[], parameters=[]
        )

        found = workbook.get_datasource("test_ds")
        assert found is not None
        assert found.name == "test_ds"

        not_found = workbook.get_datasource("nonexistent")
        assert not_found is None

    def test_get_datasource_by_caption(self) -> None:
        """キャプションによるデータソース取得テスト."""
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[])
        workbook = WorkbookModel(
            name="Test", datasources=[datasource], sheets={}, dashboards=[], parameters=[]
        )

        found = workbook.get_datasource_by_caption("Test DS")
        assert found is not None
        assert found.caption == "Test DS"

    def test_get_sheet(self) -> None:
        """ワークシート取得テスト."""
        worksheet = WorksheetModel(name="test_sheet", datasource_name="test_ds")
        workbook = WorkbookModel(
            name="Test",
            datasources=[],
            sheets={"test_sheet": worksheet},
            dashboards=[],
            parameters=[],
        )

        found = workbook.get_sheet("test_sheet")
        assert found is not None
        assert found.name == "test_sheet"

    def test_get_dashboard(self) -> None:
        """ダッシュボード取得テスト."""
        dashboard = DashboardModel(name="test_dashboard", dashboard_sheets=[])
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[dashboard], parameters=[]
        )

        found = workbook.get_dashboard("test_dashboard")
        assert found is not None
        assert found.name == "test_dashboard"

    def test_get_parameter(self) -> None:
        """パラメータ取得テスト."""
        parameter = ParameterModel(name="test_param", caption="Test Param", datatype="string")
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[parameter]
        )

        found = workbook.get_parameter("test_param")
        assert found is not None
        assert found.name == "test_param"

    def test_get_all_parameters(self) -> None:
        """全パラメータ取得テスト."""
        param1 = ParameterModel(name="param1", caption="Param 1", datatype="string")
        param2 = ParameterModel(name="param2", caption="Param 2", datatype="integer")
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[param1, param2]
        )

        all_params = workbook.get_all_parameters()
        assert len(all_params) == 2
        assert all_params[0].name == "param1"
        assert all_params[1].name == "param2"


class TestDatasourceModel:
    """DatasourceModelのテスト."""

    def test_datasource_creation(self) -> None:
        """データソースモデルの作成テスト."""
        datasource = DatasourceModel(name="test_ds", caption="Test Datasource", fields=[])

        assert datasource.name == "test_ds"
        assert datasource.caption == "Test Datasource"
        assert len(datasource.fields) == 0

    def test_get_field(self) -> None:
        """フィールド取得テスト."""
        from tabtest.models.datasource import DatasourceFieldModel

        field = DatasourceFieldModel(name="test_field", caption="Test Field", datatype="string")
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[field])

        found = datasource.get_field("test_field")
        assert found is not None
        assert found.name == "test_field"
        assert found.caption == "Test Field"

    def test_get_calculated_field(self) -> None:
        """計算フィールド取得テスト."""
        calc_field = CalculatedFieldModel(
            name="Calculation_123",
            caption="Test Calc",
            formula="[test_field] + 'test'",
            datatype="string",
        )
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", calculated_fields=[calc_field]
        )

        found = datasource.get_calculated_field("Calculation_123")
        assert found is not None
        assert found.name == "Calculation_123"
        assert found.caption == "Test Calc"

    def test_get_set(self) -> None:
        """セット取得テスト."""
        set_obj = SetModel(name="test_set", caption="Test Set", field_name="test_field")
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[], sets=[set_obj])

        found = datasource.get_set("test_set")
        assert found is not None
        assert found.name == "test_set"
        assert found.caption == "Test Set"

    def test_get_datasource_filters_with_expression(self) -> None:
        """条件式によるデータソースフィルタ取得テスト."""
        from tabtest.models.filters import GroupFilterModel

        group_filter = GroupFilterModel(expression="[test_field] = 'test'")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[datasource_filter]
        )

        found = datasource.get_datasource_filters_with_expression("=")
        assert len(found) == 1
        assert found[0].field == "[test_field]"

    def test_get_datasource_filters_with_member(self) -> None:
        """メンバー名によるデータソースフィルタ取得テスト."""
        from tabtest.models.filters import GroupFilterModel

        group_filter = GroupFilterModel(member="test_member")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[datasource_filter]
        )

        found = datasource.get_datasource_filters_with_member("test_member")
        assert len(found) == 1
        assert found[0].field == "[test_field]"


class TestWorksheetModel:
    """WorksheetModelのテスト."""

    def test_worksheet_creation(self) -> None:
        """ワークシートモデルの作成テスト."""
        worksheet = WorksheetModel(
            name="test_sheet",
            datasource_name="test_ds",
            rows=[],
            columns=[],
            filters=[],
        )

        assert worksheet.name == "test_sheet"
        assert worksheet.datasource_name == "test_ds"
        assert len(worksheet.rows) == 0
        assert len(worksheet.columns) == 0
        assert len(worksheet.filters) == 0


class TestDashboardModel:
    """DashboardModelのテスト."""

    def test_dashboard_creation(self) -> None:
        """ダッシュボードモデルの作成テスト."""
        from tabtest.models.dashboard import DashboardSheetModel

        sheet = DashboardSheetModel(
            sheet_name="test_sheet", x=0, y=0, width=100, height=100, is_worksheet=True
        )
        dashboard = DashboardModel(
            name="test_dashboard", size_width=1000, size_height=800, dashboard_sheets=[sheet]
        )

        assert dashboard.name == "test_dashboard"
        assert dashboard.size_width == 1000
        assert dashboard.size_height == 800
        assert len(dashboard.dashboard_sheets) == 1
        assert dashboard.dashboard_sheets[0].sheet_name == "test_sheet"

    def test_get_worksheet_count(self) -> None:
        """ワークシート数の取得テスト."""
        from tabtest.models.dashboard import DashboardSheetModel

        sheet1 = DashboardSheetModel(
            sheet_name="sheet1", x=0, y=0, width=100, height=100, is_worksheet=True
        )
        sheet2 = DashboardSheetModel(
            sheet_name="sheet2", x=100, y=0, width=100, height=100, is_worksheet=True
        )
        sheet3 = DashboardSheetModel(
            sheet_name="text1", x=200, y=0, width=100, height=100, is_worksheet=False
        )  # テキストボックス

        dashboard = DashboardModel(name="test_dashboard", dashboard_sheets=[sheet1, sheet2, sheet3])

        worksheet_count = dashboard.get_worksheet_count()
        assert worksheet_count == 2  # sheet1, sheet2のみがワークシート（sheet3はテキストボックス）


class TestCalculatedFieldModel:
    """CalculatedFieldModelのテスト."""

    def test_calculated_field_creation(self) -> None:
        """計算フィールドモデルの作成テスト."""
        calc_field = CalculatedFieldModel(
            name="Calculation_123",
            caption="Test Calculation",
            formula="[test_field] + 'test'",
            datatype="string",
        )

        assert calc_field.name == "Calculation_123"
        assert calc_field.caption == "Test Calculation"
        assert calc_field.formula == "[test_field] + 'test'"
        assert calc_field.datatype == "string"


class TestParameterModel:
    """ParameterModelのテスト."""

    def test_parameter_creation(self) -> None:
        """パラメータモデルの作成テスト."""
        parameter = ParameterModel(
            name="test_param",
            caption="Test Parameter",
            datatype="string",
            param_domain_type="discrete",
        )

        assert parameter.name == "test_param"
        assert parameter.caption == "Test Parameter"
        assert parameter.datatype == "string"
        assert parameter.param_domain_type == "discrete"


class TestFilterModels:
    """フィルタモデルのテスト."""

    def test_data_source_filter_creation(self) -> None:
        """データソースフィルタモデルの作成テスト."""
        from tabtest.models.filters import GroupFilterModel

        group_filter = GroupFilterModel(expression="[test_field] = 'test'")
        datasource_filter = DataSourceFilterModel(
            field="[test_field]",
            filter_class="categorical",
            filter_group="2",
            group_filter=group_filter,
        )

        assert datasource_filter.field == "[test_field]"
        assert datasource_filter.filter_class == "categorical"
        assert datasource_filter.filter_group == "2"
        assert datasource_filter.group_filter.expression == "[test_field] = 'test'"

    def test_filter_creation(self) -> None:
        """フィルタモデルの作成テスト."""
        filter_obj = FilterModel(
            name="test_filter", field="[test_field]", filter_type="categorical"
        )

        assert filter_obj.field == "[test_field]"
        assert filter_obj.filter_type == "categorical"

    def test_has_member(self) -> None:
        """メンバー名チェックテスト."""
        from tabtest.models.filters import GroupFilterModel

        # member属性に含まれる場合
        group_filter = GroupFilterModel(member="test_member_value")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)

        assert datasource_filter.has_member("test_member") is True
        assert datasource_filter.has_member("nonexistent") is False

        # expression属性に含まれる場合
        group_filter2 = GroupFilterModel(expression="[test_field] = 'test_value'")
        datasource_filter2 = DataSourceFilterModel(field="[test_field]", group_filter=group_filter2)

        assert datasource_filter2.has_member("test_value") is True

    def test_get_unescaped_expression(self) -> None:
        """エスケープ解除された条件式取得テスト."""
        from tabtest.models.filters import GroupFilterModel

        group_filter = GroupFilterModel(expression="[test_field] = 'test'")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)

        unescaped = datasource_filter.get_unescaped_expression()
        assert unescaped == "[test_field] = 'test'"

    def test_get_unescaped_member(self) -> None:
        """エスケープ解除されたメンバー名取得テスト."""
        from tabtest.models.filters import GroupFilterModel

        group_filter = GroupFilterModel(member="&apos;test&apos;")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)

        unescaped = datasource_filter.get_unescaped_member()
        assert unescaped == "'test'"


class TestSetModel:
    """SetModelのテスト."""

    def test_set_creation(self) -> None:
        """セットモデルの作成テスト."""
        set_obj = SetModel(name="test_set", caption="Test Set", field_name="test_field")

        assert set_obj.name == "test_set"
        assert set_obj.caption == "Test Set"
