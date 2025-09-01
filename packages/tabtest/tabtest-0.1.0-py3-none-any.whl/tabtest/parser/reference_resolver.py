from tabtest.models import DatasourceModel, WorkbookModel, WorksheetModel


class ReferenceResolver:
    """計算フィールドとパラメータの参照解決を担当するクラス."""

    @staticmethod
    def resolve_calculation_references_in_datasource(datasource_model: DatasourceModel) -> None:
        """データソース内の計算フィールド参照を解決."""
        # データソース内の全ての計算フィールドを取得
        all_calculated_fields = datasource_model.get_all_calculated_fields()

        # 計算フィールドの名前とキャプションのマッピングを作成
        calculation_mapping = {}
        for calc_field in all_calculated_fields:
            if calc_field.name and calc_field.caption:
                calculation_mapping[calc_field.name] = calc_field.caption

        # 各フィールドの計算式で計算フィールド参照を置き換え
        for datasource_field in datasource_model.fields:
            if datasource_field.formula:
                datasource_field.formula = (
                    ReferenceResolver._resolve_calculation_references_in_formula(
                        datasource_field.formula, calculation_mapping
                    )
                )

        # 計算フィールドリスト内の計算式でも計算フィールド参照を置き換え
        for calc_field in datasource_model.calculated_fields:
            if calc_field.formula:
                calc_field.formula = ReferenceResolver._resolve_calculation_references_in_formula(
                    calc_field.formula, calculation_mapping
                )

        # データソースフィルター内の計算フィールド参照も解決
        ReferenceResolver._resolve_calculation_references_in_datasource_filters(
            datasource_model, calculation_mapping
        )

    @staticmethod
    def resolve_calculation_references_in_worksheet(
        worksheet_model: WorksheetModel, datasource_model: DatasourceModel
    ) -> None:
        """ワークシート内の計算フィールド参照を解決."""
        # データソース内の全ての計算フィールドを取得
        all_calculated_fields = datasource_model.get_all_calculated_fields()

        # 計算フィールドの名前とキャプションのマッピングを作成
        calculation_mapping = {}
        for calc_field in all_calculated_fields:
            if calc_field.name and calc_field.caption:
                calculation_mapping[calc_field.name] = calc_field.caption

        # フィルター内の計算フィールド参照を解決
        for filter_obj in worksheet_model.filters:
            if filter_obj.field:
                filter_obj.field = (
                    ReferenceResolver._resolve_calculation_references_in_filter_field(
                        filter_obj.field, calculation_mapping
                    )
                )

        # rows内の計算フィールド参照を解決
        for i, row in enumerate(worksheet_model.rows):
            worksheet_model.rows[i] = (
                ReferenceResolver._resolve_calculation_references_in_filter_field(
                    row, calculation_mapping
                )
            )

        # columns内の計算フィールド参照を解決
        for i, col in enumerate(worksheet_model.columns):
            worksheet_model.columns[i] = (
                ReferenceResolver._resolve_calculation_references_in_filter_field(
                    col, calculation_mapping
                )
            )

    @staticmethod
    def resolve_parameter_references_in_workbook(workbook: WorkbookModel) -> None:
        """ワークブック全体のパラメータ参照を解決."""
        # パラメータマッピングを作成
        parameter_mapping = {}
        for param in workbook.parameters:
            if param.name and param.caption:
                parameter_mapping[param.name] = param.caption

        # 各データソースのパラメータ参照を解決
        for datasource in workbook.datasources:
            ReferenceResolver._resolve_parameter_references_in_datasource(
                datasource, parameter_mapping
            )

    @staticmethod
    def _resolve_calculation_references_in_formula(
        formula: str, calculation_mapping: dict[str, str]
    ) -> str:
        """計算式内の計算フィールド参照を解決."""
        if not formula:
            return formula

        resolved_formula = formula

        # [Calculation_xxx] 形式の参照を置き換え
        for calc_name, caption in calculation_mapping.items():
            # パターン1: [Calculation_xxx]
            pattern = f"[{calc_name}]"
            if pattern in resolved_formula:
                resolved_formula = resolved_formula.replace(pattern, f"[{caption}]")

            # パターン2: [none:Calculation_xxx:nk] 形式
            clean_calc_name = calc_name.strip("[]")
            pattern_with_none = f"[none:{clean_calc_name}:nk]"
            if pattern_with_none in resolved_formula:
                resolved_formula = resolved_formula.replace(pattern_with_none, f"[{caption}]")

            # パターン3: Calculation_xxx 形式の参照も置き換え（角括弧なし）
            pattern_without_brackets = calc_name
            if pattern_without_brackets in resolved_formula:
                resolved_formula = resolved_formula.replace(pattern_without_brackets, caption)

        return resolved_formula

    @staticmethod
    def _resolve_calculation_references_in_datasource_filters(
        datasource_model: DatasourceModel, calculation_mapping: dict[str, str]
    ) -> None:
        """データソースフィルター内の計算フィールド参照を解決."""
        for filter_obj in datasource_model.datasource_filters:
            if filter_obj.field:
                filter_obj.field = (
                    ReferenceResolver._resolve_calculation_references_in_filter_field(
                        filter_obj.field, calculation_mapping
                    )
                )

            if filter_obj.group_filter and filter_obj.group_filter.level:
                filter_obj.group_filter.level = (
                    ReferenceResolver._resolve_calculation_references_in_filter_field(
                        filter_obj.group_filter.level, calculation_mapping
                    )
                )

    @staticmethod
    def _resolve_calculation_references_in_filter_field(
        field_value: str, calculation_mapping: dict[str, str]
    ) -> str:
        """フィルターフィールド内の計算フィールド参照を解決."""
        if not field_value:
            return field_value

        resolved_field = field_value

        # [Calculation_xxx] 形式の参照を置き換え
        for calc_name, caption in calculation_mapping.items():
            # パターン1: [Calculation_xxx]
            pattern = f"[{calc_name}]"
            if pattern in resolved_field:
                resolved_field = resolved_field.replace(pattern, f"[{caption}]")

            # パターン2: [none:Calculation_xxx:nk] 形式
            clean_calc_name = calc_name.strip("[]")
            pattern_with_none = f"[none:{clean_calc_name}:nk]"
            if pattern_with_none in resolved_field:
                resolved_field = resolved_field.replace(pattern_with_none, f"[{caption}]")

            # パターン3: Calculation_xxx 形式の参照も置き換え（角括弧なし）
            pattern_without_brackets = calc_name
            if pattern_without_brackets in resolved_field:
                resolved_field = resolved_field.replace(pattern_without_brackets, caption)

        return resolved_field

    @staticmethod
    def _resolve_parameter_references_in_datasource(
        datasource_model: DatasourceModel, parameter_mapping: dict[str, str]
    ) -> None:
        """データソース内のパラメータ参照を解決."""
        # 各フィールドの計算式でパラメータ参照を置き換え
        for field in datasource_model.fields:
            if field.formula:
                field.formula = ReferenceResolver._resolve_parameter_references_in_formula(
                    field.formula, parameter_mapping
                )

        # 計算フィールドリスト内の計算式でもパラメータ参照を置き換え
        for calc_field in datasource_model.calculated_fields:
            if calc_field.formula:
                calc_field.formula = ReferenceResolver._resolve_parameter_references_in_formula(
                    calc_field.formula, parameter_mapping
                )

    @staticmethod
    def _resolve_parameter_references_in_formula(
        formula: str, parameter_mapping: dict[str, str]
    ) -> str:
        """計算式内のパラメータ参照を解決."""
        if not formula:
            return formula

        resolved_formula = formula

        # [Parameters].[パラメータ名] 形式の参照を置き換え
        for param_name, caption in parameter_mapping.items():
            # パラメータ名から角括弧を除去
            clean_param_name = param_name.strip("[]")
            pattern = f"[Parameters].[{clean_param_name}]"
            if pattern in resolved_formula:
                resolved_formula = resolved_formula.replace(pattern, f"[Parameter].[{caption}]")

        return resolved_formula
