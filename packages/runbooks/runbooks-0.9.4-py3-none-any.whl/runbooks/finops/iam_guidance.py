#!/usr/bin/env python3
"""
Enhanced Exception Handling with IAM/SSO Role Requirements
Enterprise-grade error messaging with actionable guidance for AWS permissions.
"""

import re
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class EnterpriseIAMGuidance:
    """Provides clear IAM/SSO role requirements and troubleshooting guidance."""

    # AWS API Permission Requirements for Runbooks Operations
    # ANY AWS profile needs these specific API permissions to run runbooks commands
    RUNBOOKS_API_REQUIREMENTS = {
        # FinOps Operations
        "ce:GetCostAndUsage": {
            "purpose": "Retrieve cost and usage data from Cost Explorer",
            "functionality_impact": "Cost analysis, spending trends, budget reports",
            "command_impact": "runbooks finops (dashboard, trend analysis)",
            "aws_managed_policies": ["AWBillingReadOnlyAccess", "AWCostExplorerServiceRolePolicy"],
        },
        "budgets:ViewBudget": {
            "purpose": "Access budget information and alerts",
            "functionality_impact": "Budget status, alerts, spending limits",
            "command_impact": "runbooks finops (budget dashboard)",
            "aws_managed_policies": ["AWBillingReadOnlyAccess"],
        },
        # Resource Discovery Operations
        "ec2:DescribeInstances": {
            "purpose": "List and describe EC2 instances",
            "functionality_impact": "Instance inventory, cost allocation, resource optimization",
            "command_impact": "runbooks inventory, runbooks operate ec2",
            "aws_managed_policies": ["ReadOnlyAccess", "EC2ReadOnlyAccess"],
        },
        "ec2:DescribeRegions": {
            "purpose": "List available AWS regions",
            "functionality_impact": "Multi-region resource discovery",
            "command_impact": "runbooks inventory (region scanning)",
            "aws_managed_policies": ["ReadOnlyAccess"],
        },
        "sts:GetCallerIdentity": {
            "purpose": "Retrieve AWS account ID and user information",
            "functionality_impact": "Account verification, audit trails",
            "command_impact": "All runbooks commands (account identification)",
            "aws_managed_policies": ["ReadOnlyAccess"],
        },
        "ec2:DescribeVolumes": {
            "purpose": "List and describe EBS volumes",
            "functionality_impact": "Storage cost analysis, orphaned volume detection",
            "command_impact": "runbooks inventory, runbooks operate ebs",
            "aws_managed_policies": ["ReadOnlyAccess", "EC2ReadOnlyAccess"],
        },
        "ec2:DescribeAddresses": {
            "purpose": "List elastic IP addresses",
            "functionality_impact": "IP cost optimization, unused resource detection",
            "command_impact": "runbooks inventory, runbooks operate eip",
            "aws_managed_policies": ["ReadOnlyAccess", "EC2ReadOnlyAccess"],
        },
        "rds:DescribeDBInstances": {
            "purpose": "List and describe RDS database instances",
            "functionality_impact": "Database cost analysis, resource optimization",
            "command_impact": "runbooks inventory, runbooks operate rds",
            "aws_managed_policies": ["ReadOnlyAccess", "RDSReadOnlyAccess"],
        },
        "rds:ListTagsForResource": {
            "purpose": "Retrieve tags for RDS resources",
            "functionality_impact": "Cost allocation, compliance tracking",
            "command_impact": "runbooks inventory (tag-based filtering)",
            "aws_managed_policies": ["ReadOnlyAccess", "RDSReadOnlyAccess"],
        },
        "lambda:ListFunctions": {
            "purpose": "List Lambda functions",
            "functionality_impact": "Serverless cost analysis, function inventory",
            "command_impact": "runbooks inventory, runbooks operate lambda",
            "aws_managed_policies": ["ReadOnlyAccess", "AWSLambda_ReadOnlyAccess"],
        },
        "lambda:ListTags": {
            "purpose": "Retrieve tags for Lambda functions",
            "functionality_impact": "Cost allocation, resource organization",
            "command_impact": "runbooks inventory (Lambda tag analysis)",
            "aws_managed_policies": ["ReadOnlyAccess", "AWSLambda_ReadOnlyAccess"],
        },
        "elbv2:DescribeLoadBalancers": {
            "purpose": "List and describe Application Load Balancers",
            "functionality_impact": "Load balancer cost analysis, traffic optimization",
            "command_impact": "runbooks inventory, runbooks operate alb",
            "aws_managed_policies": ["ReadOnlyAccess", "ElasticLoadBalancingReadOnly"],
        },
        "elbv2:DescribeTags": {
            "purpose": "Retrieve tags for load balancers",
            "functionality_impact": "Cost allocation, compliance tracking",
            "command_impact": "runbooks inventory (ALB tag analysis)",
            "aws_managed_policies": ["ReadOnlyAccess", "ElasticLoadBalancingReadOnly"],
        },
    }

    @staticmethod
    def parse_aws_error(error_message: str) -> Dict[str, str]:
        """Parse AWS error message to extract key components."""

        # Extract permission that was denied
        permission_match = re.search(r"perform: ([a-zA-Z0-9:*]+)", str(error_message))
        permission_denied = permission_match.group(1) if permission_match else "Unknown"

        # Extract resource ARN
        resource_match = re.search(r"resource: (arn:aws:[^)]+)", str(error_message))
        resource_arn = resource_match.group(1) if resource_match else "Unknown"

        # Extract user ARN
        user_match = re.search(r"User: (arn:aws:sts::[^)]+)", str(error_message))
        user_arn = user_match.group(1) if user_match else "Unknown"

        # Determine error type
        if "AccessDeniedException" in str(error_message):
            error_type = "Access Denied"
        elif "UnauthorizedOperation" in str(error_message):
            error_type = "Unauthorized Operation"
        elif "Token has expired" in str(error_message):
            error_type = "SSO Token Expired"
        else:
            error_type = "Permission Error"

        return {
            "error_type": error_type,
            "permission_denied": permission_denied,
            "resource_arn": resource_arn,
            "user_arn": user_arn,
        }

    @classmethod
    def get_permission_guidance(cls, permission_denied: str) -> Optional[Dict]:
        """Get specific guidance for the denied AWS API permission."""

        # Direct permission match
        if permission_denied in cls.RUNBOOKS_API_REQUIREMENTS:
            return cls.RUNBOOKS_API_REQUIREMENTS[permission_denied]

        # Pattern matching for wildcard permissions (e.g., ec2:Describe* matches ec2:DescribeInstances)
        for api_permission, config in cls.RUNBOOKS_API_REQUIREMENTS.items():
            permission_prefix = api_permission.split(":")[0]
            denied_prefix = permission_denied.split(":")[0]

            if permission_prefix == denied_prefix:
                # Same service, likely related permission
                return config

        return None

    @classmethod
    def display_enhanced_error(cls, error: Exception, operation_context: str = "runbooks operation"):
        """Display enterprise-grade error message with actionable guidance."""

        error_details = cls.parse_aws_error(str(error))
        permission_guidance = cls.get_permission_guidance(error_details["permission_denied"])

        # Create main error panel
        error_panel = Panel(
            f"[red]❌ {error_details['error_type']}: {error_details['permission_denied']}[/red]\n\n"
            f"[yellow]Operation:[/yellow] {operation_context}\n"
            f"[yellow]Resource:[/yellow] {error_details['resource_arn']}\n"
            f"[yellow]User:[/yellow] {error_details['user_arn']}",
            title="🚨 AWS Permission Error",
            border_style="red",
        )
        console.print(error_panel)

        # Display specific guidance if available
        if permission_guidance:
            cls._display_permission_requirements(error_details["permission_denied"], permission_guidance)
        else:
            cls._display_general_guidance(error_details["permission_denied"])

        # Display troubleshooting steps
        cls._display_troubleshooting_steps(error_details["error_type"])

    @classmethod
    def _display_permission_requirements(cls, permission_denied: str, permission_config: Dict):
        """Display specific AWS API permission requirements and impact."""

        # Permission impact table
        impact_table = Table(title=f"📋 AWS API Permission Analysis: {permission_denied}")
        impact_table.add_column("Aspect", style="bold cyan")
        impact_table.add_column("Details", style="white")

        impact_table.add_row("Permission", permission_denied)
        impact_table.add_row("Purpose", permission_config["purpose"])
        impact_table.add_row("Functionality Impact", permission_config["functionality_impact"])
        impact_table.add_row("Affected Commands", permission_config["command_impact"])

        console.print(impact_table)

        # Solution panel
        solution_panel = Panel(
            f"[green]✅ IAM/SSO Configuration Required:[/green]\n\n"
            f"1. **Required Permission**: `{permission_denied}`\n"
            f"2. **Add to IAM Policy**: Include this permission in your IAM role/policy\n"
            f"3. **SSO Configuration**: Ensure your SSO role includes this permission\n"
            f"4. **SCP Compliance**: Verify Service Control Policies don't deny this permission\n\n"
            f"[bold]AWS Managed Policies (containing this permission):[/bold]\n"
            + "\n".join([f"• {policy}" for policy in permission_config["aws_managed_policies"]]),
            title="🔧 Permission Resolution Guidance",
            border_style="green",
        )
        console.print(solution_panel)

    @classmethod
    def _display_general_guidance(cls, permission_denied: str):
        """Display general IAM guidance for unknown permissions."""

        guidance_panel = Panel(
            f"[yellow]⚠️  Permission Required: {permission_denied}[/yellow]\n\n"
            f"[bold]General Resolution Steps:[/bold]\n"
            f"• **IAM Policy**: Add `{permission_denied}` to your IAM role/policy\n"
            f"• **SSO Role**: Ensure your AWS SSO role includes this permission\n"
            f"• **SCP Review**: Check Service Control Policies don't deny this permission\n"
            f"• **Resource Policy**: Verify resource-based policies allow access\n"
            f"• **Console Test**: Test this permission via AWS Console first\n\n"
            f"[bold]Common Solutions:[/bold]\n"
            f"• Attach AWS managed policy: `ReadOnlyAccess`\n"
            f"• Create custom policy with this specific permission\n"
            f"• Contact your AWS administrator for permission escalation",
            title="📋 Permission Resolution Guidance",
            border_style="yellow",
        )
        console.print(guidance_panel)

    @classmethod
    def _display_troubleshooting_steps(cls, error_type: str):
        """Display troubleshooting steps based on error type."""

        if error_type == "SSO Token Expired":
            troubleshooting = (
                "[bold]🔄 SSO Token Refresh Steps:[/bold]\n"
                "1. Run: `aws sso login --profile your-profile-name`\n"
                "2. Follow browser authentication flow\n"
                "3. Retry the runbooks operation\n"
                "4. Consider extending SSO session duration in AWS SSO settings"
            )
        else:
            troubleshooting = (
                "[bold]🛠️ Permission Resolution Steps:[/bold]\n"
                "1. **Verify Profile**: Check `aws sts get-caller-identity --profile your-profile`\n"
                "2. **Review IAM Policy**: Ensure your role has the required permission\n"
                "3. **Check SCP**: Verify Service Control Policies allow this action\n"
                "4. **Test Console Access**: Try the same operation in AWS Console\n"
                "5. **Contact Administrator**: Request IAM policy update with required permission"
            )

        troubleshoot_panel = Panel(troubleshooting, title="🔧 Next Steps", border_style="blue")
        console.print(troubleshoot_panel)

    @classmethod
    def display_runbooks_permission_requirements(cls):
        """Display complete runbooks AWS API permission requirements."""

        matrix_table = Table(title="🔧 Runbooks AWS API Permission Requirements")
        matrix_table.add_column("AWS API Permission", style="bold cyan")
        matrix_table.add_column("Purpose", style="white")
        matrix_table.add_column("Affected Commands", style="green")
        matrix_table.add_column("AWS Managed Policy", style="yellow")

        for permission, config in cls.RUNBOOKS_API_REQUIREMENTS.items():
            policies = ", ".join(config["aws_managed_policies"][:2]) + (
                "..." if len(config["aws_managed_policies"]) > 2 else ""
            )
            matrix_table.add_row(permission, config["purpose"], config["command_impact"], policies)

        console.print(matrix_table)

        # Enterprise guidance
        enterprise_panel = Panel(
            "[bold]🎯 IAM Configuration Best Practices:[/bold]\n\n"
            "• **Any AWS Profile**: Requires these specific API permissions to run runbooks\n"
            "• **SSO Integration**: Configure SSO roles with required permissions\n"
            "• **SCP Compliance**: Ensure Service Control Policies don't deny these permissions\n\n"
            "[bold]🔒 Security Notes:[/bold]\n"
            "• All permissions are ReadOnly - no destructive operations possible\n"
            "• Permissions follow least-privilege principle\n"
            "• IAM policies can be customized based on specific runbooks usage",
            title="🔧 Runbooks Permission Configuration",
            border_style="cyan",
        )
        console.print(enterprise_panel)


# Enhanced Cost Explorer Error Handling for Single Account Scenarios
def handle_cost_explorer_error(error: Exception, profile_name: Optional[str] = None):
    """
    Handle Cost Explorer specific errors with context-aware guidance for single accounts.

    Provides enhanced error messaging that explains why single accounts typically
    don't have Cost Explorer access and suggests practical solutions.
    """
    error_str = str(error)

    # Check if this is a single account Cost Explorer access issue
    if ("AccessDeniedException" in error_str or "explicitly denied" in error_str) and "ce:GetCostAndUsage" in error_str:
        _display_single_account_cost_explorer_guidance(error, profile_name)
    else:
        # Fall back to general IAM guidance
        EnterpriseIAMGuidance.display_enhanced_error(error, "runbooks finops operation (Cost Explorer API)")


def _display_single_account_cost_explorer_guidance(error: Exception, profile_name: Optional[str] = None):
    """Display context-aware guidance for single account Cost Explorer limitations."""

    # Main explanation panel
    explanation_panel = Panel(
        "[yellow]ℹ️  Cost Explorer Access Limitation[/yellow]\n\n"
        "[bold]What's happening:[/bold]\n"
        "• Individual AWS accounts often don't have Cost Explorer API permissions\n"
        "• Cost Explorer is typically accessible through the billing/payer account\n"
        "• This is expected behavior for member accounts in AWS Organizations\n\n"
        "[bold]Why this occurs:[/bold]\n"
        "• Cost Explorer requires specific billing permissions\n"
        "• Member accounts may not have consolidated billing access\n"
        "• Service Control Policies (SCPs) may restrict Cost Explorer access",
        title="🔍 Single Account Cost Explorer Context",
        border_style="yellow",
    )
    console.print(explanation_panel)

    # Solution panel with actionable guidance
    if profile_name:
        profile_text = f"your current profile `{profile_name}`"
        solution_commands = f"""[bold]Option 1: Use Billing Profile (Recommended)[/bold]
• Set environment variable: `export BILLING_PROFILE="your-billing-profile-name"`
• Run: `runbooks finops --profile your-billing-profile-name`

[bold]Option 2: Use Your Current Profile for Resource Analysis[/bold]
• Current profile: `{profile_name}`
• Resource discovery will work, but cost data will be limited
• Consider using: `runbooks inventory collect --profile {profile_name}`"""
    else:
        profile_text = "your current profile"
        solution_commands = """[bold]Option 1: Use Billing Profile (Recommended)[/bold]
• Set environment variable: `export BILLING_PROFILE="your-billing-profile-name"`
• Run: `runbooks finops --profile your-billing-profile-name`

[bold]Option 2: Request Billing Account Access[/bold]
• Contact your AWS administrator
• Request access to the organization's billing account
• Use that profile for Cost Explorer operations"""

    solution_panel = Panel(
        f"[green]✅ Recommended Solutions:[/green]\n\n"
        f"{solution_commands}\n\n"
        f"[bold]🎯 Quick Test Commands:[/bold]\n"
        f"• Test billing access: `aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-02 --granularity MONTHLY --metrics UnblendedCost --profile your-billing-profile`\n"
        f"• List available profiles: `aws configure list-profiles`\n"
        f"• Check current identity: `aws sts get-caller-identity --profile {profile_name or 'your-profile'}`\n\n"
        f"[bold]💡 Alternative Approach:[/bold]\n"
        f"• Use resource-based analysis: `runbooks inventory collect`\n"
        f"• Focus on resource optimization rather than cost analysis\n"
        f"• Generate resource reports for cost discussions with billing team",
        title="🔧 Cost Explorer Access Solutions",
        border_style="green",
    )
    console.print(solution_panel)

    # Enterprise context panel
    enterprise_context = Panel(
        "[bold]🏢 Enterprise Context:[/bold]\n\n"
        "• **Single Account Limitations**: Member accounts typically lack billing permissions\n"
        "• **Billing Account Access**: Contact your cloud team for billing profile access\n"
        "• **Alternative Analysis**: Resource inventory can provide optimization insights\n"
        "• **Cost Management**: Consider AWS Cost and Usage Reports (CUR) for detailed analysis\n\n"
        "[bold]📊 What You Can Still Do:[/bold]\n"
        "• Resource discovery and optimization recommendations\n"
        "• Security compliance scanning and remediation\n"
        "• Infrastructure inventory and tagging analysis\n"
        "• Performance monitoring and optimization guidance",
        title="🎯 Enterprise Guidance",
        border_style="cyan",
    )
    console.print(enterprise_context)


# Original convenience functions maintained for compatibility
def handle_cost_explorer_error_simple(error: Exception):
    """Handle Cost Explorer specific errors with guidance (legacy function)."""
    EnterpriseIAMGuidance.display_enhanced_error(error, "runbooks finops operation (Cost Explorer API)")


def handle_organizations_error(error: Exception):
    """Handle AWS Organizations specific errors with guidance."""
    EnterpriseIAMGuidance.display_enhanced_error(error, "runbooks inventory operation (Organizations API)")


def handle_resource_discovery_error(error: Exception):
    """Handle resource discovery specific errors with guidance."""
    EnterpriseIAMGuidance.display_enhanced_error(error, "runbooks inventory operation (Resource Discovery APIs)")
