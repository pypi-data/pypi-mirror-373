"""メインのワークブックモデル."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .calculated_fields import CalculatedFieldModel
from .dashboard import DashboardModel
from .datasource import DatasourceModel
from .parameters import ParameterModel
from .sets import SetModel
from .worksheet import WorksheetModel


class WorkbookModel(BaseModel):
    """ワークブック情報."""

    name: str = Field(description="ワークブック名")
    datasources: List[DatasourceModel] = Field(default_factory=list, description="データソース一覧")
    sheets: Dict[str, WorksheetModel] = Field(default_factory=dict, description="ワークシート一覧")
    dashboards: List[DashboardModel] = Field(default_factory=list, description="ダッシュボード一覧")
    parameters: List[ParameterModel] = Field(default_factory=list, description="パラメータ一覧")
    version: Optional[str] = Field(None, description="Tableauバージョン")
    author: Optional[str] = Field(None, description="作成者")
    created_date: Optional[str] = Field(None, description="作成日")
    modified_date: Optional[str] = Field(None, description="更新日")
    description: Optional[str] = Field(None, description="説明")

    def get_datasource(self, name: str) -> Optional[DatasourceModel]:
        """指定した名前のデータソースを取得."""
        for ds in self.datasources:
            if ds.name == name:
                return ds
        return None

    def get_datasource_by_caption(self, caption: str) -> Optional[DatasourceModel]:
        """指定したキャプションのデータソースを取得."""
        for ds in self.datasources:
            if ds.caption == caption:
                return ds
        return None

    def get_sheet(self, name: str) -> Optional[WorksheetModel]:
        """指定した名前のワークシートを取得."""
        return self.sheets.get(name)

    def get_dashboard(self, name: str) -> Optional[DashboardModel]:
        """指定した名前のダッシュボードを取得."""
        for db in self.dashboards:
            if db.name == name:
                return db
        return None

    def get_parameter(self, name: str) -> Optional[ParameterModel]:
        """指定した名前のパラメータを取得."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_set(self, name: str) -> Optional[SetModel]:
        """指定した名前のセットを取得（全データソースから検索）."""
        for datasource in self.datasources:
            set_obj = datasource.get_set(name)
            if set_obj:
                return set_obj
        return None

    def get_calculated_field(self, name: str) -> Optional[CalculatedFieldModel]:
        """指定した名前の計算フィールドを取得（全データソースから検索）."""
        for datasource in self.datasources:
            calc_field = datasource.get_calculated_field(name)
            if calc_field:
                return calc_field
        return None

    def find_sheets_by_datasource(self, datasource_name: str) -> List[str]:
        """指定したデータソースを使用するワークシート名一覧を取得."""
        return [
            name for name, sheet in self.sheets.items() if sheet.datasource_name == datasource_name
        ]

    def find_sheets_with_field(self, field_name: str) -> List[str]:
        """指定したフィールドを使用するワークシート名一覧を取得."""
        result = []
        for name, sheet in self.sheets.items():
            datasource = self.get_datasource(sheet.datasource_name)
            if datasource:
                for field in datasource.fields:
                    if field_name in field.name:
                        result.append(name)
                        break
        return result

    def find_sheets_with_parameter(self, parameter_name: str) -> List[str]:
        """指定したパラメータを使用するワークシート名一覧を取得."""
        result = []
        for name, sheet in self.sheets.items():
            # パラメータがワークシートで使用されているかチェック
            if any(parameter_name in row for row in sheet.rows) or any(
                parameter_name in col for col in sheet.columns
            ):
                result.append(name)
        return result

    def find_sheets_with_set(self, set_name: str) -> List[str]:
        """指定したセットを使用するワークシート名一覧を取得."""
        result = []
        for name, sheet in self.sheets.items():
            datasource = self.get_datasource(sheet.datasource_name)
            if datasource and datasource.has_set(set_name):
                # セットがワークシートで使用されているかチェック
                if any(set_name in row for row in sheet.rows) or any(
                    set_name in col for col in sheet.columns
                ):
                    result.append(name)
        return result

    def get_all_calculated_fields(self) -> List[CalculatedFieldModel]:
        """すべての計算フィールドを取得（全データソースから）."""
        result = []
        for datasource in self.datasources:
            result.extend(datasource.get_all_calculated_fields())
        return result

    def get_all_parameters(self) -> List[ParameterModel]:
        """すべてのパラメータを取得."""
        return self.parameters

    def get_all_sets(self) -> List[SetModel]:
        """すべてのセットを取得（全データソースから）."""
        result = []
        for datasource in self.datasources:
            result.extend(datasource.sets)
        return result
