import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


class XMLLoader:
    """XMLファイルの読み込みを担当するクラス."""

    @staticmethod
    def load_xml(file_path: str | Path):
        """
        .twbまたは.twbxファイルからXMLを読み込む.

        Args:
            file_path: ファイルパス.

        Returns:
            ElementTreeオブジェクト.

        Raises:
            ValueError: サポートされていないファイル形式の場合.

        """
        file_path = Path(file_path)
        if file_path.suffix == ".twb":
            return ET.parse(str(file_path))
        elif file_path.suffix == ".twbx":
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                for name in zip_ref.namelist():
                    if name.endswith(".twb"):
                        with zip_ref.open(name) as f:
                            return ET.parse(f)
                raise ValueError("No .twb file found in .twbx archive")
        else:
            raise ValueError("Unsupported file type. Only .twb and .twbx files are supported.")
