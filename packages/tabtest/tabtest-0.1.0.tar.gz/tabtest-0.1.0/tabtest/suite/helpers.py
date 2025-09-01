"""
tabtestのヘルパー関数.

Tableauワークブックのテストを簡単にするためのアサーション関数を提供します.
"""

from typing import List

from tabtest.models import (
    CalculatedFieldModel,
    DashboardModel,
    DataSourceFilterModel,
    DatasourceModel,
    ParameterModel,
    SetModel,
    WorkbookModel,
    WorksheetModel,
)


def assert_workbook_has_datasource(
    workbook: WorkbookModel, datasource_name: str
) -> DatasourceModel:
    """
    ワークブックに指定したデータソースが存在することをアサート.

    Args:
        workbook: ワークブック.
        datasource_name: データソース名またはキャプション名.

    Returns:
        データソースモデル.

    Raises:
        AssertionError: データソースが見つからない場合.

    """
    # まず名前で検索
    datasource = workbook.get_datasource(datasource_name)
    if datasource is not None:
        return datasource

    # 名前で見つからない場合はキャプションで検索
    datasource = workbook.get_datasource_by_caption(datasource_name)
    assert datasource is not None, (
        f"データソース '{datasource_name}' が見つかりません（名前またはキャプションで検索）"
    )
    return datasource


def assert_workbook_has_sheet(workbook: WorkbookModel, sheet_name: str) -> WorksheetModel:
    """
    ワークブックに指定したワークシートが存在することをアサート.

    Args:
        workbook: ワークブック.
        sheet_name: ワークシート名.

    Returns:
        ワークシートモデル.

    Raises:
        AssertionError: ワークシートが見つからない場合.

    """
    sheet = workbook.get_sheet(sheet_name)
    assert sheet is not None, f"ワークシート '{sheet_name}' が見つかりません"
    return sheet


def assert_workbook_has_dashboard(workbook: WorkbookModel, dashboard_name: str) -> DashboardModel:
    """
    ワークブックに指定したダッシュボードが存在することをアサート.

    Args:
        workbook: ワークブック.
        dashboard_name: ダッシュボード名.

    Returns:
        ダッシュボードモデル.

    Raises:
        AssertionError: ダッシュボードが見つからない場合.

    """
    dashboard = workbook.get_dashboard(dashboard_name)
    assert dashboard is not None, f"ダッシュボード '{dashboard_name}' が見つかりません"
    return dashboard


def assert_datasource_has_calculated_field(
    datasource: DatasourceModel, calculated_field_name: str
) -> CalculatedFieldModel:
    """
    データソースに指定した計算フィールドが存在することをアサート.

    Args:
        datasource: データソース.
        calculated_field_name: 計算フィールド名.

    Returns:
        計算フィールドモデル.

    Raises:
        AssertionError: 計算フィールドが見つからない場合.

    """
    calculated_field = datasource.get_calculated_field(calculated_field_name)
    assert calculated_field is not None, (
        f"データソース '{datasource.name}' に計算フィールド "
        f"'{calculated_field_name}' が見つかりません"
    )
    return calculated_field


def assert_workbook_has_parameter(workbook: WorkbookModel, parameter_name: str) -> ParameterModel:
    """
    ワークブックに指定したパラメータが存在することをアサート.

    Args:
        workbook: ワークブック.
        parameter_name: パラメータ名.

    Returns:
        パラメータモデル.

    Raises:
        AssertionError: パラメータが見つからない場合.

    """
    parameter = workbook.get_parameter(parameter_name)
    assert parameter is not None, f"パラメータ '{parameter_name}' が見つかりません"
    return parameter


def assert_datasource_has_set(datasource: DatasourceModel, set_name: str) -> SetModel:
    """
    データソースに指定したセットが存在することをアサート.

    Args:
        datasource: データソース.
        set_name: セット名.

    Returns:
        セットモデル.

    Raises:
        AssertionError: セットが見つからない場合.

    """
    set_obj = datasource.get_set(set_name)
    assert set_obj is not None, (
        f"データソース '{datasource.name}' にセット '{set_name}' が見つかりません"
    )
    return set_obj


def assert_workbook_has_set(workbook: WorkbookModel, set_name: str) -> SetModel:
    """
    ワークブックに指定したセットが存在することをアサート.

    Args:
        workbook: ワークブック.
        set_name: セット名.

    Returns:
        セットモデル.

    Raises:
        AssertionError: セットが見つからない場合.

    """
    set_obj = workbook.get_set(set_name)
    assert set_obj is not None, f"セット '{set_name}' が見つかりません"
    return set_obj


def assert_workbook_has_calculated_field(
    workbook: WorkbookModel, calculated_field_name: str
) -> CalculatedFieldModel:
    """
    ワークブックに指定した計算フィールドが存在することをアサート.

    Args:
        workbook: ワークブック.
        calculated_field_name: 計算フィールド名.

    Returns:
        計算フィールドモデル.

    Raises:
        AssertionError: 計算フィールドが見つからない場合.

    """
    calculated_field = workbook.get_calculated_field(calculated_field_name)
    assert calculated_field is not None, (
        f"計算フィールド '{calculated_field_name}' が見つかりません"
    )
    return calculated_field


def assert_sheet_has_field_in_rows(sheet: WorksheetModel, field_name: str) -> None:
    """
    ワークシートの行に指定したフィールドが配置されていることをアサート.

    Args:
        sheet: ワークシート.
        field_name: フィールド名.

    Raises:
        AssertionError: フィールドが行に配置されていない場合.

    """
    assert sheet.has_field_in_rows(field_name), (
        f"フィールド '{field_name}' が行に配置されていません"
    )


def assert_sheet_has_field_in_columns(sheet: WorksheetModel, field_name: str) -> None:
    """
    ワークシートの列に指定したフィールドが配置されていることをアサート.

    Args:
        sheet: ワークシート.
        field_name: フィールド名.

    Raises:
        AssertionError: フィールドが列に配置されていない場合.

    """
    assert sheet.has_field_in_columns(field_name), (
        f"フィールド '{field_name}' が列に配置されていません"
    )


def assert_sheet_has_filter(sheet: WorksheetModel, field_name: str) -> None:
    """
    ワークシートに指定したフィールドのフィルターが設定されていることをアサート.

    Args:
        sheet: ワークシート.
        field_name: フィールド名.

    Raises:
        AssertionError: フィルターが設定されていない場合.

    """
    assert sheet.has_filter(field_name), (
        f"フィールド '{field_name}' にフィルターが設定されていません"
    )


def assert_dashboard_contains_sheet(dashboard: DashboardModel, sheet_name: str) -> None:
    """
    ダッシュボードに指定したワークシートが含まれていることをアサート.

    Args:
        dashboard: ダッシュボード.
        sheet_name: ワークシート名.

    Raises:
        AssertionError: ワークシートが含まれていない場合.

    """
    assert dashboard.contains_sheet(sheet_name), (
        f"ダッシュボードにワークシート '{sheet_name}' が含まれていません"
    )


def assert_worksheet_has_title(sheet: WorksheetModel, title: str) -> None:
    """
    ワークシートに指定したタイトルが設定されていることをアサート.

    Args:
        sheet: ワークシート.
        title: タイトル.

    Raises:
        AssertionError: タイトルが設定されていない場合.

    """
    assert sheet.title == title, (
        f"ワークシートのタイトルが '{title}' ではありません（実際: {sheet.title}）"
    )


def assert_worksheet_has_mark_type(sheet: WorksheetModel, mark_type: str) -> None:
    """
    ワークシートに指定したマークタイプが設定されていることをアサート.

    Args:
        sheet: ワークシート.
        mark_type: マークタイプ.

    Raises:
        AssertionError: マークタイプが設定されていない場合.

    """
    assert sheet.mark_type == mark_type, (
        f"ワークシートのマークタイプが '{mark_type}' ではありません（実際: {sheet.mark_type}）"
    )


def assert_dashboard_has_size(dashboard: DashboardModel, width: int, height: int) -> None:
    """
    ダッシュボードに指定したサイズが設定されていることをアサート.

    Args:
        dashboard: ダッシュボード.
        width: 幅.
        height: 高さ.

    Raises:
        AssertionError: サイズが設定されていない場合.

    """
    assert dashboard.size_width == width, (
        f"ダッシュボードの幅が {width} ではありません（実際: {dashboard.size_width}）"
    )
    assert dashboard.size_height == height, (
        f"ダッシュボードの高さが {height} ではありません（実際: {dashboard.size_height}）"
    )


def assert_parameter_has_default_value(parameter: ParameterModel, default_value: str) -> None:
    """
    パラメータに指定したデフォルト値が設定されていることをアサート.

    Args:
        parameter: パラメータ.
        default_value: デフォルト値.

    Raises:
        AssertionError: デフォルト値が設定されていない場合.

    """
    assert parameter.default_value == default_value, (
        f"パラメータのデフォルト値が '{default_value}' ではありません"
        f"（実際: {parameter.default_value}）"
    )


def assert_set_has_members(set_obj: SetModel, members: List[str]) -> None:
    """
    セットに指定したメンバーが含まれていることをアサート.

    Args:
        set_obj: セット.
        members: メンバー一覧.

    Raises:
        AssertionError: メンバーが含まれていない場合.

    """
    for member in members:
        assert member in set_obj.members, (
            f"セット '{set_obj.name}' にメンバー '{member}' が含まれていません"
        )


def assert_datasource_has_filter_with_expression(
    datasource: DatasourceModel, expression: str
) -> DataSourceFilterModel:
    """
    データソースに指定した条件式を含むフィルタが存在することをアサート.

    Args:
        datasource: データソース.
        expression: 検索する条件式.

    Returns:
        データソースフィルタモデル.

    Raises:
        AssertionError: 条件式を含むフィルタが見つからない場合.

    """
    filters_with_expression = datasource.get_datasource_filters_with_expression(expression)
    assert len(filters_with_expression) > 0, (
        f"データソース '{datasource.name}' に条件式 '{expression}' を含むフィルタが見つかりません"
    )
    return filters_with_expression[0]


def assert_datasource_has_filter_with_member(
    datasource: DatasourceModel, member: str
) -> DataSourceFilterModel:
    """
    データソースに指定したメンバー名を含むフィルタが存在することをアサート.

    Args:
        datasource: データソース.
        member: 検索するメンバー名.

    Returns:
        データソースフィルタモデル.

    Raises:
        AssertionError: メンバー名を含むフィルタが見つからない場合.

    """
    filters_with_member = datasource.get_datasource_filters_with_member(member)
    assert len(filters_with_member) > 0, (
        f"データソース '{datasource.name}' にメンバー名 '{member}' を含むフィルタが見つかりません"
    )
    return filters_with_member[0]


def assert_calculated_field_has_formula(
    calculated_field: CalculatedFieldModel, formula: str
) -> None:
    """
    計算フィールドに指定した計算式が設定されていることをアサート.

    Args:
        calculated_field: 計算フィールド.
        formula: 計算式.

    Raises:
        AssertionError: 計算式が設定されていない場合.

    """
    assert calculated_field.formula == formula, (
        f"計算フィールドの計算式が '{formula}' ではありません（実際: {calculated_field.formula}）"
    )
