"""ワークシート関連のモデル."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .formatting import FormattingModel


class FilterModel(BaseModel):
    """フィルター情報."""

    name: str = Field(description="フィルター名")
    field: str = Field(description="フィルター対象フィールド")
    default_value: Optional[str] = Field(None, description="デフォルト値")
    apply_mode: Optional[str] = Field(None, description="適用モード")
    allow_all_values: bool = Field(False, description="全値を許可するか")
    filter_type: Optional[str] = Field(None, description="フィルタータイプ")
    values: List[str] = Field(default_factory=list, description="フィルター値")
    range_start: Optional[str] = Field(None, description="範囲開始値")
    range_end: Optional[str] = Field(None, description="範囲終了値")


class WorksheetModel(BaseModel):
    """ワークシート情報."""

    name: str = Field(description="ワークシート名")
    datasource_name: str = Field(description="データソース名")
    filters: List[FilterModel] = Field(default_factory=list, description="フィルター一覧")
    rows: List[str] = Field(default_factory=list, description="行に配置されたフィールド")
    columns: List[str] = Field(default_factory=list, description="列に配置されたフィールド")
    mark_type: Optional[str] = Field(None, description="マークタイプ")
    mark_color: Optional[str] = Field(None, description="マーク色")
    mark_size: Optional[str] = Field(None, description="マークサイズ")
    mark_shape: Optional[str] = Field(None, description="マーク形状")
    mark_label: Optional[str] = Field(None, description="マークラベル")
    mark_tooltip: Optional[str] = Field(None, description="マークツールチップ")
    formatting: Optional[FormattingModel] = Field(None, description="書式設定")
    title: Optional[str] = Field(None, description="タイトル")
    subtitle: Optional[str] = Field(None, description="サブタイトル")
    caption: Optional[str] = Field(None, description="キャプション")
    show_title: bool = Field(True, description="タイトルを表示するか")
    show_subtitle: bool = Field(True, description="サブタイトルを表示するか")
    show_caption: bool = Field(True, description="キャプションを表示するか")

    def has_field_in_rows(self, field_name: str) -> bool:
        """指定したフィールドが行に配置されているかチェック."""
        return any(field_name in row for row in self.rows)

    def has_field_in_columns(self, field_name: str) -> bool:
        """指定したフィールドが列に配置されているかチェック."""
        return any(field_name in col for col in self.columns)

    def has_filter(self, field_name: str) -> bool:
        """指定したフィールドにフィルターが設定されているかチェック."""
        return any(field_name in filter.field for filter in self.filters)
