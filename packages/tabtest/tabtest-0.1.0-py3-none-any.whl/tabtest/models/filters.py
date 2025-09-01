"""フィルタ関連のモデル."""

import html
import urllib.parse
from typing import Optional

from pydantic import BaseModel, Field


class GroupFilterModel(BaseModel):
    """グループフィルタ情報."""

    function: Optional[str] = Field(None, description="フィルタ機能")
    level: Optional[str] = Field(None, description="レベル")
    member: Optional[str] = Field(None, description="メンバー")
    expression: Optional[str] = Field(None, description="フィルタ条件式")
    ui_enumeration: Optional[str] = Field(None, description="UI列挙設定")
    ui_marker: Optional[str] = Field(None, description="UIマーカー")
    ui_domain: Optional[str] = Field(None, description="UIドメイン")
    ui_manual_selection: Optional[str] = Field(None, description="UI手動選択")
    ui_manual_selection_all_when_empty: Optional[str] = Field(None, description="UI空時の全選択")

    def get_unescaped_member(self) -> Optional[str]:
        """
        エスケープされていないメンバー名を取得.

        Returns:
            エスケープされていないメンバー名

        """
        if not self.member:
            return None

        # HTMLエンティティをデコード
        unescaped = html.unescape(self.member)

        # URLエンコードをデコード
        try:
            unescaped = urllib.parse.unquote(unescaped)
        except Exception:
            # URLデコードに失敗した場合は元の値をそのまま使用
            pass

        return unescaped


class DataSourceFilterModel(BaseModel):
    """データソースフィルタ情報."""

    name: Optional[str] = Field(None, description="フィルタ名")
    field: str = Field(description="フィールド名")
    filter_class: Optional[str] = Field(None, description="フィルタクラス")
    filter_group: Optional[str] = Field(None, description="フィルタグループ")
    group_filter: Optional[GroupFilterModel] = Field(None, description="グループフィルタ")

    def has_expression(self, expression: str) -> bool:
        """
        指定した条件式が含まれているかチェック.

        Args:
            expression: 検索する条件式

        Returns:
            条件式が含まれているかどうか

        """
        if not self.group_filter or not self.group_filter.expression:
            return False

        # エスケープされた文字列を通常の文字列に変換して比較
        normalized_expression = self._unescape_text(self.group_filter.expression)
        normalized_search = self._unescape_text(expression)

        return normalized_search in normalized_expression

    def get_unescaped_expression(self) -> Optional[str]:
        """
        エスケープされていない条件式を取得.

        Returns:
            エスケープされていない条件式

        """
        if not self.group_filter or not self.group_filter.expression:
            return None

        return self._unescape_text(self.group_filter.expression)

    def has_member(self, member: str) -> bool:
        """
        指定したメンバー名が含まれているかチェック.

        Args:
            member: 検索するメンバー名

        Returns:
            メンバー名が含まれているかどうか

        """
        if not self.group_filter:
            return False

        # member属性をチェック
        if self.group_filter.member:
            normalized_member = self._unescape_text(self.group_filter.member)
            normalized_search = self._unescape_text(member)
            if normalized_search in normalized_member:
                return True

        # expression属性もチェック（expressionにmemberが含まれている場合がある）
        if self.group_filter.expression:
            normalized_expression = self._unescape_text(self.group_filter.expression)
            normalized_search = self._unescape_text(member)
            if normalized_search in normalized_expression:
                return True

        return False

    def get_unescaped_member(self) -> Optional[str]:
        """
        エスケープされていないメンバー名を取得.

        Returns:
            エスケープされていないメンバー名

        """
        if not self.group_filter:
            return None

        return self.group_filter.get_unescaped_member()

    def _unescape_text(self, text: str) -> str:
        """
        テキストからエスケープ文字列を除去.

        Args:
            text: エスケープ文字列を含むテキスト

        Returns:
            エスケープ文字列が除去されたテキスト

        """
        if not text:
            return text

        # HTMLエンティティをデコード
        unescaped = html.unescape(text)

        # URLエンコードをデコード
        try:
            unescaped = urllib.parse.unquote(unescaped)
        except Exception:
            # URLデコードに失敗した場合は元の値をそのまま使用
            pass

        return unescaped
