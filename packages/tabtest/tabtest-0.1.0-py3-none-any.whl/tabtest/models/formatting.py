"""書式設定関連のモデル."""

from typing import Optional

from pydantic import BaseModel, Field


class FormattingModel(BaseModel):
    """書式設定情報."""

    font_family: Optional[str] = Field(None, description="フォントファミリー")
    font_size: Optional[int] = Field(None, description="フォントサイズ")
    font_color: Optional[str] = Field(None, description="フォント色")
    background_color: Optional[str] = Field(None, description="背景色")
    alignment: Optional[str] = Field(None, description="配置")
    number_format: Optional[str] = Field(None, description="数値フォーマット")
    bold: Optional[bool] = Field(None, description="太字")
    italic: Optional[bool] = Field(None, description="斜体")
    underline: Optional[bool] = Field(None, description="下線")
    date_format: Optional[str] = Field(None, description="日付フォーマット")
    currency_format: Optional[str] = Field(None, description="通貨フォーマット")
    padding: Optional[int] = Field(None, description="パディング設定")
    border_width: Optional[int] = Field(None, description="ボーダー幅")
    border_color: Optional[str] = Field(None, description="ボーダー色")
    border_style: Optional[str] = Field(None, description="ボーダースタイル")
