"""計算フィールド関連のモデル."""

from typing import Optional

from pydantic import BaseModel, Field


class CalculatedFieldModel(BaseModel):
    """計算フィールド情報."""

    name: str = Field(description="計算フィールド名")
    caption: Optional[str] = Field(None, description="キャプション")
    datatype: Optional[str] = Field(None, description="データ型")
    role: Optional[str] = Field(None, description="役割（dimension/measure）")
    type: Optional[str] = Field(None, description="型（nominal/ordinal/quantitative）")
    formula: str = Field(description="計算式")
