"""データソース関連のモデル."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .calculated_fields import CalculatedFieldModel
from .filters import DataSourceFilterModel
from .sets import SetModel


class DatasourceFieldModel(BaseModel):
    """データソースフィールド情報."""

    name: str = Field(description="フィールド名")
    datatype: Optional[str] = Field(None, description="データ型")
    role: Optional[str] = Field(None, description="役割（dimension/measure）")
    type: Optional[str] = Field(None, description="型（nominal/ordinal/quantitative）")
    caption: Optional[str] = Field(None, description="キャプション")
    formula: Optional[str] = Field(None, description="計算式")
    alias: Optional[str] = Field(None, description="別名")
    description: Optional[str] = Field(None, description="説明")
    is_calculated: bool = Field(False, description="計算フィールドかどうか")
    is_parameter: bool = Field(False, description="パラメータかどうか")
    is_set: bool = Field(False, description="セットかどうか")


class DatasourceModel(BaseModel):
    """データソース情報."""

    name: Optional[str] = Field(None, description="データソース名")
    caption: Optional[str] = Field(None, description="キャプション")
    fields: List[DatasourceFieldModel] = Field(default_factory=list, description="フィールド一覧")
    calculated_fields: List[CalculatedFieldModel] = Field(
        default_factory=list, description="計算フィールド一覧"
    )
    sets: List[SetModel] = Field(default_factory=list, description="セット一覧")
    datasource_filters: List[DataSourceFilterModel] = Field(
        default_factory=list, description="データソースフィルタ一覧"
    )
    connection_type: Optional[str] = Field(None, description="接続タイプ")
    server: Optional[str] = Field(None, description="サーバー名")
    database: Optional[str] = Field(None, description="データベース名")
    schema_name: Optional[str] = Field(None, description="スキーマ名")
    table: Optional[str] = Field(None, description="テーブル名")
    query: Optional[str] = Field(None, description="クエリ")

    def get_field(self, field_name: str) -> Optional[DatasourceFieldModel]:
        """指定した名前のフィールドを取得."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None

    def get_calculated_field(self, name: str) -> Optional[CalculatedFieldModel]:
        """指定した名前の計算フィールドを取得."""
        for calc_field in self.calculated_fields:
            if calc_field.name == name:
                return calc_field
        return None

    def get_set(self, name: str) -> Optional[SetModel]:
        """指定した名前のセットを取得."""
        for set_obj in self.sets:
            if set_obj.name == name:
                return set_obj
        return None

    def has_calculated_field(self, name: str) -> bool:
        """指定した名前の計算フィールドが存在するかチェック."""
        return self.get_calculated_field(name) is not None

    def has_set(self, name: str) -> bool:
        """指定した名前のセットが存在するかチェック."""
        return self.get_set(name) is not None

    def get_all_calculated_fields(self) -> List[CalculatedFieldModel]:
        """すべての計算フィールドを取得（フィールド内と計算フィールドリストの両方）."""
        result = []

        # 計算フィールドリスト
        result.extend(self.calculated_fields)

        # フィールド内の計算フィールド
        for field in self.fields:
            if field.is_calculated and field.formula:
                result.append(
                    CalculatedFieldModel(
                        name=field.name,
                        caption=field.caption,
                        datatype=field.datatype,
                        role=field.role,
                        type=field.type,
                        formula=field.formula,
                    )
                )

        return result

    def get_datasource_filter(self, field_name: str) -> Optional[DataSourceFilterModel]:
        """指定したフィールド名のデータソースフィルタを取得."""
        for filter_obj in self.datasource_filters:
            if filter_obj.field == field_name:
                return filter_obj
        return None

    def has_datasource_filter(self, field_name: str) -> bool:
        """指定したフィールド名のデータソースフィルタが存在するかチェック."""
        return self.get_datasource_filter(field_name) is not None

    def get_datasource_filters_with_expression(
        self, expression: str
    ) -> List[DataSourceFilterModel]:
        """指定した条件式を含むデータソースフィルタを取得."""
        result = []
        for filter_obj in self.datasource_filters:
            if filter_obj.has_expression(expression):
                result.append(filter_obj)
        return result

    def get_datasource_filters_with_member(self, member: str) -> List[DataSourceFilterModel]:
        """指定したメンバー名を含むデータソースフィルタを取得."""
        result = []
        for filter_obj in self.datasource_filters:
            if filter_obj.has_member(member):
                result.append(filter_obj)
        return result

    def resolve_calculation_references(self, formula: str) -> str:
        """計算フィールドの参照をキャプションに置き換える."""
        if not formula:
            return formula

        resolved_formula = formula

        # データソース内の全ての計算フィールドを取得
        all_calculated_fields = self.get_all_calculated_fields()

        # 計算フィールドの名前とキャプションのマッピングを作成
        calculation_mapping = {}
        for field in all_calculated_fields:
            if field.name and field.caption:
                calculation_mapping[field.name] = field.caption

        # 各計算フィールドの参照を置き換え
        for calc_name, caption in calculation_mapping.items():
            # [Calculation_xxx] 形式の参照を置き換え
            pattern = f"[{calc_name}]"
            if pattern in resolved_formula:
                resolved_formula = resolved_formula.replace(pattern, f"[{caption}]")

        return resolved_formula

    def get_resolved_formula(self, field_name: str) -> Optional[str]:
        """指定したフィールドの計算フィールド参照を解決した計算式を取得."""
        field = self.get_field(field_name)
        if not field or not field.formula:
            return None

        return self.resolve_calculation_references(field.formula)
