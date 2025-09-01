import xml.etree.ElementTree as ET
from typing import Dict, Optional

from tabtest.models import (
    DashboardActionModel,
    DashboardModel,
    DashboardObjectModel,
    DashboardSheetModel,
    FormattingModel,
    WorksheetModel,
)


class DashboardParser:
    """ダッシュボード関連の解析を担当するクラス."""

    @staticmethod
    def parse_dashboard(
        db_element: ET.Element, worksheets: Dict[str, WorksheetModel]
    ) -> DashboardModel:
        """ダッシュボード要素を解析してDashboardModelを作成."""
        db_name = db_element.attrib.get("name")

        # サイズ情報を取得
        size_width, size_height = DashboardParser._parse_size(db_element)

        # ダッシュボードシートを解析
        dashboard_sheets = DashboardParser._parse_dashboard_sheets(db_element, worksheets)

        # オブジェクト情報を取得
        objects = DashboardParser._parse_objects(db_element)

        # アクション情報を取得
        actions = DashboardParser._parse_actions(db_element)

        # ダッシュボードのタイトル情報
        title, show_title = DashboardParser._parse_title(db_element)
        subtitle, show_subtitle = DashboardParser._parse_subtitle(db_element)

        return DashboardModel(
            name=db_name,
            dashboard_sheets=dashboard_sheets,
            objects=objects,
            actions=actions,
            layout=None,
            size_width=size_width,
            size_height=size_height,
            title=title,
            subtitle=subtitle,
            show_title=show_title,
            show_subtitle=show_subtitle,
            formatting=None,
        )

    @staticmethod
    def _parse_size(db_element: ET.Element) -> tuple[int, int]:
        """ダッシュボードのサイズ情報を解析."""
        size_elem = db_element.find(".//size")
        size_width = 0
        size_height = 0
        if size_elem is not None:
            # maxwidth/maxheightを優先し、なければwidth/heightを使用
            size_width = DashboardParser._safe_int(
                size_elem.attrib.get("maxwidth")
            ) or DashboardParser._safe_int(size_elem.attrib.get("width"))
            size_height = DashboardParser._safe_int(
                size_elem.attrib.get("maxheight")
            ) or DashboardParser._safe_int(size_elem.attrib.get("height"))

        return size_width, size_height

    @staticmethod
    def _parse_dashboard_sheets(
        db_element: ET.Element, worksheets: Dict[str, WorksheetModel]
    ) -> list[DashboardSheetModel]:
        """ダッシュボードシートを解析."""
        dashboard_sheets = []
        seen_sheet_names = set()  # 重複を防ぐためのセット

        for zone in db_element.findall(".//zone"):
            ws_name = zone.attrib.get("name")
            if ws_name and ws_name not in seen_sheet_names:  # 重複チェック
                seen_sheet_names.add(ws_name)  # 追加済みマーク

                # タイトル情報を取得
                title_elem = zone.find(".//title")
                title = title_elem.text if title_elem is not None else None
                show_title = (
                    title_elem.get("show", "true").lower() == "true"
                    if title_elem is not None
                    else True
                )

                # ワークシートかどうかを判定（汎用的な方法）
                is_worksheet = ws_name in worksheets

                dashboard_sheets.append(
                    DashboardSheetModel(
                        sheet_name=ws_name,
                        x=DashboardParser._safe_int(zone.attrib.get("x")),
                        y=DashboardParser._safe_int(zone.attrib.get("y")),
                        width=DashboardParser._safe_int(zone.attrib.get("w")),  # w/hを使用
                        height=DashboardParser._safe_int(zone.attrib.get("h")),
                        title=title,
                        show_title=show_title,
                        is_worksheet=is_worksheet,
                        formatting=None,
                    )
                )

        return dashboard_sheets

    @staticmethod
    def _parse_objects(db_element: ET.Element) -> list[DashboardObjectModel]:
        """ダッシュボードオブジェクトを解析."""
        objects = []
        for obj_elem in db_element.findall(".//object"):
            obj_model = DashboardParser._parse_dashboard_object(obj_elem)
            if obj_model:
                objects.append(obj_model)

        return objects

    @staticmethod
    def _parse_actions(db_element: ET.Element) -> list[DashboardActionModel]:
        """ダッシュボードアクションを解析."""
        actions = []
        for action_elem in db_element.findall(".//action"):
            action_model = DashboardParser._parse_dashboard_action(action_elem)
            if action_model:
                actions.append(action_model)

        return actions

    @staticmethod
    def _parse_title(db_element: ET.Element) -> tuple[str | None, bool]:
        """ダッシュボードのタイトルを解析."""
        title_elem = db_element.find(".//title")
        title = title_elem.text if title_elem is not None else None
        show_title = (
            title_elem.get("show", "true").lower() == "true" if title_elem is not None else True
        )

        return title, show_title

    @staticmethod
    def _parse_subtitle(db_element: ET.Element) -> tuple[str | None, bool]:
        """ダッシュボードのサブタイトルを解析."""
        subtitle_elem = db_element.find(".//subtitle")
        subtitle = subtitle_elem.text if subtitle_elem is not None else None
        show_subtitle = (
            subtitle_elem.get("show", "true").lower() == "true"
            if subtitle_elem is not None
            else True
        )

        return subtitle, show_subtitle

    @staticmethod
    def _parse_dashboard_object(obj_elem: ET.Element) -> Optional[DashboardObjectModel]:
        """ダッシュボードオブジェクト要素を解析してDashboardObjectModelを作成."""
        obj_type = obj_elem.get("type")
        if not obj_type:
            return None

        # 位置情報を取得
        id = obj_elem.get("id", "")
        name = obj_elem.get("name")
        x = DashboardParser._safe_int(obj_elem.get("x"))
        y = DashboardParser._safe_int(obj_elem.get("y"))
        width = DashboardParser._safe_int(obj_elem.get("width"))
        height = DashboardParser._safe_int(obj_elem.get("height"))

        # 書式設定を取得
        formatting = None
        format_elem = obj_elem.find(".//format")
        if format_elem is not None:
            formatting = FormattingModel(
                font_family=format_elem.get("font-family"),
                font_size=DashboardParser._safe_int(format_elem.get("font-size")),
                font_color=format_elem.get("font-color"),
                background_color=format_elem.get("background-color"),
                alignment=format_elem.get("alignment"),
                bold=format_elem.get("bold", "false").lower() == "true",
                italic=format_elem.get("italic", "false").lower() == "true",
                underline=format_elem.get("underline", "false").lower() == "true",
                date_format=format_elem.get("date-format"),
                currency_format=format_elem.get("currency-format"),
                number_format=format_elem.get("number-format"),
                padding=DashboardParser._safe_int(format_elem.get("padding")),
                border_width=DashboardParser._safe_int(format_elem.get("border-width")),
                border_color=format_elem.get("border-color"),
                border_style=format_elem.get("border-style"),
            )

        return DashboardObjectModel(
            id=id,
            type=obj_type,
            name=name,
            x=x,
            y=y,
            width=width,
            height=height,
            content=obj_elem.text,
            formatting=formatting,
        )

    @staticmethod
    def _parse_dashboard_action(action_elem: ET.Element) -> Optional[DashboardActionModel]:
        """ダッシュボードアクション要素を解析してDashboardActionModelを作成."""
        action_type = action_elem.get("type")
        if not action_type:
            return None

        return DashboardActionModel(
            name=action_elem.get("name", ""),
            action_type=action_type,
            source_sheet=action_elem.get("source-sheet"),
            target_sheet=action_elem.get("target-sheet"),
            source_field=action_elem.get("source-field"),
            target_field=action_elem.get("target-field"),
            enabled=action_elem.get("enabled", "true").lower() == "true",
        )

    @staticmethod
    def _safe_int(value: object) -> int:
        """安全にintに変換する."""
        if value is None:
            return 0
        try:
            return int(str(value))
        except (ValueError, TypeError):
            return 0
