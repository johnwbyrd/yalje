"""YAML exporter for LiveJournal data."""

from pathlib import Path

from yalje.core.exceptions import ExportError
from yalje.models.export import LJExport


class YAMLExporter:
    """Exports LiveJournal data to YAML format."""

    def export(self, data: LJExport, output_path: Path) -> None:
        """Export data to YAML file.

        Args:
            data: LJExport object containing all data
            output_path: Path to write YAML file

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Write to file using model's to_file method
            data.to_file(str(output_path))

        except Exception as e:
            raise ExportError(f"Failed to export to YAML: {e}") from e

    def export_string(self, data: LJExport) -> str:
        """Export data to YAML string.

        Args:
            data: LJExport object containing all data

        Returns:
            YAML string

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Use model's to_yaml method
            return data.to_yaml()

        except Exception as e:
            raise ExportError(f"Failed to export to YAML string: {e}") from e

    @staticmethod
    def load(input_path: Path) -> LJExport:
        """Load data from YAML file.

        Args:
            input_path: Path to YAML file

        Returns:
            LJExport object

        Raises:
            ExportError: If load fails
        """
        try:
            return LJExport.from_file(str(input_path))
        except Exception as e:
            raise ExportError(f"Failed to load from YAML: {e}") from e
