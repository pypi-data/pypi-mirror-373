import datetime
import importlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
import botocore

from runbooks.common.profile_utils import create_management_session
from runbooks.common.rich_utils import (
    STATUS_INDICATORS,
    console,
    create_panel,
    create_progress_bar,
    create_table,
    print_error,
    print_info,
    print_status,
    print_success,
    print_warning,
)

from . import (
    checklist,  # noqa: F403
    report_generator,
)
from .security_export import SecurityExporter
from .utils import common, language, level_const

# from .utils.language import get_translator


class SecurityBaselineTester:
    def __init__(self, profile, lang_code, output_dir, export_formats: List[str] = None):
        self.profile = profile
        self.language = lang_code
        self.output = output_dir
        self.export_formats = export_formats or ["json", "csv"]
        self.session = self._create_session()
        self.config = self._load_config()
        self.exporter = SecurityExporter(output_dir)
        ## Call module 'language' and pass the string 'lang_code'
        self.translator = language.get_translator("main", lang_code)

    def _create_session(self):
        # Use enterprise profile management for security operations (management profile for cross-account)
        return create_management_session(profile=self.profile)

    def _load_config(self):
        ## Get the absolute directory where *this script* is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.json")

        try:
            # with open("./config.json", "r") as file:
            with open(config_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("config.json file not found. Please ensure it exists in the same directory as this script.")
            raise
        except json.JSONDecodeError:
            logging.error("Error parsing config.json. Please ensure it is a valid JSON file.")
            raise

    def run(self):
        """Execute the security baseline assessment with Rich CLI output."""
        try:
            # Print security assessment header
            console.print(
                create_panel(
                    "[bold cyan]AWS Security Baseline Assessment[/bold cyan]\n\n"
                    f"[dim]Profile: {self.profile} | Language: {self.language}[/dim]",
                    title="🛡️ Starting Security Assessment",
                    border_style="cyan",
                )
            )

            self._validate_session()
            caller_identity = self._get_caller_identity()
            self._print_auditor_info(caller_identity)

            print_info("Initiating comprehensive security baseline tests...")

            account_id, results = self._execute_tests()
            self._generate_report(account_id, results)

            # Export results in multiple formats
            if self.export_formats:
                print_info("Exporting security assessment results...")
                self.exporter.export_security_results(
                    account_id=account_id, results=results, language=self.language, formats=self.export_formats
                )

            print_success("Security baseline assessment completed successfully!")

        except Exception as e:
            print_error(f"Security baseline test failed: {str(e)}", exception=e)
            logging.error(f"An error occurred during the security baseline test: {str(e)}", exc_info=True)
            raise

    def _validate_session(self):
        if self.session.region_name is None:
            raise ValueError('AWS region is not specified. Run "aws configure" to set it.')

    def _get_caller_identity(self):
        try:
            return self.session.client("sts").get_caller_identity()
        except botocore.exceptions.ClientError as e:
            logging.error(f"Failed to get caller identity: {str(e)}")
            raise

    def _print_auditor_info(self, caller_identity):
        """Display auditor information with Rich formatting."""
        auditor_info = f"""[bold cyan]User ID:[/bold cyan] {caller_identity["UserId"]}
[bold cyan]Account:[/bold cyan] {caller_identity["Account"]}
[bold cyan]ARN:[/bold cyan] {caller_identity["Arn"]}"""

        console.print(
            create_panel(auditor_info, title="🔐 Security Assessment Context", border_style="cyan", padding=1)
        )

    def _execute_tests(self):
        iam_client = self.session.client("iam")
        sts_client = self.session.client("sts")

        account_id = common.get_account_id(sts_client)
        print_info(f"Generating credential report for account {account_id}")
        credential_report = common.generate_credential_report(iam_client)

        # Create progress bar for security checks
        checks = self.config.get("checks", [])
        total_checks = len(checks)

        with create_progress_bar(description="Security Assessment") as progress:
            task = progress.add_task("Running security checks...", total=total_checks)

            with ThreadPoolExecutor(max_workers=self.config.get("max_workers", 5)) as executor:
                futures = {
                    executor.submit(self._run_check, check_name, credential_report): check_name for check_name in checks
                }

                results = {
                    level: [] for level in ["Success", "Warning", "Danger", "Error", "Info"] if isinstance(level, str)
                }
                completed_checks = 0

                for future in as_completed(futures):
                    result = future.result()
                    results[result.level].append(result)
                    completed_checks += 1
                    progress.update(task, completed=completed_checks)

        # Display security assessment summary
        self._display_security_summary(results, total_checks)
        return account_id, results

    def _display_security_summary(self, results: Dict[str, List], total_checks: int):
        """Display security assessment summary with Rich formatting."""
        # Create summary table
        summary_table = create_table(
            title="🛡️ Security Assessment Summary",
            columns=[
                {"name": "Status", "style": "bold", "justify": "left"},
                {"name": "Count", "style": "bold", "justify": "center"},
                {"name": "Percentage", "style": "dim", "justify": "right"},
            ],
        )

        # Calculate statistics
        for level in ["Danger", "Warning", "Success", "Info", "Error"]:
            count = len(results.get(level, []))
            if total_checks > 0:
                percentage = (count / total_checks) * 100
                percentage_str = f"{percentage:.1f}%"
            else:
                percentage_str = "0%"

            # Style based on level
            if level == "Danger":
                status_text = f"🔴 {level}"
                style = "error"
            elif level == "Warning":
                status_text = f"🟡 {level}"
                style = "warning"
            elif level == "Success":
                status_text = f"🟢 {level}"
                style = "success"
            elif level == "Info":
                status_text = f"🔵 {level}"
                style = "info"
            else:  # Error
                status_text = f"❌ {level}"
                style = "critical"

            summary_table.add_row(status_text, str(count), percentage_str, style=style)

        console.print(summary_table)

        # Calculate overall security score
        total_issues = len(results.get("Danger", [])) + len(results.get("Warning", []))
        total_success = len(results.get("Success", []))

        if total_checks > 0:
            security_score = (total_success / total_checks) * 100
            if security_score >= 90:
                score_style = "success"
                score_icon = "🛡️"
            elif security_score >= 75:
                score_style = "warning"
                score_icon = "⚠️"
            else:
                score_style = "error"
                score_icon = "🚨"

            score_summary = f"""[bold {score_style}]{score_icon} Overall Security Score: {security_score:.1f}%[/bold {score_style}]

[dim]Total Checks: {total_checks} | Issues Found: {total_issues} | Successful: {total_success}[/dim]"""

            console.print(create_panel(score_summary, title="Security Posture Assessment", border_style=score_style))

    def _run_check(self, check_name, credential_report):
        # check_module = __import__(f"checklist.{check_name}", fromlist=[check_name])
        check_module = importlib.import_module(f"runbooks.security.checklist.{check_name}")
        check_method = getattr(check_module, self.config["checks"][check_name])
        translator = language.get_translator(check_name, self.language)

        if check_name in [
            "alternate_contacts",
            "account_level_bucket_public_access",
            "bucket_public_access",
            "cloudwatch_alarm_configuration",
            "direct_attached_policy",
            "guardduty_enabled",
            "multi_region_instance_usage",
            "multi_region_trail",
            "trail_enabled",
            "iam_password_policy",
        ]:
            return check_method(self.session, translator)
        elif check_name in [
            "root_mfa",
            "root_usage",
            "root_access_key",
            "iam_user_mfa",
        ]:
            return check_method(self.session, translator, credential_report)
        elif check_name == "trusted_advisor":
            return check_method(translator)
        else:
            raise ValueError(f"Unknown check method: {check_name}")

    def _check_result_directory(self):
        """
        Ensures that the 'results' directory (located next to this script) exists.

        :return: A Path object pointing to the results directory.
        """

        # directory_name = "./results"
        # if not os.path.exists(directory_name):
        #     os.makedirs(directory_name)
        #     logging.info(self.translator.translate("results_folder_created"))
        # else:
        #     logging.info(self.translator.translate("results_folder_already_exists"))

        ## ISSUE: creates results/ next to the module files in, e.g, .../site-packages/runbooks/security_baseline/results
        # script_dir = Path(__file__).resolve().parent
        # results_dir = script_dir / "results"
        ## Use the current working directory instead of the script directory
        if self.output:
            results_dir = Path(self.output).resolve()
        else:
            results_dir = Path.cwd() / "results"

        if not results_dir.exists():
            results_dir.mkdir(parents=True, exist_ok=True)
            print_info(f"Created results directory: {results_dir}")
        else:
            print_info(f"Using existing results directory: {results_dir}")

        return results_dir

    def _generate_report(self, account_id, results):
        """
        Generates an HTML security report and writes it to the 'results' directory.

        :param account_id: The AWS account ID or similar identifier.
        :param results:    A dictionary containing the security baseline results.
        """
        html_report = report_generator.generate_html_report(account_id, results, self.language)

        current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        short_account_id = account_id[-4:]

        ## Ensure the results directory exists
        results_dir = self._check_result_directory()

        ## Build the report filename
        report_filename = f"security-report-{short_account_id}-{current_time}.html"
        report_path = results_dir / report_filename

        ## Get the absolute directory where *this script* is located
        # test_report_dir = os.path.dirname(os.path.abspath(__file__))
        # test_report_path = os.path.join(test_report_dir, report_filename)

        # with open(test_report_path, "w") as file:
        ## Write the report to disk
        with report_path.open("w", encoding="utf-8") as file:
            file.write(html_report)

        # Display report generation success with Rich formatting
        report_success = f"""[bold green]Security Report Generated Successfully[/bold green]

[cyan]Report Location:[/cyan] {report_path}
[cyan]Account ID:[/cyan] {account_id}
[cyan]Language:[/cyan] {self.language}
[cyan]Report Time:[/cyan] {current_time}

[dim]Open the HTML report in your browser to view detailed findings.[/dim]"""

        console.print(create_panel(report_success, title="📊 Report Generation Complete", border_style="green"))

        print_success(f"HTML report saved to: {report_path}")
