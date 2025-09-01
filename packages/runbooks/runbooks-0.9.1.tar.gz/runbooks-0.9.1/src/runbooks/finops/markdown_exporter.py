#!/usr/bin/env python3
"""
Rich-styled Markdown Export Module for CloudOps Runbooks FinOps

This module provides Rich table to markdown conversion functionality with
MkDocs compatibility for copy-pasteable documentation tables.

Features:
- Rich table to markdown conversion with styled borders
- 10-column format for multi-account analysis
- MkDocs compatible table syntax
- Intelligent file management and organization
- Preserves color coding through markdown syntax
- Automated timestamping and metadata

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich import box
from rich.table import Table
from rich.text import Text

from runbooks.common.rich_utils import (
    STATUS_INDICATORS,
    console,
    create_table,
    format_cost,
    print_info,
    print_success,
    print_warning,
)


class MarkdownExporter:
    """Rich-styled markdown export functionality for FinOps analysis."""

    def __init__(self, output_dir: str = "./exports"):
        """
        Initialize the markdown exporter.

        Args:
            output_dir: Directory to save markdown exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def rich_table_to_markdown(self, table: Table, preserve_styling: bool = True) -> str:
        """
        Convert Rich table to markdown format with optional styling preservation.

        Args:
            table: Rich Table object to convert
            preserve_styling: Whether to preserve Rich styling through markdown syntax

        Returns:
            Markdown formatted table string
        """
        if not table.columns:
            return ""

        # Extract column headers
        headers = []
        for column in table.columns:
            header_text = column.header or ""
            if hasattr(header_text, "plain"):
                headers.append(header_text.plain)
            else:
                headers.append(str(header_text))

        # Create markdown table header
        markdown_lines = []
        markdown_lines.append("| " + " | ".join(headers) + " |")

        # Create GitHub-compliant separator line with proper alignment syntax
        separators = []
        for column in table.columns:
            if column.justify == "right":
                separators.append("---:")  # GitHub right alignment (minimum 3 hyphens)
            elif column.justify == "center":
                separators.append(":---:")  # GitHub center alignment
            else:
                separators.append("---")  # GitHub left alignment (default, minimum 3 hyphens)
        markdown_lines.append("| " + " | ".join(separators) + " |")

        # Extract and format data rows
        for row in table.rows:
            row_cells = []
            for cell in row:
                if isinstance(cell, Text):
                    if preserve_styling:
                        # Convert Rich Text to markdown with styling
                        cell_text = self._rich_text_to_markdown(cell)
                    else:
                        cell_text = cell.plain
                else:
                    cell_text = str(cell)

                # GitHub tables don't support multi-line content - convert to single line
                cell_text = cell_text.replace("\n", " • ").strip()

                # Escape pipes in cell content for GitHub compatibility
                cell_text = cell_text.replace("|", "\\|")

                # Remove excessive Rich formatting that doesn't render well in GitHub
                cell_text = self._clean_rich_formatting_for_github(cell_text)

                row_cells.append(cell_text)

            markdown_lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(markdown_lines)

    def _rich_text_to_markdown(self, rich_text: Text) -> str:
        """
        Convert Rich Text object to markdown with style preservation.

        Args:
            rich_text: Rich Text object with styling

        Returns:
            Markdown formatted string with preserved styling
        """
        # Start with plain text
        text = rich_text.plain

        # Extract style information and apply markdown equivalents
        if hasattr(rich_text, "_spans") and rich_text._spans:
            for span in reversed(rich_text._spans):  # Reverse to handle overlapping spans
                style = span.style
                start, end = span.start, span.end

                # Apply markdown formatting based on Rich styles
                if style and hasattr(style, "color"):
                    if "green" in str(style.color):
                        # Green text (success/positive) - use ✅ emoji
                        text = text[:start] + "✅ " + text[start:end] + text[end:]
                    elif "red" in str(style.color):
                        # Red text (error/negative) - use ❌ emoji
                        text = text[:start] + "❌ " + text[start:end] + text[end:]
                    elif "yellow" in str(style.color):
                        # Yellow text (warning) - use ⚠️ emoji
                        text = text[:start] + "⚠️ " + text[start:end] + text[end:]
                    elif "cyan" in str(style.color):
                        # Cyan text (info) - use **bold** markdown
                        text = text[:start] + "**" + text[start:end] + "**" + text[end:]

                if style and hasattr(style, "bold") and style.bold:
                    text = text[:start] + "**" + text[start:end] + "**" + text[end:]

                if style and hasattr(style, "italic") and style.italic:
                    text = text[:start] + "*" + text[start:end] + "*" + text[end:]

        return text

    def _clean_rich_formatting_for_github(self, text: str) -> str:
        """
        Clean Rich formatting for better GitHub markdown compatibility.

        Args:
            text: Text with Rich formatting tags

        Returns:
            Cleaned text suitable for GitHub markdown tables
        """
        # Remove Rich color/style tags that don't render well in GitHub
        import re

        # Remove Rich markup tags but preserve content
        text = re.sub(r"\[/?(?:red|green|yellow|cyan|blue|magenta|white|black|bright_\w+|dim|bold|italic)\]", "", text)
        text = re.sub(r"\[/?[^\]]*\]", "", text)  # Remove any remaining Rich tags

        # Clean up multiple spaces and trim
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def create_single_account_export(self, profile_data: Dict[str, Any], account_id: str, profile_name: str) -> str:
        """
        Create markdown export for single account analysis.

        Args:
            profile_data: Single profile cost data
            account_id: AWS account ID
            profile_name: AWS profile name

        Returns:
            Markdown formatted single account analysis
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Create markdown content
        markdown_content = f"""# AWS Cost Analysis - Account {account_id}

**Generated**: {timestamp}  
**Profile**: {profile_name}  
**Organization**: Single Account Analysis

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Cost | ${profile_data.get("total_cost", 0):,.2f} | {self._get_cost_status_emoji(profile_data.get("total_cost", 0))} |
| Service Count | {len(profile_data.get("service_breakdown", []))} services | 📊 |
| Cost Trend | {profile_data.get("cost_trend", "Stable")} | {self._get_trend_emoji(profile_data.get("cost_trend", ""))} |

## Service Breakdown

| Service | Current Cost | Percentage | Trend | Optimization |
|---------|--------------|------------|-------|--------------|
"""

        # Add service breakdown rows
        services = profile_data.get("service_breakdown", [])
        for service in services[:10]:  # Top 10 services
            service_name = service.get("service", "Unknown")
            cost = service.get("cost", 0)
            percentage = service.get("percentage", 0)
            trend = service.get("trend", "Stable")
            optimization = service.get("optimization_opportunity", "Monitor")

            markdown_content += f"| {service_name} | ${cost:,.2f} | {percentage:.1f}% | {self._get_trend_emoji(trend)} {trend} | {optimization} |\n"

        # Add resource optimization section
        markdown_content += f"""

## Resource Optimization Opportunities

| Resource Type | Count | Potential Savings | Action Required |
|---------------|-------|------------------|-----------------|
| Stopped EC2 Instances | {profile_data.get("stopped_ec2", 0)} | ${profile_data.get("stopped_ec2_savings", 0):,.2f} | Review and terminate |
| Unused EBS Volumes | {profile_data.get("unused_volumes", 0)} | ${profile_data.get("unused_volume_savings", 0):,.2f} | Clean up unused storage |
| Unused Elastic IPs | {profile_data.get("unused_eips", 0)} | ${profile_data.get("unused_eip_savings", 0):,.2f} | Release unused IPs |
| Untagged Resources | {profile_data.get("untagged_resources", 0)} | N/A | Implement tagging strategy |

---
*Generated by CloudOps Runbooks FinOps Module v0.7.8*
"""

        return markdown_content

    def create_multi_account_export(
        self, multi_profile_data: List[Dict[str, Any]], organization_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create 10-column markdown export for multi-account analysis.

        Args:
            multi_profile_data: List of profile data dictionaries
            organization_info: Optional organization metadata

        Returns:
            Markdown formatted multi-account analysis with 10 columns
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        account_count = len(multi_profile_data)

        # Calculate organization totals
        total_cost = sum(profile.get("total_cost", 0) for profile in multi_profile_data)
        total_savings = sum(profile.get("potential_savings", 0) for profile in multi_profile_data)

        # Create markdown content with 10-column format
        markdown_content = f"""# AWS Multi-Account Cost Analysis

**Generated**: {timestamp}  
**Organization**: {account_count} accounts  
**Total Cost**: ${total_cost:,.2f}  
**Potential Savings**: ${total_savings:,.2f}

## Executive Dashboard

| Metric | Value | Status |
|--------|-------|--------|
| Total Monthly Cost | ${total_cost:,.2f} | 💰 |
| Average per Account | ${total_cost / account_count:,.2f} | 📊 |
| Optimization Opportunity | ${total_savings:,.2f} ({total_savings / total_cost * 100:.1f}%) | 🎯 |

## Multi-Account Analysis (10-Column Format)

| Profile | Last Month | Current Month | Top 3 Services | Budget | Stopped EC2 | Unused Vol | Unused EIP | Savings | Untagged |
|---------|------------|---------------|-----------------|---------|-------------|------------|------------|---------|----------|
"""

        # Add data rows for each profile
        for profile_data in multi_profile_data:
            profile_name = profile_data.get("profile_name", "Unknown")[:15]  # Truncate for table width
            last_month = profile_data.get("last_month_cost", 0)
            current_month = profile_data.get("total_cost", 0)

            # Get top 3 services
            services = profile_data.get("service_breakdown", [])
            top_services = [s.get("service", "")[:6] for s in services[:3]]  # Truncate service names
            top_services_str = ",".join(top_services) if top_services else "N/A"

            # Budget status
            budget_status = self._get_budget_status_emoji(profile_data.get("budget_status", "unknown"))

            # Resource optimization data
            stopped_ec2 = profile_data.get("stopped_ec2", 0)
            unused_volumes = profile_data.get("unused_volumes", 0)
            unused_eips = profile_data.get("unused_eips", 0)
            potential_savings = profile_data.get("potential_savings", 0)
            untagged_resources = profile_data.get("untagged_resources", 0)

            # Add row to table
            markdown_content += f"| {profile_name} | ${last_month:,.0f} | ${current_month:,.0f} | {top_services_str} | {budget_status} | {stopped_ec2} | {unused_volumes} | {unused_eips} | ${potential_savings:,.0f} | {untagged_resources} |\n"

        # Add summary section
        markdown_content += f"""

## Organization Summary

### Cost Trends
- **Month-over-Month Change**: {self._calculate_mom_change(multi_profile_data):.1f}%
- **Highest Cost Account**: {self._get_highest_cost_account(multi_profile_data)}
- **Most Opportunities**: {self._get_most_optimization_account(multi_profile_data)}

### Optimization Recommendations
1. **Immediate Actions**: Review {sum(p.get("stopped_ec2", 0) for p in multi_profile_data)} stopped EC2 instances
2. **Storage Cleanup**: Clean up {sum(p.get("unused_volumes", 0) for p in multi_profile_data)} unused EBS volumes
3. **Network Optimization**: Release {sum(p.get("unused_eips", 0) for p in multi_profile_data)} unused Elastic IPs
4. **Governance**: Tag {sum(p.get("untagged_resources", 0) for p in multi_profile_data)} untagged resources

---
*Generated by CloudOps Runbooks FinOps Module v0.7.8*
"""

        return markdown_content

    def export_to_file(self, markdown_content: str, filename: str, account_type: str = "single") -> str:
        """
        Export markdown content to file with intelligent naming.

        Args:
            markdown_content: Markdown content to export
            filename: Base filename (without extension)
            account_type: Type of analysis (single, multi, organization)

        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not filename.endswith(".md"):
            filename = f"{filename}_{account_type}_account_{timestamp}.md"

        filepath = self.output_dir / filename

        # Show progress indication
        print_info(f"📝 Generating markdown export: {filename}")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            print_success(f"Rich-styled markdown export saved: {filepath}")
            print_info(f"🔗 Ready for MkDocs or GitHub documentation sharing")
            return str(filepath)

        except Exception as e:
            print_warning(f"Failed to save markdown export: {e}")
            return ""

    def _get_cost_status_emoji(self, cost: float) -> str:
        """Get emoji based on cost level."""
        if cost >= 10000:
            return "🔴 High"
        elif cost >= 1000:
            return "🟡 Medium"
        else:
            return "🟢 Low"

    def _get_trend_emoji(self, trend: str) -> str:
        """Get emoji for cost trend."""
        trend_lower = trend.lower()
        if "up" in trend_lower or "increas" in trend_lower:
            return "📈"
        elif "down" in trend_lower or "decreas" in trend_lower:
            return "📉"
        else:
            return "➡️"

    def _get_budget_status_emoji(self, status: str) -> str:
        """Get emoji for budget status."""
        status_lower = status.lower()
        if "over" in status_lower or "exceeded" in status_lower:
            return "❌ Over"
        elif "warn" in status_lower:
            return "⚠️ Warn"
        elif "ok" in status_lower or "good" in status_lower:
            return "✅ OK"
        else:
            return "❓ Unknown"

    def _calculate_mom_change(self, profiles: List[Dict[str, Any]]) -> float:
        """Calculate month-over-month change percentage."""
        total_current = sum(p.get("total_cost", 0) for p in profiles)
        total_last = sum(p.get("last_month_cost", 0) for p in profiles)

        if total_last == 0:
            return 0.0

        return ((total_current - total_last) / total_last) * 100

    def _get_highest_cost_account(self, profiles: List[Dict[str, Any]]) -> str:
        """Get the account with highest cost."""
        if not profiles:
            return "N/A"

        highest = max(profiles, key=lambda p: p.get("total_cost", 0))
        return highest.get("profile_name", "Unknown")[:20]

    def _get_most_optimization_account(self, profiles: List[Dict[str, Any]]) -> str:
        """Get the account with most optimization opportunities."""
        if not profiles:
            return "N/A"

        highest = max(profiles, key=lambda p: p.get("potential_savings", 0))
        return highest.get("profile_name", "Unknown")[:20]


def export_finops_to_markdown(
    profile_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    output_dir: str = "./exports",
    filename: str = "finops_analysis",
    account_type: str = "auto",
) -> str:
    """
    Export FinOps analysis to markdown format.

    Args:
        profile_data: Single profile dict or list of profiles
        output_dir: Output directory for exports
        filename: Base filename for export
        account_type: Type of analysis (single, multi, auto)

    Returns:
        Path to exported markdown file
    """
    exporter = MarkdownExporter(output_dir)

    # Determine account type if auto
    if account_type == "auto":
        account_type = "multi" if isinstance(profile_data, list) else "single"

    # Generate appropriate markdown content
    if account_type == "single" and isinstance(profile_data, dict):
        markdown_content = exporter.create_single_account_export(
            profile_data, profile_data.get("account_id", "Unknown"), profile_data.get("profile_name", "Unknown")
        )
    elif account_type == "multi" and isinstance(profile_data, list):
        markdown_content = exporter.create_multi_account_export(profile_data)
    else:
        raise ValueError(f"Invalid combination: account_type={account_type}, data_type={type(profile_data)}")

    # Export to file
    return exporter.export_to_file(markdown_content, filename, account_type)


# Export public interface
__all__ = ["MarkdownExporter", "export_finops_to_markdown"]
