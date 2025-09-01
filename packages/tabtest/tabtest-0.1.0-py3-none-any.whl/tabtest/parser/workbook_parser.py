import xml.etree.ElementTree as ET
from pathlib import Path

from tabtest.models import WorkbookModel

from .dashboard_parser import DashboardParser
from .datasource_parser import DatasourceParser
from .reference_resolver import ReferenceResolver
from .worksheet_parser import WorksheetParser
from .xml_loader import XMLLoader


class WorkbookParser:
    """Tableauワークブックのメインパーサークラス."""

    def __init__(self, file_path: str) -> None:
        """ワークブックパーサーの初期化."""
        self.file_path = Path(file_path)
        self.tree: ET.ElementTree | None = None
        self.root: ET.Element | None = None
        self.workbook: WorkbookModel | None = None

        self._parse()

    def _parse(self) -> None:
        """ワークブックの解析を実行."""
        self._load_xml()
        self._parse_workbook()

    def _load_xml(self) -> None:
        """XMLファイルを読み込む."""
        self.tree = XMLLoader.load_xml(self.file_path)
        self.root = self.tree.getroot()

    def _parse_workbook(self) -> None:
        """ワークブック全体を解析."""
        if self.root is None:
            raise ValueError("XML root element is not loaded")

        repo_elem = self.root.find(".//repository-location")
        if repo_elem is not None:
            workbook_name = repo_elem.attrib.get("id", "Untitled Workbook")
        else:
            workbook_name = "Untitled Workbook"

        # ワークブックのメタデータを取得
        version = self.root.get("version")
        author = self.root.get("author")
        created_date = self.root.get("created")
        modified_date = self.root.get("modified")

        # Datasources
        datasources = []
        for ds_element in self.root.findall(".//datasource"):
            ds_name = ds_element.get("name")
            if ds_name == "Parameters":
                # Parameters datasource → DatasourceModel には入れない
                continue
            ds_model = DatasourceParser.parse_datasource(ds_element)
            if ds_model.fields:  # fieldsが空でない場合だけ追加する
                datasources.append(ds_model)

        # Parameters (ワークブックレベルで解析)
        parameters = []
        seen_param_names = set()  # 重複チェック用
        for param_element in self.root.findall(".//column[@param-domain-type]"):
            param_model = DatasourceParser.parse_parameter(param_element)
            if param_model and param_model.name not in seen_param_names:
                parameters.append(param_model)
                seen_param_names.add(param_model.name)

        # Worksheets
        worksheets = {}
        for ws_element in self.root.findall(".//worksheet"):
            ws_model = WorksheetParser.parse_worksheet(ws_element, datasources)
            worksheets[ws_model.name] = ws_model

        # Dashboards
        dashboards = []
        for db_element in self.root.findall(".//dashboard"):
            db_name = db_element.attrib.get("name")
            # 名前が正しく設定されているダッシュボードのみを解析
            if db_name and not db_name.startswith("Unnamed_"):
                dashboards.append(DashboardParser.parse_dashboard(db_element, worksheets))

        self.workbook = WorkbookModel(
            name=workbook_name,
            datasources=datasources,
            sheets=worksheets,
            dashboards=dashboards,
            parameters=parameters,
            version=version,
            author=author,
            created_date=created_date,
            modified_date=modified_date,
            description=None,
        )

        # ワークブック全体の解析が完了した後、パラメータ参照を解決
        ReferenceResolver.resolve_parameter_references_in_workbook(self.workbook)
