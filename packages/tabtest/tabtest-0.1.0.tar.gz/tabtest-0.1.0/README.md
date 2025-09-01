# tabtest

Tableauの`.twb`/`.twbx`ファイルを解析し、pytestでテストを実行できるPythonライブラリです。

## 概要

tabtestは、Tableauワークブックの構造を解析し、pytestを使用してワークブックの内容をテストできるようにするツールです。以下のようなテストが可能です：

- データソースの存在確認
- 計算フィールドの存在確認
- ワークシートの設定確認
- ダッシュボードのレイアウト確認
- パラメータの設定確認
- フィルターの設定確認

## インストール

```bash
pip install tabtest
```

## 基本的な使用方法

### 1. ワークブックの解析

```python
from tabtest import WorkbookParser

# ワークブックを解析
parser = WorkbookParser("./path/to/your/workbook.twb")
workbook = parser.workbook

# 基本情報の確認
print(f"ワークブック名: {workbook.name}")
print(f"データソース数: {len(workbook.datasources)}")
print(f"ワークシート数: {len(workbook.sheets)}")
print(f"ダッシュボード数: {len(workbook.dashboards)}")
```

### 2. pytestでのテスト

```python
import pytest
from tabtest.suite.helpers import (
    assert_workbook_has_datasource,
    assert_workbook_has_sheet,
    assert_workbook_has_dashboard,
    assert_datasource_has_calculated_field,
)

def test_workbook_structure(workbook_fixture):
    """ワークブックの基本構造をテスト"""
    workbook = workbook_fixture
    
    # データソースの確認
    data_ds = assert_workbook_has_datasource(
        workbook, "mock_datasource"
    )
    
    # 計算フィールドの確認
    assert_datasource_has_calculated_field(
        data_ds, "mock_calculated_field"
    )
    
    # ワークシートの確認
    sheet = assert_workbook_has_sheet(workbook, "mock_sheet")
    assert sheet.mark_type == "bar"
    
    # ダッシュボードの確認
    dashboard = assert_workbook_has_dashboard(workbook, "mock_dashboard")
    assert dashboard.size_width == 1200
    assert dashboard.size_height == 800
```

### 3. 利用可能なフィクスチャ

#### 汎用フィクスチャ（tabtestライブラリ提供）

pytestで以下の汎用フィクスチャが利用できます：

- `workbook_parser`: カスタムワークブックパーサー
- `workbook`: 解析済みワークブック
- `workbook_fixture`: モックワークブック（tests/assets/mock_workbook.twb）

使用方法：
```python
@pytest.mark.parametrize("workbook_parser", ["./path/to/your/workbook.twb"], indirect=True)
def test_workbook(workbook_parser):
    assert workbook_parser.workbook.name == "Expected Name"

@pytest.mark.parametrize("workbook_parser", ["./path/to/your/workbook.twb"], indirect=True)
def test_workbook(workbook):
    assert workbook.name == "Expected Name"
    assert len(workbook.datasources) > 0

def test_with_mock_workbook(workbook_fixture):
    """モックワークブックを使用したテスト"""
    workbook = workbook_fixture
    assert workbook.name == "Mock Workbook"
    assert len(workbook.datasources) > 0
```

#### ユーザー固有フィクスチャ

ユーザーは`tests/fixtures.py`で固有のフィクスチャを定義できます：

```python
# tests/fixtures.py
import pytest
from tabtest import WorkbookParser

@pytest.fixture
def my_workbook():
    """ユーザー固有のワークブックフィクスチャ"""
    parser = WorkbookParser("./path/to/your/workbook.twb")
    return parser.workbook
```

### 4. ヘルパー関数

以下のヘルパー関数が利用できます：

```python
from tabtest.suite.helpers import (
    # ワークブックレベル
    assert_workbook_has_datasource,
    assert_workbook_has_sheet,
    assert_workbook_has_dashboard,
    
    # データソースレベル
    assert_datasource_has_field,
    assert_datasource_has_calculated_field,
    
    # ワークシートレベル
    assert_sheet_has_field_in_rows,
    assert_sheet_has_field_in_columns,
    assert_sheet_has_filter,
    
    # ダッシュボードレベル
    assert_dashboard_contains_sheet,
)
```

## データモデル

### WorkbookModel

ワークブック全体の情報を表すモデルです。

```python
class WorkbookModel:
    name: str                    # ワークブック名
    datasources: List[DatasourceModel]  # データソース一覧
    sheets: Dict[str, WorksheetModel]   # ワークシート一覧
    dashboards: List[DashboardModel]    # ダッシュボード一覧
    parameters: List[ParameterModel]     # パラメータ一覧
```

### DatasourceModel

データソースの情報を表すモデルです。

```python
class DatasourceModel:
    name: Optional[str]          # データソース名
    caption: Optional[str]       # キャプション
    fields: List[DatasourceFieldModel]  # フィールド一覧
```

### WorksheetModel

ワークシートの情報を表すモデルです。

```python
class WorksheetModel:
    name: str                    # ワークシート名
    datasource_name: str         # データソース名
    filters: List[FilterModel]   # フィルター一覧
    rows: List[str]              # 行に配置されたフィールド
    columns: List[str]           # 列に配置されたフィールド
    mark_type: Optional[str]     # マークタイプ
```

### DashboardModel

ダッシュボードの情報を表すモデルです。

```python
class DashboardModel:
    name: Optional[str]          # ダッシュボード名
    dashboard_sheets: List[DashboardSheetModel]  # ダッシュボード内のワークシート
    size_width: int              # ダッシュボード幅
    size_height: int             # ダッシュボード高さ
```

## 使用例

詳細な使用例は`examples/`ディレクトリを参照してください：

- `examples/basic_usage.py`: 基本的な使用方法
- `examples/pytest_example.py`: pytestでのテスト例

## 開発

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-username/tabtest.git
cd tabtest

# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate     # Windows

# 依存関係をインストール
pip install -e .
pip install -e ".[dev]"
```

### テストの実行

```bash
# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_workbook_parser.py

# 詳細な出力でテストを実行
pytest -v
```

### コード品質チェック

```bash
# リンターを実行
ruff check .

# 型チェックを実行
mypy .

# フォーマットを実行
ruff format .
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。貢献する前に、以下の手順を確認してください：

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題や質問がある場合は、GitHubのイシューを作成してください。

## ライセンス

MIT License