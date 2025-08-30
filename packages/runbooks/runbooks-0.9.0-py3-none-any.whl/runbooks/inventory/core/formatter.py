"""
Inventory formatter for various output formats.

This module provides formatting capabilities for inventory data
including CSV, JSON, Excel, and console table formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

try:
    import pandas as pd

    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False
    pd = None

from loguru import logger

from runbooks.base import CloudFoundationsFormatter


class InventoryFormatter(CloudFoundationsFormatter):
    """Formatter for inventory data with multiple output formats."""

    def __init__(self, inventory_data: Dict[str, Any]):
        """Initialize formatter with inventory data."""
        super().__init__(inventory_data)
        self.inventory_data = inventory_data

    def to_csv(self, file_path: Union[str, Path]) -> None:
        """Save inventory data as CSV files (one per resource type)."""
        if not _HAS_PANDAS:
            logger.error("pandas is required for CSV export. Install with: pip install pandas")
            return

        output_path = Path(file_path)
        output_dir = output_path.parent / output_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        resources = self.inventory_data.get("resources", {})

        for resource_type, accounts_data in resources.items():
            # Flatten data for CSV format
            rows = []

            for account_id, account_data in accounts_data.items():
                if "error" in account_data:
                    rows.append(
                        {
                            "account_id": account_id,
                            "resource_type": resource_type,
                            "status": "error",
                            "error_message": account_data["error"],
                        }
                    )
                    continue

                # Extract resources based on type
                if resource_type == "ec2" and "instances" in account_data:
                    for instance in account_data["instances"]:
                        row = {
                            "account_id": account_id,
                            "resource_type": resource_type,
                            "resource_id": instance.get("instance_id"),
                            "resource_name": instance.get("instance_id"),
                            "instance_type": instance.get("instance_type"),
                            "state": instance.get("state"),
                            "region": instance.get("region"),
                            "tags": json.dumps(instance.get("tags", {})),
                        }
                        rows.append(row)

                elif resource_type == "rds" and "instances" in account_data:
                    for instance in account_data["instances"]:
                        row = {
                            "account_id": account_id,
                            "resource_type": resource_type,
                            "resource_id": instance.get("db_instance_identifier"),
                            "resource_name": instance.get("db_instance_identifier"),
                            "engine": instance.get("engine"),
                            "instance_class": instance.get("instance_class"),
                            "status": instance.get("status"),
                            "region": self.inventory_data["metadata"].get("collector_region"),
                        }
                        rows.append(row)

                elif resource_type == "s3" and "buckets" in account_data:
                    for bucket in account_data["buckets"]:
                        row = {
                            "account_id": account_id,
                            "resource_type": resource_type,
                            "resource_id": bucket.get("name"),
                            "resource_name": bucket.get("name"),
                            "creation_date": bucket.get("creation_date"),
                            "region": bucket.get("region"),
                        }
                        rows.append(row)

            if rows:
                df = pd.DataFrame(rows)
                csv_file = output_dir / f"{resource_type}.csv"
                df.to_csv(csv_file, index=False)
                logger.info(f"Saved {resource_type} data to: {csv_file}")

        # Save summary
        summary_file = output_dir / "summary.csv"
        summary_data = []

        summary = self.inventory_data.get("summary", {})
        for resource_type, count in summary.get("resources_by_type", {}).items():
            summary_data.append({"resource_type": resource_type, "total_count": count})

        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv(summary_file, index=False)
            logger.info(f"Saved summary to: {summary_file}")

    def to_excel(self, file_path: Union[str, Path]) -> None:
        """Save inventory data as Excel file with multiple sheets."""
        if not _HAS_PANDAS:
            logger.error("pandas is required for Excel export. Install with: pip install pandas")
            return

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            # Summary sheet
            summary = self.inventory_data.get("summary", {})
            summary_data = []

            for resource_type, count in summary.get("resources_by_type", {}).items():
                summary_data.append({"Resource Type": resource_type.upper(), "Total Count": count})

            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name="Summary", index=False)

            # Resource sheets
            resources = self.inventory_data.get("resources", {})

            for resource_type, accounts_data in resources.items():
                rows = []

                for account_id, account_data in accounts_data.items():
                    if "error" in account_data:
                        continue

                    # Extract resources based on type
                    if resource_type == "ec2" and "instances" in account_data:
                        for instance in account_data["instances"]:
                            row = {
                                "Account ID": account_id,
                                "Instance ID": instance.get("instance_id"),
                                "Instance Type": instance.get("instance_type"),
                                "State": instance.get("state"),
                                "Region": instance.get("region"),
                                "Environment": instance.get("tags", {}).get("Environment", "N/A"),
                            }
                            rows.append(row)

                    elif resource_type == "rds" and "instances" in account_data:
                        for instance in account_data["instances"]:
                            row = {
                                "Account ID": account_id,
                                "DB Instance ID": instance.get("db_instance_identifier"),
                                "Engine": instance.get("engine"),
                                "Instance Class": instance.get("instance_class"),
                                "Status": instance.get("status"),
                            }
                            rows.append(row)

                    elif resource_type == "s3" and "buckets" in account_data:
                        for bucket in account_data["buckets"]:
                            row = {
                                "Account ID": account_id,
                                "Bucket Name": bucket.get("name"),
                                "Creation Date": bucket.get("creation_date"),
                                "Region": bucket.get("region"),
                            }
                            rows.append(row)

                if rows:
                    df = pd.DataFrame(rows)
                    sheet_name = resource_type.upper()[:31]  # Excel sheet name limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Excel inventory saved to: {output_path}")

    def to_json(self, file_path: Union[str, Path]) -> None:
        """Save inventory data as JSON file."""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.inventory_data, f, indent=2, default=str)

        logger.info(f"JSON inventory saved to: {output_path}")

    def format_console_table(self) -> str:
        """Format inventory data for console display."""
        try:
            from rich.console import Console
            from rich.table import Table
        except ImportError:
            # Fallback to simple text output
            return self._format_simple_text_table()

        console = Console()

        # Summary table
        summary_table = Table(title="Inventory Summary")
        summary_table.add_column("Resource Type", style="cyan")
        summary_table.add_column("Total Count", style="bold")

        summary = self.inventory_data.get("summary", {})
        for resource_type, count in summary.get("resources_by_type", {}).items():
            summary_table.add_row(resource_type.upper(), str(count))

        # Account breakdown table
        account_table = Table(title="Resources by Account")
        account_table.add_column("Account ID", style="cyan")
        account_table.add_column("Total Resources", style="bold")

        for account_id, count in summary.get("resources_by_account", {}).items():
            account_table.add_row(account_id, str(count))

        # Capture console output
        with console.capture() as capture:
            console.print(summary_table)
            console.print()
            console.print(account_table)

            # Metadata
            metadata = self.inventory_data.get("metadata", {})
            console.print(f"\n[bold]Collection Details:[/bold]")
            console.print(f"Collection Time: {metadata.get('collection_time', 'N/A')}")
            console.print(f"Duration: {metadata.get('duration_seconds', 0):.1f}s")
            console.print(f"Profile: {metadata.get('collector_profile', 'N/A')}")
            console.print(f"Region: {metadata.get('collector_region', 'N/A')}")

        return capture.get()

    def _format_simple_text_table(self) -> str:
        """Fallback text formatting when rich is not available."""
        output = "Inventory Summary\n" + "=" * 50 + "\n"

        summary = self.inventory_data.get("summary", {})

        # Resource summary
        output += "Resources by Type:\n"
        for resource_type, count in summary.get("resources_by_type", {}).items():
            output += f"  {resource_type.upper()}: {count}\n"

        # Account summary
        output += "\nResources by Account:\n"
        for account_id, count in summary.get("resources_by_account", {}).items():
            output += f"  {account_id}: {count}\n"

        # Metadata
        metadata = self.inventory_data.get("metadata", {})
        output += f"\nCollection Details:\n"
        output += f"  Collection Time: {metadata.get('collection_time', 'N/A')}\n"
        output += f"  Duration: {metadata.get('duration_seconds', 0):.1f}s\n"
        output += f"  Profile: {metadata.get('collector_profile', 'N/A')}\n"
        output += f"  Region: {metadata.get('collector_region', 'N/A')}\n"

        return output

    def get_resource_counts(self) -> Dict[str, int]:
        """Get resource counts by type."""
        summary = self.inventory_data.get("summary", {})
        return summary.get("resources_by_type", {})

    def get_account_counts(self) -> Dict[str, int]:
        """Get resource counts by account."""
        summary = self.inventory_data.get("summary", {})
        return summary.get("resources_by_account", {})

    def get_total_resources(self) -> int:
        """Get total resource count."""
        summary = self.inventory_data.get("summary", {})
        return summary.get("total_resources", 0)

    def has_errors(self) -> bool:
        """Check if inventory collection had errors."""
        errors = self.inventory_data.get("errors", [])
        return len(errors) > 0

    def get_errors(self) -> List[str]:
        """Get list of collection errors."""
        return self.inventory_data.get("errors", [])
