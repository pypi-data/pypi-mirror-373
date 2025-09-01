"""セット関連のモデル."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SetModel(BaseModel):
    """セット情報."""

    name: str = Field(description="セット名")
    caption: Optional[str] = Field(None, description="キャプション")
    field_name: str = Field(description="対象フィールド名")
    set_type: Optional[str] = Field(None, description="セットタイプ")
    members: List[str] = Field(default_factory=list, description="メンバー一覧")
    formula: Optional[str] = Field(None, description="計算式")
