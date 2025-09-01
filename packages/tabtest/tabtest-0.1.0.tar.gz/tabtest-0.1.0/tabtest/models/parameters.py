"""パラメータ関連のモデル."""

from typing import Optional

from pydantic import BaseModel, Field


class ParameterModel(BaseModel):
    """パラメータ情報."""

    name: str = Field(description="パラメータ名")
    caption: Optional[str] = Field(None, description="キャプション")
    datatype: Optional[str] = Field(None, description="データ型")
    role: Optional[str] = Field(None, description="役割")
    param_domain_type: Optional[str] = Field(None, description="ドメインタイプ")
    default_value: Optional[str] = Field(None, description="デフォルト値")
