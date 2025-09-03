"""
Report generation for Cloud Foundations Assessment Tool.

This module provides various report formats including HTML, CSV, and JSON
for assessment results.
"""

from pathlib import Path
from typing import Union

from loguru import logger

from runbooks.cfat.models import AssessmentReport, CheckStatus, Severity


class HTMLReportGenerator:
    """Generate HTML reports for CFAT assessments."""

    def __init__(self, report: AssessmentReport):
        """Initialize with assessment report."""
        self.report = report

    def generate(self, file_path: Union[str, Path]) -> None:
        """Generate HTML report file."""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self._generate_html()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {output_path}")

    def _generate_html(self) -> str:
        """Generate the complete HTML content."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Foundations Assessment Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_summary()}
        {self._generate_results_table()}
        {self._generate_recommendations()}
        {self._generate_footer()}
    </div>
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""

    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header .subtitle {
            margin-top: 10px;
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .summary {
            padding: 30px;
            background-color: #fafafa;
            border-bottom: 1px solid #eee;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .summary-card .label {
            color: #666;
            font-size: 0.9em;
        }
        
        .pass { color: #4CAF50; }
        .fail { color: #f44336; }
        .warning { color: #ff9800; }
        .critical { color: #d32f2f; }
        .info { color: #2196F3; }
        
        .results {
            padding: 30px;
        }
        
        .filters {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .filter-btn:hover {
            background: #f0f0f0;
        }
        
        .filter-btn.active {
            background: #2196F3;
            color: white;
            border-color: #2196F3;
        }
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .results-table th,
        .results-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .results-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
        }
        
        .results-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-pass {
            background-color: #e8f5e8;
            color: #2e7d32;
        }
        
        .status-fail {
            background-color: #ffebee;
            color: #c62828;
        }
        
        .status-error {
            background-color: #fff3e0;
            color: #ef6c00;
        }
        
        .severity-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .severity-info {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        .severity-warning {
            background-color: #fff8e1;
            color: #f57c00;
        }
        
        .severity-critical {
            background-color: #ffebee;
            color: #d32f2f;
        }
        
        .recommendations {
            padding: 30px;
            background-color: #f8f9fa;
        }
        
        .footer {
            padding: 20px 30px;
            background-color: #666;
            color: white;
            text-align: center;
            font-size: 0.9em;
        }
        
        .expandable {
            cursor: pointer;
        }
        
        .details {
            display: none;
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary,
            .results {
                padding: 20px;
            }
            
            .results-table {
                font-size: 0.9em;
            }
        }
        """

    def _generate_header(self) -> str:
        """Generate the report header."""
        return f"""
        <div class="header">
            <h1>Cloud Foundations Assessment Report</h1>
            <div class="subtitle">
                Account: {self.report.account_id} | 
                Region: {self.report.region} | 
                Generated: {self.report.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>
        """

    def _generate_summary(self) -> str:
        """Generate the summary section."""
        summary = self.report.summary

        return f"""
        <div class="summary">
            <h2>Assessment Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="number">{summary.total_checks}</div>
                    <div class="label">Total Checks</div>
                </div>
                <div class="summary-card">
                    <div class="number pass">{summary.passed_checks}</div>
                    <div class="label">Passed</div>
                </div>
                <div class="summary-card">
                    <div class="number fail">{summary.failed_checks}</div>
                    <div class="label">Failed</div>
                </div>
                <div class="summary-card">
                    <div class="number warning">{summary.warnings}</div>
                    <div class="label">Warnings</div>
                </div>
                <div class="summary-card">
                    <div class="number critical">{summary.critical_issues}</div>
                    <div class="label">Critical Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number info">{summary.pass_rate:.1f}%</div>
                    <div class="label">Pass Rate</div>
                </div>
            </div>
        </div>
        """

    def _generate_results_table(self) -> str:
        """Generate the results table."""
        table_rows = ""

        for result in self.report.results:
            status_class = f"status-{result.status.value.lower()}"
            severity_class = f"severity-{result.severity.value.lower()}"

            table_rows += f"""
            <tr class="result-row expandable" onclick="toggleDetails(this)">
                <td>{result.check_name}</td>
                <td>{result.check_category}</td>
                <td><span class="status-badge {status_class}">{result.status.value}</span></td>
                <td><span class="severity-badge {severity_class}">{result.severity.value}</span></td>
                <td>{result.message}</td>
                <td>{result.execution_time:.2f}s</td>
            </tr>
            """

            if result.recommendations:
                recommendations_html = "<ul>" + "".join(f"<li>{rec}</li>" for rec in result.recommendations) + "</ul>"
                table_rows += f"""
                <tr class="details-row">
                    <td colspan="6">
                        <div class="details">
                            <strong>Recommendations:</strong>
                            {recommendations_html}
                        </div>
                    </td>
                </tr>
                """

        return f"""
        <div class="results">
            <h2>Assessment Results</h2>
            <div class="filters">
                <button class="filter-btn active" onclick="filterResults('all')">All</button>
                <button class="filter-btn" onclick="filterResults('fail')">Failed</button>
                <button class="filter-btn" onclick="filterResults('pass')">Passed</button>
                <button class="filter-btn" onclick="filterResults('critical')">Critical</button>
                <button class="filter-btn" onclick="filterResults('warning')">Warning</button>
            </div>
            
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Check Name</th>
                        <th>Category</th>
                        <th>Status</th>
                        <th>Severity</th>
                        <th>Message</th>
                        <th>Execution Time</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        failed_results = self.report.get_failed_results()

        if not failed_results:
            return """
            <div class="recommendations">
                <h2>Recommendations</h2>
                <p>Congratulations! All assessment checks passed successfully.</p>
            </div>
            """

        recommendations_html = ""
        for result in failed_results:
            if result.recommendations:
                recommendations_html += f"""
                <div class="recommendation-item">
                    <h4>{result.check_name}</h4>
                    <ul>
                        {"".join(f"<li>{rec}</li>" for rec in result.recommendations)}
                    </ul>
                </div>
                """

        return f"""
        <div class="recommendations">
            <h2>Recommendations</h2>
            <p>Based on the assessment results, here are the recommended actions to improve your AWS account security and compliance:</p>
            {recommendations_html}
        </div>
        """

    def _generate_footer(self) -> str:
        """Generate the report footer."""
        return f"""
        <div class="footer">
            Generated by CloudOps Runbooks v{self.report.version} | 
            Execution time: {self.report.summary.total_execution_time:.1f}s |
            Profile: {self.report.profile}
        </div>
        """

    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features."""
        return """
        function toggleDetails(row) {
            const detailsRow = row.nextElementSibling;
            if (detailsRow && detailsRow.classList.contains('details-row')) {
                const details = detailsRow.querySelector('.details');
                if (details.style.display === 'none' || details.style.display === '') {
                    details.style.display = 'block';
                } else {
                    details.style.display = 'none';
                }
            }
        }
        
        function filterResults(filter) {
            const rows = document.querySelectorAll('.result-row');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update active button
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            rows.forEach(row => {
                const statusBadge = row.querySelector('.status-badge');
                const severityBadge = row.querySelector('.severity-badge');
                const detailsRow = row.nextElementSibling;
                
                let show = false;
                
                if (filter === 'all') {
                    show = true;
                } else if (filter === 'fail') {
                    show = statusBadge && statusBadge.textContent.toLowerCase() === 'fail';
                } else if (filter === 'pass') {
                    show = statusBadge && statusBadge.textContent.toLowerCase() === 'pass';
                } else if (filter === 'critical') {
                    show = severityBadge && severityBadge.textContent.toLowerCase() === 'critical';
                } else if (filter === 'warning') {
                    show = severityBadge && severityBadge.textContent.toLowerCase() === 'warning';
                }
                
                row.style.display = show ? '' : 'none';
                if (detailsRow && detailsRow.classList.contains('details-row')) {
                    detailsRow.style.display = show ? '' : 'none';
                }
            });
        }
        
        // Initialize details as hidden
        document.addEventListener('DOMContentLoaded', function() {
            const details = document.querySelectorAll('.details');
            details.forEach(detail => {
                detail.style.display = 'none';
            });
        });
        """
