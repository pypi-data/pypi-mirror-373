import xml.etree.ElementTree as ET

from tabtest.models import DatasourceModel, FilterModel, WorksheetModel

from .reference_resolver import ReferenceResolver


class WorksheetParser:
    """ワークシート関連の解析を担当するクラス."""

    @staticmethod
    def parse_worksheet(
        ws_element: ET.Element, workbook_datasources: list[DatasourceModel]
    ) -> WorksheetModel:
        """ワークシート要素を解析してWorksheetModelを作成."""
        ws_name = ws_element.get("name", "")

        # データソース取得
        datasource_elem = ws_element.find(".//datasource")
        datasource_name = ""
        if datasource_elem is not None:
            datasource_name = datasource_elem.get("name", "")

        # フィルター
        filters = WorksheetParser._parse_filters(ws_element)

        # rows
        rows = WorksheetParser._parse_rows(ws_element)

        # columns
        columns = WorksheetParser._parse_columns(ws_element)

        # mark type and properties
        mark_type, mark_color, mark_size, mark_shape, mark_label, mark_tooltip = (
            WorksheetParser._parse_mark_properties(ws_element)
        )

        # タイトル情報
        title, show_title = WorksheetParser._parse_title(ws_element)
        subtitle, show_subtitle = WorksheetParser._parse_subtitle(ws_element)
        caption, show_caption = WorksheetParser._parse_caption(ws_element)

        worksheet_model = WorksheetModel(
            name=ws_name,
            datasource_name=datasource_name,
            filters=filters,
            rows=rows,
            columns=columns,
            mark_type=mark_type,
            mark_color=mark_color,
            mark_size=mark_size,
            mark_shape=mark_shape,
            mark_label=mark_label,
            mark_tooltip=mark_tooltip,
            title=title,
            subtitle=subtitle,
            caption=caption,
            show_title=show_title,
            show_subtitle=show_subtitle,
            show_caption=show_caption,
            formatting=None,
        )

        # ワークシート内の計算フィールド参照を解決
        if datasource_name and datasource_name in [ds.name for ds in workbook_datasources]:
            datasource_model = next(
                (ds for ds in workbook_datasources if ds.name == datasource_name), None
            )
            if datasource_model:
                ReferenceResolver.resolve_calculation_references_in_worksheet(
                    worksheet_model, datasource_model
                )

        return worksheet_model

    @staticmethod
    def _parse_filters(ws_element: ET.Element) -> list[FilterModel]:
        """ワークシートのフィルターを解析."""
        filters = []
        for filter_elem in ws_element.findall(".//filter"):
            # field属性とcolumn属性の両方をチェック
            field = filter_elem.get("field") or filter_elem.get("column")
            if field:
                filter_model = FilterModel(
                    name=filter_elem.get("name", ""),
                    field=field,
                    default_value=filter_elem.get("value"),
                    apply_mode=filter_elem.get("apply-mode"),
                    allow_all_values=filter_elem.get("allow-all-values", "false").lower() == "true",
                    filter_type=filter_elem.get("filter-type") or filter_elem.get("class"),
                    values=[val.get("value", "") for val in filter_elem.findall(".//value")],
                    range_start=filter_elem.get("range-start"),
                    range_end=filter_elem.get("range-end"),
                )
                filters.append(filter_model)

        return filters

    @staticmethod
    def _parse_rows(ws_element: ET.Element) -> list[str]:
        """ワークシートのrowsを解析."""
        rows_elem = ws_element.find(".//rows")
        rows = []
        if rows_elem is not None and rows_elem.text:
            rows = [row.strip() for row in rows_elem.text.strip().split("\n") if row.strip()]

        return rows

    @staticmethod
    def _parse_columns(ws_element: ET.Element) -> list[str]:
        """ワークシートのcolumnsを解析."""
        cols_elem = ws_element.find(".//cols")
        columns = []
        if cols_elem is not None and cols_elem.text:
            columns = [col.strip() for col in cols_elem.text.strip().split("\n") if col.strip()]

        return columns

    @staticmethod
    def _parse_mark_properties(
        ws_element: ET.Element,
    ) -> tuple[str, str | None, str | None, str | None, str | None, str | None]:
        """ワークシートのmark propertiesを解析."""
        mark_elem = ws_element.find(".//mark")
        if mark_elem is None:
            return "", None, None, None, None, None

        mark_type = mark_elem.get("class", "")
        mark_color = mark_elem.get("color") if mark_elem is not None else None
        mark_size = mark_elem.get("size") if mark_elem is not None else None
        mark_shape = mark_elem.get("shape") if mark_elem is not None else None
        mark_label = mark_elem.get("label") if mark_elem is not None else None
        mark_tooltip = mark_elem.get("tooltip") if mark_elem is not None else None
        return mark_type, mark_color, mark_size, mark_shape, mark_label, mark_tooltip

    @staticmethod
    def _parse_title(ws_element: ET.Element) -> tuple[str | None, bool]:
        """ワークシートのタイトルを解析."""
        title_elem = ws_element.find(".//title")
        title = title_elem.text if title_elem is not None else None
        show_title = (
            title_elem.get("show", "true").lower() == "true" if title_elem is not None else True
        )

        return title, show_title

    @staticmethod
    def _parse_subtitle(ws_element: ET.Element) -> tuple[str | None, bool]:
        """ワークシートのサブタイトルを解析."""
        subtitle_elem = ws_element.find(".//subtitle")
        subtitle = subtitle_elem.text if subtitle_elem is not None else None
        show_subtitle = (
            subtitle_elem.get("show", "true").lower() == "true"
            if subtitle_elem is not None
            else True
        )

        return subtitle, show_subtitle

    @staticmethod
    def _parse_caption(ws_element: ET.Element) -> tuple[str | None, bool]:
        """ワークシートのキャプションを解析."""
        caption_elem = ws_element.find(".//caption")
        caption = caption_elem.text if caption_elem is not None else None
        show_caption = (
            caption_elem.get("show", "true").lower() == "true" if caption_elem is not None else True
        )

        return caption, show_caption
