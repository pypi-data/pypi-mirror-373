"""ダッシュボード関連のモデル."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .formatting import FormattingModel


class DashboardZoneModel(BaseModel):
    """ダッシュボードのゾーン情報."""

    id: str
    type: Optional[str] = Field(None, description="ゾーンのタイプ")
    x: Optional[int] = Field(None, description="X座標")
    y: Optional[int] = Field(None, description="Y座標")
    width: Optional[int] = Field(None, description="幅")
    height: Optional[int] = Field(None, description="高さ")
    name: Optional[str] = Field(None, description="ゾーン名")
    alt_text: Optional[str] = Field(None, description="代替テキスト")
    image_path: Optional[str] = Field(None, description="画像パス")
    action: Optional[str] = Field(None, description="アクション")
    children: List["DashboardZoneModel"] = Field(default_factory=list, description="子ゾーン")
    formatting: Optional[FormattingModel] = Field(None, description="書式設定")


class DashboardSheetModel(BaseModel):
    """ダッシュボード内のワークシート情報."""

    sheet_name: str = Field(description="ワークシート名")
    x: int = Field(description="X座標")
    y: int = Field(description="Y座標")
    width: int = Field(description="幅")
    height: int = Field(description="高さ")
    title: Optional[str] = Field(None, description="タイトル")
    show_title: bool = Field(True, description="タイトルを表示するか")
    formatting: Optional[FormattingModel] = Field(None, description="書式設定")
    is_worksheet: bool = Field(True, description="ワークシートかどうか")


class DashboardObjectModel(BaseModel):
    """ダッシュボードオブジェクト情報."""

    id: str = Field(description="オブジェクトID")
    type: str = Field(description="オブジェクトタイプ")
    name: Optional[str] = Field(None, description="オブジェクト名")
    x: int = Field(description="X座標")
    y: int = Field(description="Y座標")
    width: int = Field(description="幅")
    height: int = Field(description="高さ")
    content: Optional[str] = Field(None, description="コンテンツ")
    formatting: Optional[FormattingModel] = Field(None, description="書式設定")
    properties: Dict[str, Any] = Field(default_factory=dict, description="プロパティ")


class DashboardActionModel(BaseModel):
    """ダッシュボードアクション情報."""

    name: str = Field(description="アクション名")
    action_type: str = Field(description="アクションタイプ")
    source_sheet: Optional[str] = Field(None, description="ソースシート")
    target_sheet: Optional[str] = Field(None, description="ターゲットシート")
    source_field: Optional[str] = Field(None, description="ソースフィールド")
    target_field: Optional[str] = Field(None, description="ターゲットフィールド")
    enabled: bool = Field(True, description="有効かどうか")


class DashboardModel(BaseModel):
    """ダッシュボード情報."""

    name: Optional[str] = Field(None, description="ダッシュボード名")
    dashboard_sheets: List[DashboardSheetModel] = Field(
        default_factory=list, description="ダッシュボード内のワークシート"
    )
    objects: List[DashboardObjectModel] = Field(
        default_factory=list, description="オブジェクト一覧"
    )
    actions: List[DashboardActionModel] = Field(default_factory=list, description="アクション一覧")
    layout: Optional[Dict[str, Any]] = Field(None, description="レイアウト情報")
    size_width: int = Field(0, description="ダッシュボード幅")
    size_height: int = Field(0, description="ダッシュボード高さ")
    zones: List[DashboardZoneModel] = Field(default_factory=list, description="ゾーン一覧")
    title: Optional[str] = Field(None, description="タイトル")
    subtitle: Optional[str] = Field(None, description="サブタイトル")
    show_title: bool = Field(True, description="タイトルを表示するか")
    show_subtitle: bool = Field(True, description="サブタイトルを表示するか")
    formatting: Optional[FormattingModel] = Field(None, description="書式設定")

    def contains_sheet(self, sheet_name: str) -> bool:
        """指定したワークシートがダッシュボードに含まれているかチェック."""
        return any(sheet.sheet_name == sheet_name for sheet in self.dashboard_sheets)

    def get_sheet(self, sheet_name: str) -> Optional[DashboardSheetModel]:
        """指定したワークシート名でワークシートを取得."""
        for sheet in self.dashboard_sheets:
            if sheet.sheet_name == sheet_name:
                return sheet
        return None

    def get_worksheet_count(self) -> int:
        """ダッシュボード内のワークシート数を取得."""
        return len([sheet for sheet in self.dashboard_sheets if sheet.is_worksheet])

    def get_object(self, object_name: str) -> Optional[DashboardObjectModel]:
        """指定したIDのオブジェクトを取得."""
        for obj in self.objects:
            if obj.name == object_name:
                return obj
        return None
