import html
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional

from tabtest.models import (
    CalculatedFieldModel,
    DatasourceFieldModel,
    DataSourceFilterModel,
    DatasourceModel,
    GroupFilterModel,
    ParameterModel,
    SetModel,
)

from .reference_resolver import ReferenceResolver


class DatasourceParser:
    """データソース関連の解析を担当するクラス."""

    @staticmethod
    def parse_datasource(ds_element: ET.Element) -> DatasourceModel:
        """データソース要素を解析してDatasourceModelを作成."""
        ds_name = ds_element.get("name")
        ds_caption = ds_element.get("caption")

        # 接続情報を取得
        connection_elem = ds_element.find(".//connection")
        connection_type = connection_elem.get("class") if connection_elem is not None else None
        server = connection_elem.get("server") if connection_elem is not None else None
        database = connection_elem.get("dbname") if connection_elem is not None else None
        schema_name = connection_elem.get("schema") if connection_elem is not None else None
        table = connection_elem.get("table") if connection_elem is not None else None

        # クエリ情報を取得
        query_elem = ds_element.find(".//query")
        query = query_elem.text if query_elem is not None else None

        # フィールドを解析
        fields = DatasourceParser._parse_fields(ds_element)

        # データソース内の計算フィールドを解析
        calculated_fields = DatasourceParser._parse_calculated_fields(ds_element)

        # データソース内のセットを解析
        sets = DatasourceParser._parse_sets(ds_element)

        # データソース内のフィルタを解析
        datasource_filters = DatasourceParser._parse_datasource_filters(ds_element)

        datasource_model = DatasourceModel(
            name=ds_name,
            caption=ds_caption,
            fields=fields,
            calculated_fields=calculated_fields,
            sets=sets,
            datasource_filters=datasource_filters,
            connection_type=connection_type,
            server=server,
            database=database,
            schema_name=schema_name,
            table=table,
            query=query,
        )

        # 計算フィールドの参照を解決
        ReferenceResolver.resolve_calculation_references_in_datasource(datasource_model)

        return datasource_model

    @staticmethod
    def parse_parameter(param_element: ET.Element) -> Optional[ParameterModel]:
        """パラメータ要素を解析してParameterModelを作成."""
        if param_element.get("param-domain-type") is None:
            return None

        param_name = param_element.get("name", "")
        param_caption = param_element.get("caption")
        param_type = param_element.get("param-domain-type")
        param_datatype = param_element.get("datatype")
        param_role = param_element.get("role")

        # デフォルト値を取得
        default_value = param_element.get("value")

        # パラメータの詳細情報を取得
        param_info = param_element.find(".//param")
        if param_info is not None:
            param_type = param_info.get("param-domain-type", param_type)
            param_datatype = param_info.get("datatype", param_datatype)

        return ParameterModel(
            name=param_name,
            caption=param_caption,
            param_domain_type=param_type,
            datatype=param_datatype,
            default_value=default_value,
            role=param_role,
        )

    @staticmethod
    def _parse_fields(ds_element: ET.Element) -> list[DatasourceFieldModel]:
        """データソース内のフィールドを解析."""
        fields = []
        for col_element in ds_element.findall("./column"):
            calc_element = col_element.find("./calculation")
            formula = calc_element.get("formula") if calc_element is not None else None

            # フィールドの詳細情報を取得
            is_calculated = formula is not None
            is_parameter = col_element.get("param-domain-type") is not None
            is_set = col_element.get("set-domain-type") is not None

            field = DatasourceFieldModel(
                name=col_element.get("name", ""),
                datatype=col_element.get("datatype"),
                role=col_element.get("role"),
                type=col_element.get("type"),
                caption=col_element.get("caption"),
                formula=formula,
                alias=col_element.get("alias"),
                description=col_element.get("description"),
                is_calculated=is_calculated,
                is_parameter=is_parameter,
                is_set=is_set,
            )
            fields.append(field)

        return fields

    @staticmethod
    def _parse_calculated_fields(ds_element: ET.Element) -> list[CalculatedFieldModel]:
        """データソース内の計算フィールドを解析."""
        calculated_fields = []
        # calculation要素を検索
        for calc_element in ds_element.findall(".//calculation"):
            calc_model = DatasourceParser._parse_calculated_field(calc_element)
            if calc_model:
                calculated_fields.append(calc_model)

        # column要素から計算フィールドを検出
        for col_element in ds_element.findall("./column"):
            if col_element.get("formula") is not None:
                calc_model = DatasourceParser._parse_calculated_field_from_column(col_element)
                if calc_model:
                    calculated_fields.append(calc_model)

        return calculated_fields

    @staticmethod
    def _parse_sets(ds_element: ET.Element) -> list[SetModel]:
        """データソース内のセットを解析."""
        sets = []
        # column要素からセットを検出
        for col_element in ds_element.findall("./column"):
            if col_element.get("set-domain-type") is not None:
                set_model = DatasourceParser._parse_set_from_column(col_element)
                if set_model:
                    sets.append(set_model)

        return sets

    @staticmethod
    def _parse_datasource_filters(ds_element: ET.Element) -> list[DataSourceFilterModel]:
        """データソース内のフィルタを解析."""
        datasource_filters = []
        # データソースフィルタは通常のフィルタとは異なる場所にある可能性がある
        for filter_elem in ds_element.findall(".//filter"):
            filter_model = DatasourceParser._parse_datasource_filter(filter_elem)
            if filter_model:
                datasource_filters.append(filter_model)

        # groupfilter要素も直接検索
        for group_filter_elem in ds_element.findall(".//groupfilter"):
            filter_model = DatasourceParser._parse_group_filter(group_filter_elem)
            if filter_model:
                datasource_filters.append(filter_model)

        return datasource_filters

    @staticmethod
    def _parse_calculated_field(calc_element: ET.Element) -> Optional[CalculatedFieldModel]:
        """計算フィールド要素を解析してCalculatedFieldModelを作成."""
        if calc_element.get("formula") is None:
            return None

        name = calc_element.get("name")
        if name is None:
            return None

        formula = calc_element.get("formula", "")
        # エスケープ文字をデコード
        formula = html.unescape(formula)
        formula = urllib.parse.unquote(formula)

        return CalculatedFieldModel(
            name=name,
            role=calc_element.get("role"),
            type=calc_element.get("type"),
            caption=calc_element.get("caption"),
            formula=formula,
            datatype=calc_element.get("datatype"),
        )

    @staticmethod
    def _parse_calculated_field_from_column(
        col_element: ET.Element,
    ) -> Optional[CalculatedFieldModel]:
        """column要素から計算フィールドを解析してCalculatedFieldModelを作成."""
        formula = col_element.get("formula")
        if formula is None:
            return None

        name = col_element.get("name")
        if name is None:
            return None

        # エスケープ文字をデコード
        formula = html.unescape(formula)
        formula = urllib.parse.unquote(formula)

        return CalculatedFieldModel(
            name=name,
            role=col_element.get("role"),
            type=col_element.get("type"),
            caption=col_element.get("caption"),
            formula=formula,
            datatype=col_element.get("datatype"),
        )

    @staticmethod
    def _parse_set(set_element: ET.Element) -> Optional[SetModel]:
        """セット要素を解析してSetModelを作成."""
        if set_element.get("name") is None:
            return None

        return SetModel(
            name=set_element.get("name", ""),
            caption=set_element.get("caption"),
            field_name=set_element.get("name", ""),
            set_type=set_element.get("set-domain-type"),
            formula=set_element.get("formula"),
        )

    @staticmethod
    def _parse_set_from_column(col_element: ET.Element) -> Optional[SetModel]:
        """column要素からセットを解析してSetModelを作成."""
        if col_element.get("name") is None:
            return None

        return SetModel(
            name=col_element.get("name", ""),
            caption=col_element.get("caption"),
            field_name=col_element.get("name", ""),
            set_type=col_element.get("set-domain-type"),
            formula=col_element.get("formula"),
        )

    @staticmethod
    def _parse_datasource_filter(filter_elem: ET.Element) -> Optional[DataSourceFilterModel]:
        """データソースフィルタ要素を解析してDataSourceFilterModelを作成."""
        if filter_elem.get("field") is None:
            return None

        field = filter_elem.get("field", "")
        # エスケープ文字をデコード
        field = html.unescape(field)
        field = urllib.parse.unquote(field)

        # groupfilter要素を取得
        group_filter_elem = filter_elem.find(".//groupfilter")
        group_filter = None
        if group_filter_elem is not None:
            expression = group_filter_elem.get("expression")
            if expression:
                # エスケープ文字をデコード
                expression = html.unescape(expression)
                expression = urllib.parse.unquote(expression)

            group_filter = GroupFilterModel(
                expression=expression,
                function=group_filter_elem.get("function"),
                level=group_filter_elem.get("level"),
                member=group_filter_elem.get("member"),
                ui_enumeration=group_filter_elem.get("ui-enumeration"),
                ui_marker=group_filter_elem.get("ui-marker"),
                ui_domain=group_filter_elem.get("ui-domain"),
                ui_manual_selection=group_filter_elem.get("ui-manual-selection"),
                ui_manual_selection_all_when_empty=group_filter_elem.get(
                    "ui-manual-selection-all-when-empty"
                ),
            )

        return DataSourceFilterModel(
            name=filter_elem.get("name", ""),
            field=field,
            filter_class=filter_elem.get("class"),
            filter_group=filter_elem.get("group"),
            group_filter=group_filter,
        )

    @staticmethod
    def _parse_group_filter(group_filter_elem: ET.Element) -> Optional[DataSourceFilterModel]:
        """groupfilter要素を解析してDataSourceFilterModelを作成."""
        expression = group_filter_elem.get("expression")
        if not expression:
            return None

        # エスケープ文字をデコード
        expression = html.unescape(expression)
        expression = urllib.parse.unquote(expression)

        # expressionからfield名を抽出
        # 例: CONTAINS( [member_name] , '|'+USERNAME()+'|' ) から [member_name] を抽出
        field = ""
        if "[" in expression and "]" in expression:
            start = expression.find("[")
            end = expression.find("]", start)
            if start != -1 and end != -1:
                field = expression[start : end + 1]

        group_filter = GroupFilterModel(
            expression=expression,
            function=group_filter_elem.get("function"),
            level=group_filter_elem.get("level"),
            member=group_filter_elem.get("member"),
            ui_enumeration=group_filter_elem.get("ui-enumeration"),
            ui_marker=group_filter_elem.get("ui-marker"),
            ui_domain=group_filter_elem.get("ui-domain"),
            ui_manual_selection=group_filter_elem.get("ui-manual-selection"),
            ui_manual_selection_all_when_empty=group_filter_elem.get(
                "ui-manual-selection-all-when-empty"
            ),
        )

        # ui-marker='filter-by'を持つ要素は通常group='2'のような属性を持つ
        filter_group = group_filter_elem.get("group")
        if (
            not filter_group
            and group_filter_elem.get("{http://www.tableausoftware.com/xml/user}ui-marker")
            == "filter-by"
        ):
            filter_group = "2"  # デフォルト値

        return DataSourceFilterModel(
            name=group_filter_elem.get("name", ""),
            field=field,
            filter_class=group_filter_elem.get("class") or "categorical",  # デフォルト値を設定
            filter_group=filter_group,
            group_filter=group_filter,
        )
