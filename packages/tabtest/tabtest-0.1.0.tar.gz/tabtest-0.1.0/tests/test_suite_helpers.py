"""suiteヘルパー関数の単体テスト."""

import pytest

from tabtest.models.calculated_fields import CalculatedFieldModel
from tabtest.models.dashboard import DashboardModel
from tabtest.models.datasource import DatasourceModel
from tabtest.models.filters import DataSourceFilterModel, GroupFilterModel
from tabtest.models.workbook import WorkbookModel
from tabtest.models.worksheet import WorksheetModel
from tabtest.suite.helpers import (
    assert_datasource_has_calculated_field,
    assert_datasource_has_filter_with_expression,
    assert_datasource_has_filter_with_member,
    assert_sheet_has_field_in_columns,
    assert_sheet_has_field_in_rows,
    assert_workbook_has_dashboard,
    assert_workbook_has_datasource,
    assert_workbook_has_sheet,
)


class TestSuiteHelpers:
    """suiteヘルパー関数のテスト."""

    def test_assert_workbook_has_datasource_success(self) -> None:
        """データソース存在確認テスト（成功）."""
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[])
        workbook = WorkbookModel(
            name="Test", datasources=[datasource], sheets={}, dashboards=[], parameters=[]
        )

        result = assert_workbook_has_datasource(workbook, "test_ds")
        assert result is not None
        assert result.name == "test_ds"

    def test_assert_workbook_has_datasource_by_caption(self) -> None:
        """キャプションによるデータソース存在確認テスト."""
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[])
        workbook = WorkbookModel(
            name="Test", datasources=[datasource], sheets={}, dashboards=[], parameters=[]
        )

        result = assert_workbook_has_datasource(workbook, "Test DS")
        assert result is not None
        assert result.caption == "Test DS"

    def test_assert_workbook_has_datasource_failure(self) -> None:
        """データソース存在確認テスト（失敗）."""
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        with pytest.raises(AssertionError):
            assert_workbook_has_datasource(workbook, "nonexistent")

    def test_assert_workbook_has_sheet_success(self) -> None:
        """ワークシート存在確認テスト（成功）."""
        worksheet = WorksheetModel(name="test_sheet", datasource_name="test_ds")
        workbook = WorkbookModel(
            name="Test",
            datasources=[],
            sheets={"test_sheet": worksheet},
            dashboards=[],
            parameters=[],
        )

        result = assert_workbook_has_sheet(workbook, "test_sheet")
        assert result is not None
        assert result.name == "test_sheet"

    def test_assert_workbook_has_sheet_failure(self) -> None:
        """ワークシート存在確認テスト（失敗）."""
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        with pytest.raises(AssertionError):
            assert_workbook_has_sheet(workbook, "nonexistent")

    def test_assert_workbook_has_dashboard_success(self) -> None:
        """ダッシュボード存在確認テスト（成功）."""
        dashboard = DashboardModel(name="test_dashboard", dashboard_sheets=[])
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[dashboard], parameters=[]
        )

        result = assert_workbook_has_dashboard(workbook, "test_dashboard")
        assert result is not None
        assert result.name == "test_dashboard"

    def test_assert_workbook_has_dashboard_failure(self) -> None:
        """ダッシュボード存在確認テスト（失敗）."""
        workbook = WorkbookModel(
            name="Test", datasources=[], sheets={}, dashboards=[], parameters=[]
        )

        with pytest.raises(AssertionError):
            assert_workbook_has_dashboard(workbook, "nonexistent")

    def test_assert_datasource_has_calculated_field_success(self) -> None:
        """計算フィールド存在確認テスト（成功）."""
        calc_field = CalculatedFieldModel(
            name="Calculation_123",
            caption="Test Calc",
            formula="[test_field] + 'test'",
            datatype="string",
        )
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", calculated_fields=[calc_field]
        )

        result = assert_datasource_has_calculated_field(datasource, "Calculation_123")
        assert result is not None
        assert result.name == "Calculation_123"

    def test_assert_datasource_has_calculated_field_failure(self) -> None:
        """計算フィールド存在確認テスト（失敗）."""
        datasource = DatasourceModel(name="test_ds", caption="Test DS", fields=[])

        with pytest.raises(AssertionError):
            assert_datasource_has_calculated_field(datasource, "nonexistent")

    def test_assert_datasource_has_filter_with_expression_success(self) -> None:
        """条件式によるフィルタ存在確認テスト（成功）."""
        group_filter = GroupFilterModel(expression="[test_field] = 'test'")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[datasource_filter]
        )

        result = assert_datasource_has_filter_with_expression(datasource, "=")
        assert result is not None
        assert result.field == "[test_field]"

    def test_assert_datasource_has_filter_with_expression_failure(self) -> None:
        """条件式によるフィルタ存在確認テスト（失敗）."""
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[]
        )

        with pytest.raises(AssertionError):
            assert_datasource_has_filter_with_expression(datasource, "nonexistent")

    def test_assert_datasource_has_filter_with_member_success(self) -> None:
        """メンバー名によるフィルタ存在確認テスト（成功）."""
        group_filter = GroupFilterModel(member="test_member")
        datasource_filter = DataSourceFilterModel(field="[test_field]", group_filter=group_filter)
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[datasource_filter]
        )

        result = assert_datasource_has_filter_with_member(datasource, "test_member")
        assert result is not None
        assert result.field == "[test_field]"

    def test_assert_datasource_has_filter_with_member_failure(self) -> None:
        """メンバー名によるフィルタ存在確認テスト（失敗）."""
        datasource = DatasourceModel(
            name="test_ds", caption="Test DS", fields=[], datasource_filters=[]
        )

        with pytest.raises(AssertionError):
            assert_datasource_has_filter_with_member(datasource, "nonexistent")

    def test_assert_sheet_has_field_in_columns_success(self) -> None:
        """ワークシートの列にフィールドが含まれるテスト（成功）."""
        worksheet = WorksheetModel(
            name="test_sheet", datasource_name="test_ds", columns=["[test_field]"]
        )

        # この関数は戻り値がないため、例外が発生しないことを確認
        assert_sheet_has_field_in_columns(worksheet, "test_field")

    def test_assert_sheet_has_field_in_columns_failure(self) -> None:
        """ワークシートの列にフィールドが含まれるテスト（失敗）."""
        worksheet = WorksheetModel(
            name="test_sheet", datasource_name="test_ds", columns=["[other_field]"]
        )

        with pytest.raises(AssertionError):
            assert_sheet_has_field_in_columns(worksheet, "test_field")

    def test_assert_sheet_has_field_in_rows_success(self) -> None:
        """ワークシートの行にフィールドが含まれるテスト（成功）."""
        worksheet = WorksheetModel(
            name="test_sheet", datasource_name="test_ds", rows=["[test_field]"]
        )

        # この関数は戻り値がないため、例外が発生しないことを確認
        assert_sheet_has_field_in_rows(worksheet, "test_field")

    def test_assert_sheet_has_field_in_rows_failure(self) -> None:
        """ワークシートの行にフィールドが含まれるテスト（失敗）."""
        worksheet = WorksheetModel(
            name="test_sheet", datasource_name="test_ds", rows=["[other_field]"]
        )

        with pytest.raises(AssertionError):
            assert_sheet_has_field_in_rows(worksheet, "test_field")
