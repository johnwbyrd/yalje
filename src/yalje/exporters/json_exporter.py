"""JSON exporter for LiveJournal data."""

import json
from pathlib import Path

from yalje.core.exceptions import ExportError
from yalje.models.export import LJExport


class JSONExporter:
    """Exports LiveJournal data to JSON format."""

    def export(self, data: LJExport, output_path: Path, indent: int = 2) -> None:
        """Export data to JSON file.

        Args:
            data: LJExport object containing all data
            output_path: Path to write JSON file
            indent: Indentation level for pretty-printing

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Convert to dict
            data_dict = data.model_dump(mode="python")

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=indent, ensure_ascii=False)

        except Exception as e:
            raise ExportError(f"Failed to export to JSON: {e}") from e

    def export_string(self, data: LJExport, indent: int = 2) -> str:
        """Export data to JSON string.

        Args:
            data: LJExport object containing all data
            indent: Indentation level for pretty-printing

        Returns:
            JSON string

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Convert to dict
            data_dict = data.model_dump(mode="python")

            # Serialize to JSON
            return json.dumps(data_dict, indent=indent, ensure_ascii=False)

        except Exception as e:
            raise ExportError(f"Failed to export to JSON string: {e}") from e

    @staticmethod
    def load(input_path: Path) -> LJExport:
        """Load data from JSON file.

        Args:
            input_path: Path to JSON file

        Returns:
            LJExport object

        Raises:
            ExportError: If load fails
        """
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LJExport(**data)
        except Exception as e:
            raise ExportError(f"Failed to load from JSON: {e}") from e
