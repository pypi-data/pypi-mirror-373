#!/usr/bin/env python3
"""
User Feedback Collection System for CloudOps Runbooks Platform.

Collects user feedback on Rich CLI improvements, performance, and feature usage
to drive continuous improvement and measure deployment success.

Features:
- CLI experience feedback collection
- Performance satisfaction tracking
- Feature usage analytics
- Terminal compatibility reporting
- A/B testing support for CLI improvements

Author: Enterprise Product Owner
Version: 1.0.0 - Phase 2 Production Deployment
"""

import json
import os
import platform
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


class UserFeedbackCollector:
    """
    Enterprise user feedback collection for CloudOps Runbooks platform.

    Collects structured feedback on Rich CLI enhancements, performance,
    and overall user experience to guide continuous improvement.
    """

    def __init__(self):
        """Initialize user feedback collection system."""
        self.feedback_file = Path("artifacts/feedback/user_feedback.json")
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

        self.session_id = str(uuid.uuid4())[:8]
        self.system_info = self._collect_system_info()

    def _collect_system_info(self) -> Dict[str, str]:
        """Collect system information for compatibility analysis."""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "terminal": os.environ.get("TERM", "unknown"),
            "terminal_program": os.environ.get("TERM_PROGRAM", "unknown"),
            "color_support": str(console.color_system),
            "width": str(console.size.width),
            "height": str(console.size.height),
        }

    def collect_cli_experience_feedback(self) -> Dict[str, Any]:
        """
        Collect feedback specifically on Rich CLI improvements.

        Returns:
            Structured feedback data
        """
        console.print(
            Panel(
                "[bold blue]📋 Rich CLI Experience Feedback[/bold blue]\n\n"
                "Help us improve the CloudOps Runbooks CLI experience!\n"
                "Your feedback drives our continuous improvement.",
                title="User Feedback Collection",
                border_style="blue",
            )
        )

        feedback = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_type": "cli_experience",
            "system_info": self.system_info,
        }

        # Overall satisfaction rating
        satisfaction = Prompt.ask(
            "\n[cyan]Overall CLI Experience Rating[/cyan] (1-10, where 10 is excellent)",
            choices=[str(i) for i in range(1, 11)],
            default="8",
        )
        feedback["overall_satisfaction"] = int(satisfaction)

        # Rich CLI specific feedback
        console.print("\n[yellow]📊 Rich CLI Features Feedback[/yellow]")

        # Color coding effectiveness
        color_rating = Prompt.ask(
            "How helpful are the color-coded messages? (1-10)", choices=[str(i) for i in range(1, 11)], default="8"
        )
        feedback["color_coding_rating"] = int(color_rating)

        # Progress indicators
        progress_rating = Prompt.ask(
            "How useful are the progress indicators? (1-10)", choices=[str(i) for i in range(1, 11)], default="8"
        )
        feedback["progress_indicators_rating"] = int(progress_rating)

        # Error messages clarity
        error_clarity = Prompt.ask(
            "How clear are the error messages? (1-10)", choices=[str(i) for i in range(1, 11)], default="8"
        )
        feedback["error_message_clarity"] = int(error_clarity)

        # Terminal compatibility
        compatibility_issues = Confirm.ask("\nDid you experience any display issues in your terminal?")
        feedback["compatibility_issues"] = compatibility_issues

        if compatibility_issues:
            issues_description = Prompt.ask(
                "Please describe the display issues (optional)", default="No description provided"
            )
            feedback["issues_description"] = issues_description

        # Feature usage
        console.print("\n[green]🚀 Feature Usage[/green]")

        modules_used = []
        available_modules = ["operate", "cfat", "inventory", "security", "finops", "vpc"]

        for module in available_modules:
            if Confirm.ask(f"Have you used the {module} module?"):
                modules_used.append(module)

        feedback["modules_used"] = modules_used

        # Most valuable features
        if modules_used:
            favorite_module = Prompt.ask(
                "Which module do you find most valuable?",
                choices=modules_used,
                default=modules_used[0] if modules_used else "operate",
            )
            feedback["favorite_module"] = favorite_module

        # Performance satisfaction
        console.print("\n[blue]⚡ Performance Feedback[/blue]")

        performance_rating = Prompt.ask(
            "How satisfied are you with operation speed? (1-10)", choices=[str(i) for i in range(1, 11)], default="8"
        )
        feedback["performance_satisfaction"] = int(performance_rating)

        # Free-form feedback
        console.print("\n[magenta]💬 Additional Feedback[/magenta]")

        improvements = Prompt.ask("What improvements would you like to see? (optional)", default="No suggestions")
        feedback["suggested_improvements"] = improvements

        # Recommendation likelihood (NPS-style)
        nps_score = Prompt.ask(
            "How likely are you to recommend CloudOps Runbooks? (0-10)",
            choices=[str(i) for i in range(0, 11)],
            default="8",
        )
        feedback["nps_score"] = int(nps_score)

        return feedback

    def collect_performance_feedback(self, module: str, operation: str, execution_time: float) -> Dict[str, Any]:
        """
        Collect performance-specific feedback after operations.

        Args:
            module: Module name that was used
            operation: Operation that was performed
            execution_time: Actual execution time

        Returns:
            Performance feedback data
        """
        feedback = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_type": "performance",
            "module": module,
            "operation": operation,
            "execution_time": execution_time,
            "system_info": self.system_info,
        }

        # Quick performance satisfaction
        performance_acceptable = Confirm.ask(
            f"\n[cyan]Was the {module} {operation} performance acceptable?[/cyan] (took {execution_time:.2f}s)"
        )
        feedback["performance_acceptable"] = performance_acceptable

        if not performance_acceptable:
            expected_time = Prompt.ask("What would be an acceptable time for this operation? (seconds)", default="5")
            feedback["expected_time"] = float(expected_time)

        return feedback

    def collect_feature_request(self) -> Dict[str, Any]:
        """
        Collect feature requests and enhancement suggestions.

        Returns:
            Feature request data
        """
        console.print(
            Panel(
                "[bold green]💡 Feature Request & Enhancement Ideas[/bold green]\n\n"
                "Share your ideas to help us enhance CloudOps Runbooks!",
                title="Feature Requests",
                border_style="green",
            )
        )

        feedback = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_type": "feature_request",
            "system_info": self.system_info,
        }

        # Feature category
        categories = ["cli_experience", "new_module", "performance", "reporting", "integration", "other"]
        category = Prompt.ask(
            "What category does your request fall into?", choices=categories, default="cli_experience"
        )
        feedback["category"] = category

        # Priority level
        priority = Prompt.ask(
            "How important is this to you?", choices=["low", "medium", "high", "critical"], default="medium"
        )
        feedback["priority"] = priority

        # Description
        description = Prompt.ask("Please describe your feature request or enhancement idea", default="Feature request")
        feedback["description"] = description

        # Use case
        use_case = Prompt.ask(
            "What problem would this solve or what value would it add?", default="General improvement"
        )
        feedback["use_case"] = use_case

        return feedback

    def store_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """
        Store feedback data to persistent storage.

        Args:
            feedback_data: Structured feedback data
        """
        try:
            # Load existing feedback
            if self.feedback_file.exists():
                with open(self.feedback_file, "r") as f:
                    all_feedback = json.load(f)
            else:
                all_feedback = {"feedback_entries": []}

            # Add new feedback
            all_feedback["feedback_entries"].append(feedback_data)

            # Save updated feedback
            with open(self.feedback_file, "w") as f:
                json.dump(all_feedback, f, indent=2)

            console.print(
                f"[green]✅ Thank you! Feedback saved (ID: {feedback_data.get('session_id', 'unknown')})[/green]"
            )

        except Exception as e:
            console.print(f"[red]❌ Error saving feedback: {e}[/red]")

    def analyze_feedback_trends(self) -> Dict[str, Any]:
        """
        Analyze collected feedback for trends and insights.

        Returns:
            Analysis results and trends
        """
        if not self.feedback_file.exists():
            return {"status": "no_data", "message": "No feedback data available"}

        try:
            with open(self.feedback_file, "r") as f:
                data = json.load(f)

            entries = data.get("feedback_entries", [])

            if not entries:
                return {"status": "no_entries", "message": "No feedback entries found"}

            # Overall statistics
            total_entries = len(entries)
            cli_feedback = [e for e in entries if e.get("feedback_type") == "cli_experience"]

            analysis = {
                "status": "success",
                "total_entries": total_entries,
                "analysis_date": datetime.now().isoformat(),
                "feedback_breakdown": {
                    "cli_experience": len([e for e in entries if e.get("feedback_type") == "cli_experience"]),
                    "performance": len([e for e in entries if e.get("feedback_type") == "performance"]),
                    "feature_request": len([e for e in entries if e.get("feedback_type") == "feature_request"]),
                },
            }

            # CLI experience analysis
            if cli_feedback:
                satisfaction_scores = [e.get("overall_satisfaction", 0) for e in cli_feedback]
                nps_scores = [e.get("nps_score", 0) for e in cli_feedback]
                color_ratings = [e.get("color_coding_rating", 0) for e in cli_feedback]

                analysis["cli_analysis"] = {
                    "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores),
                    "average_nps": sum(nps_scores) / len(nps_scores),
                    "average_color_rating": sum(color_ratings) / len(color_ratings),
                    "compatibility_issues_rate": sum(1 for e in cli_feedback if e.get("compatibility_issues", False))
                    / len(cli_feedback)
                    * 100,
                }

            # Module usage analysis
            module_usage = {}
            for entry in cli_feedback:
                modules = entry.get("modules_used", [])
                for module in modules:
                    module_usage[module] = module_usage.get(module, 0) + 1

            analysis["module_usage"] = module_usage

            # System compatibility
            systems = {}
            terminals = {}
            for entry in entries:
                sys_info = entry.get("system_info", {})
                system = sys_info.get("platform", "unknown")
                terminal = sys_info.get("terminal_program", "unknown")

                systems[system] = systems.get(system, 0) + 1
                terminals[terminal] = terminals.get(terminal, 0) + 1

            analysis["system_compatibility"] = {"platforms": systems, "terminals": terminals}

            return analysis

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def display_feedback_summary(self) -> None:
        """Display a formatted summary of feedback analysis."""
        analysis = self.analyze_feedback_trends()

        if analysis["status"] != "success":
            console.print(f"[yellow]⚠️  {analysis['message']}[/yellow]")
            return

        # Summary panel
        summary_panel = Panel(
            f"[green]Total Feedback Entries:[/green] {analysis['total_entries']}\n"
            f"[blue]CLI Experience:[/blue] {analysis['feedback_breakdown']['cli_experience']}\n"
            f"[cyan]Performance:[/cyan] {analysis['feedback_breakdown']['performance']}\n"
            f"[magenta]Feature Requests:[/magenta] {analysis['feedback_breakdown']['feature_request']}",
            title="📊 Feedback Summary",
            border_style="blue",
        )

        console.print(summary_panel)

        # CLI analysis
        if "cli_analysis" in analysis:
            cli_analysis = analysis["cli_analysis"]

            cli_panel = Panel(
                f"[green]Average Satisfaction:[/green] {cli_analysis['average_satisfaction']:.1f}/10\n"
                f"[blue]Average NPS Score:[/blue] {cli_analysis['average_nps']:.1f}/10\n"
                f"[cyan]Color Rating:[/cyan] {cli_analysis['average_color_rating']:.1f}/10\n"
                f"[yellow]Compatibility Issues:[/yellow] {cli_analysis['compatibility_issues_rate']:.1f}%",
                title="🎨 Rich CLI Analysis",
                border_style="green" if cli_analysis["average_satisfaction"] >= 8 else "yellow",
            )

            console.print(cli_panel)

        # Module usage table
        if analysis.get("module_usage"):
            usage_table = Table(title="Module Usage Popularity")
            usage_table.add_column("Module", style="bold")
            usage_table.add_column("Usage Count", justify="center")
            usage_table.add_column("Popularity", justify="center")

            total_usage = sum(analysis["module_usage"].values())

            for module, count in sorted(analysis["module_usage"].items(), key=lambda x: x[1], reverse=True):
                popularity = count / total_usage * 100
                usage_table.add_row(module.title(), str(count), f"{popularity:.1f}%")

            console.print(usage_table)


# Command-line interface for feedback collection
def main():
    """Main CLI interface for feedback collection."""
    collector = UserFeedbackCollector()

    console.print("[bold blue]🎯 CloudOps Runbooks Feedback System[/bold blue]")

    action = Prompt.ask(
        "\nWhat would you like to do?",
        choices=["give_feedback", "request_feature", "view_summary", "quit"],
        default="give_feedback",
    )

    if action == "give_feedback":
        feedback = collector.collect_cli_experience_feedback()
        collector.store_feedback(feedback)

    elif action == "request_feature":
        request = collector.collect_feature_request()
        collector.store_feedback(request)

    elif action == "view_summary":
        collector.display_feedback_summary()

    elif action == "quit":
        console.print("[dim]Thank you for using CloudOps Runbooks![/dim]")


if __name__ == "__main__":
    main()
