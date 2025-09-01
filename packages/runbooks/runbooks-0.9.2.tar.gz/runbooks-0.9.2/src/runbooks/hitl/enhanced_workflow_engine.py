#!/usr/bin/env python3
"""
Enhanced HITL Workflow Engine for Human-in-the-Loop Optimization

Issue #93: HITL System & DORA Metrics Optimization
Priority: High (Sprint 1 Improvements)
Scope: Streamlined approval workflows with ±15% cross-validation accuracy
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..metrics.dora_metrics_engine import DORAMetricsEngine
from ..utils.logger import configure_logger

logger = configure_logger(__name__)


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"


class WorkflowStep(Enum):
    VALIDATION = "validation"
    ARCHITECTURE_REVIEW = "architecture_review"
    SECURITY_REVIEW = "security_review"
    COST_ANALYSIS = "cost_analysis"
    MANAGER_APPROVAL = "manager_approval"
    DEPLOYMENT = "deployment"


@dataclass
class ApprovalRequest:
    """Approval request for HITL workflow"""

    request_id: str
    request_type: str  # deployment, architecture, security, cost
    title: str
    description: str
    requester: str
    created_at: datetime
    priority: str = "medium"  # low, medium, high, critical
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ApprovalDecision:
    """Approval decision record"""

    request_id: str
    approver: str
    status: ApprovalStatus
    decision_time: datetime
    reason: str = ""
    additional_data: Dict = None

    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}


@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""

    workflow_id: str
    request_id: str
    steps: List[WorkflowStep]
    current_step: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    step_durations: Dict[str, float] = None

    def __post_init__(self):
        if self.step_durations is None:
            self.step_durations = {}


class EnhancedHITLWorkflowEngine:
    """Enhanced Human-in-the-Loop workflow engine with optimization"""

    def __init__(
        self,
        dora_engine: DORAMetricsEngine,
        artifacts_dir: str = "./artifacts/hitl",
        cross_validation_tolerance: float = 15.0,
    ):
        """
        Initialize Enhanced HITL Workflow Engine

        Args:
            dora_engine: DORA metrics engine for performance tracking
            artifacts_dir: Directory for HITL artifacts
            cross_validation_tolerance: Cross-validation tolerance percentage
        """
        self.dora_engine = dora_engine
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.tolerance = cross_validation_tolerance

        # Workflow data
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.approval_decisions: Dict[str, List[ApprovalDecision]] = {}
        self.workflow_executions: Dict[str, WorkflowExecution] = {}

        # Approval matrix from CLAUDE.md
        self.approval_matrix = {
            "production_changes": {
                "required": True,
                "approvers": ["management"],
                "timeout_minutes": 30,
                "escalation": "slack",
            },
            "cost_impact_high": {  # >$1000
                "required": True,
                "approvers": ["management", "finops"],
                "timeout_minutes": 45,
                "analysis_required": True,
            },
            "security_changes": {
                "required": True,
                "compliance": ["SOC2", "PCI-DSS", "HIPAA"],
                "approvers": ["management", "security"],
                "evidence_required": True,
                "timeout_minutes": 60,
            },
            "architecture_changes": {
                "required": True,
                "scope": ["multi-account", "cross-region"],
                "approvers": ["management", "architect"],
                "documentation_required": True,
                "timeout_minutes": 45,
            },
        }

        # Performance optimization settings
        self.optimization_config = {
            "parallel_approvals": True,
            "auto_escalation": True,
            "smart_routing": True,
            "cross_validation": True,
            "bottleneck_detection": True,
        }

        # Workflow templates
        self.workflow_templates = {
            "deployment_approval": [
                WorkflowStep.VALIDATION,
                WorkflowStep.ARCHITECTURE_REVIEW,
                WorkflowStep.SECURITY_REVIEW,
                WorkflowStep.COST_ANALYSIS,
                WorkflowStep.MANAGER_APPROVAL,
                WorkflowStep.DEPLOYMENT,
            ],
            "architecture_review": [
                WorkflowStep.VALIDATION,
                WorkflowStep.ARCHITECTURE_REVIEW,
                WorkflowStep.SECURITY_REVIEW,
                WorkflowStep.MANAGER_APPROVAL,
            ],
            "cost_optimization": [WorkflowStep.VALIDATION, WorkflowStep.COST_ANALYSIS, WorkflowStep.MANAGER_APPROVAL],
        }

    async def submit_approval_request(
        self,
        request_type: str,
        title: str,
        description: str,
        requester: str,
        priority: str = "medium",
        metadata: Dict = None,
    ) -> str:
        """Submit new approval request"""

        request_id = f"{request_type}_{int(datetime.now().timestamp())}"

        request = ApprovalRequest(
            request_id=request_id,
            request_type=request_type,
            title=title,
            description=description,
            requester=requester,
            created_at=datetime.now(timezone.utc),
            priority=priority,
            metadata=metadata or {},
        )

        self.approval_requests[request_id] = request

        # Start workflow execution
        await self._start_workflow(request)

        logger.info(f"📝 Approval request submitted: {request_id} - {title}")

        return request_id

    async def _start_workflow(self, request: ApprovalRequest):
        """Start workflow execution for approval request"""

        # Determine workflow template
        if request.request_type in self.workflow_templates:
            steps = self.workflow_templates[request.request_type]
        else:
            steps = self.workflow_templates["deployment_approval"]  # Default

        workflow_id = f"wf_{request.request_id}"

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            request_id=request.request_id,
            steps=steps,
            current_step=0,
            status="running",
            start_time=datetime.now(timezone.utc),
        )

        self.workflow_executions[workflow_id] = execution

        # Start first step
        await self._execute_workflow_step(execution)

    async def _execute_workflow_step(self, execution: WorkflowExecution):
        """Execute current workflow step"""

        if execution.current_step >= len(execution.steps):
            # Workflow completed
            execution.status = "completed"
            execution.end_time = datetime.now(timezone.utc)

            # Record workflow completion time
            total_duration = (execution.end_time - execution.start_time).total_seconds() / 60  # minutes
            self.dora_engine.record_approval_time(total_duration, "complete_workflow")

            logger.info(f"✅ Workflow completed: {execution.workflow_id}")
            return

        current_step = execution.steps[execution.current_step]
        step_start = datetime.now(timezone.utc)

        logger.info(f"🔄 Executing step: {current_step.value} for {execution.workflow_id}")

        # Execute step based on type
        step_result = await self._execute_step_logic(current_step, execution)

        step_duration = (datetime.now(timezone.utc) - step_start).total_seconds() / 60  # minutes
        execution.step_durations[current_step.value] = step_duration

        # Record step timing
        self.dora_engine.record_approval_time(step_duration, current_step.value)

        if step_result["success"]:
            # Move to next step
            execution.current_step += 1
            await self._execute_workflow_step(execution)
        else:
            # Handle step failure
            execution.status = "failed"
            execution.end_time = datetime.now(timezone.utc)
            logger.error(f"❌ Workflow step failed: {current_step.value} - {step_result.get('error', 'Unknown error')}")

    async def _execute_step_logic(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict:
        """Execute specific step logic"""

        request = self.approval_requests[execution.request_id]

        if step == WorkflowStep.VALIDATION:
            return await self._validate_request(request)
        elif step == WorkflowStep.ARCHITECTURE_REVIEW:
            return await self._architecture_review(request)
        elif step == WorkflowStep.SECURITY_REVIEW:
            return await self._security_review(request)
        elif step == WorkflowStep.COST_ANALYSIS:
            return await self._cost_analysis(request)
        elif step == WorkflowStep.MANAGER_APPROVAL:
            return await self._manager_approval(request)
        elif step == WorkflowStep.DEPLOYMENT:
            return await self._execute_deployment(request)
        else:
            return {"success": False, "error": f"Unknown step: {step}"}

    async def _validate_request(self, request: ApprovalRequest) -> Dict:
        """Validate approval request"""

        # Basic validation
        if not request.title or not request.description:
            return {"success": False, "error": "Missing required fields"}

        # Cross-validation if enabled
        if self.optimization_config["cross_validation"]:
            validation_result = await self._cross_validate_request(request)
            if not validation_result["valid"]:
                return {"success": False, "error": f"Cross-validation failed: {validation_result['error']}"}

        logger.info(f"✅ Request validated: {request.request_id}")
        return {"success": True, "validation_result": "passed"}

    async def _cross_validate_request(self, request: ApprovalRequest) -> Dict:
        """Cross-validate request with ±15% tolerance"""

        # Simulate cross-validation logic
        # In real implementation, this would validate against external systems

        if request.request_type == "cost_optimization":
            expected_savings = request.metadata.get("expected_savings", 0)
            actual_estimate = request.metadata.get("actual_estimate", 0)

            if expected_savings > 0:
                variance = abs(expected_savings - actual_estimate) / expected_savings * 100
                if variance <= self.tolerance:
                    return {"valid": True, "variance": variance}
                else:
                    return {
                        "valid": False,
                        "error": f"Cost variance {variance:.1f}% exceeds tolerance {self.tolerance}%",
                        "variance": variance,
                    }

        return {"valid": True, "variance": 0}

    async def _architecture_review(self, request: ApprovalRequest) -> Dict:
        """Execute architecture review step"""

        # Check if architecture review is required
        if request.request_type in ["deployment_approval", "architecture_review"]:
            # Simulate architecture review (would integrate with actual review process)
            review_score = 95  # From CLAUDE.md - "Architecture approved (95/100)"

            if review_score >= 90:
                logger.info(f"✅ Architecture review passed: {request.request_id} - Score: {review_score}/100")
                return {"success": True, "review_score": review_score}
            else:
                return {"success": False, "error": f"Architecture review failed - Score: {review_score}/100"}

        # Skip if not required
        return {"success": True, "skipped": "not_required"}

    async def _security_review(self, request: ApprovalRequest) -> Dict:
        """Execute security review step"""

        # Check security requirements
        if request.request_type in ["deployment_approval", "security_changes"]:
            # Simulate security compliance check
            compliance_frameworks = ["SOC2", "PCI-DSS", "AWS Well-Architected"]
            compliance_scores = {fw: 98 for fw in compliance_frameworks}  # High compliance scores

            all_passed = all(score >= 95 for score in compliance_scores.values())

            if all_passed:
                logger.info(f"✅ Security review passed: {request.request_id}")
                return {"success": True, "compliance_scores": compliance_scores}
            else:
                failing_frameworks = [fw for fw, score in compliance_scores.items() if score < 95]
                return {"success": False, "error": f"Security compliance failed: {failing_frameworks}"}

        return {"success": True, "skipped": "not_required"}

    async def _cost_analysis(self, request: ApprovalRequest) -> Dict:
        """Execute cost analysis step"""

        # Check if cost analysis is required
        cost_impact = request.metadata.get("cost_impact", 0)

        if cost_impact > 1000:  # >$1000 threshold from CLAUDE.md
            # Simulate cost analysis
            analysis_result = {
                "cost_impact": cost_impact,
                "monthly_increase": cost_impact,
                "annual_impact": cost_impact * 12,
                "optimization_potential": cost_impact * 0.25,  # 25% savings target
                "recommendation": "approved_with_monitoring",
            }

            logger.info(f"✅ Cost analysis completed: {request.request_id} - Impact: ${cost_impact}")
            return {"success": True, "analysis_result": analysis_result}

        return {"success": True, "skipped": "low_cost_impact"}

    async def _manager_approval(self, request: ApprovalRequest) -> Dict:
        """Execute manager approval step"""

        # Check if manual approval is pending
        request_decisions = self.approval_decisions.get(request.request_id, [])
        manager_decisions = [d for d in request_decisions if "manager" in d.approver.lower()]

        if manager_decisions:
            latest_decision = max(manager_decisions, key=lambda d: d.decision_time)

            if latest_decision.status == ApprovalStatus.APPROVED:
                logger.info(f"✅ Manager approval granted: {request.request_id}")
                return {"success": True, "approver": latest_decision.approver}
            else:
                return {"success": False, "error": f"Manager approval {latest_decision.status.value}"}

        # Wait for manual approval (in real implementation, would trigger notification)
        logger.info(f"⏳ Waiting for manager approval: {request.request_id}")

        # For simulation, auto-approve after short delay
        await asyncio.sleep(1)

        # Simulate manager approval
        auto_decision = ApprovalDecision(
            request_id=request.request_id,
            approver="management_auto",
            status=ApprovalStatus.APPROVED,
            decision_time=datetime.now(timezone.utc),
            reason="Auto-approved for simulation",
        )

        if request.request_id not in self.approval_decisions:
            self.approval_decisions[request.request_id] = []
        self.approval_decisions[request.request_id].append(auto_decision)

        return {"success": True, "approver": "management_auto"}

    async def _execute_deployment(self, request: ApprovalRequest) -> Dict:
        """Execute deployment step"""

        if request.request_type == "deployment_approval":
            # Create deployment record in DORA metrics
            deployment_id = f"deploy_{request.request_id}"

            deployment = self.dora_engine.record_deployment(
                deployment_id=deployment_id,
                environment=request.metadata.get("environment", "production"),
                service_name=request.metadata.get("service_name", "unknown"),
                version=request.metadata.get("version", "unknown"),
                commit_sha=request.metadata.get("commit_sha", ""),
                approver=request.metadata.get("approver", request.requester),
            )

            # Simulate deployment (would trigger actual deployment)
            await asyncio.sleep(2)  # Simulate deployment time

            # Mark deployment as successful (90% success rate from CLAUDE.md targets)
            success_rate = 0.95
            deployment_success = hash(deployment_id) % 100 < (success_rate * 100)

            status = "success" if deployment_success else "failed"
            self.dora_engine.complete_deployment(deployment_id, status)

            if deployment_success:
                logger.info(f"✅ Deployment successful: {deployment_id}")
                return {"success": True, "deployment_id": deployment_id}
            else:
                logger.error(f"❌ Deployment failed: {deployment_id}")
                return {"success": False, "error": "Deployment failed", "deployment_id": deployment_id}

        return {"success": True, "skipped": "not_deployment"}

    def record_manual_approval(self, request_id: str, approver: str, status: ApprovalStatus, reason: str = "") -> bool:
        """Record manual approval decision"""

        if request_id not in self.approval_requests:
            logger.warning(f"⚠️ Approval request not found: {request_id}")
            return False

        decision = ApprovalDecision(
            request_id=request_id,
            approver=approver,
            status=status,
            decision_time=datetime.now(timezone.utc),
            reason=reason,
        )

        if request_id not in self.approval_decisions:
            self.approval_decisions[request_id] = []
        self.approval_decisions[request_id].append(decision)

        # Record approval time
        request = self.approval_requests[request_id]
        approval_duration = (decision.decision_time - request.created_at).total_seconds() / 60  # minutes
        self.dora_engine.record_approval_time(approval_duration, "manual_approval")

        logger.info(f"📝 Manual approval recorded: {request_id} - {status.value} by {approver}")

        return True

    def identify_workflow_bottlenecks(self) -> Dict:
        """Identify workflow bottlenecks for optimization"""

        bottlenecks = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "step_performance": {},
            "recommendations": [],
        }

        # Analyze step durations across all workflows
        all_step_durations = {}

        for execution in self.workflow_executions.values():
            for step, duration in execution.step_durations.items():
                if step not in all_step_durations:
                    all_step_durations[step] = []
                all_step_durations[step].append(duration)

        # Calculate average durations and identify bottlenecks
        for step, durations in all_step_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)

                bottlenecks["step_performance"][step] = {
                    "average_duration_minutes": avg_duration,
                    "max_duration_minutes": max_duration,
                    "executions_count": len(durations),
                    "is_bottleneck": avg_duration > 30,  # >30 minutes considered bottleneck
                }

                if avg_duration > 30:
                    bottlenecks["recommendations"].append(
                        f"Optimize '{step}' step - average duration {avg_duration:.1f} minutes exceeds target"
                    )

        # Overall recommendations
        if not bottlenecks["recommendations"]:
            bottlenecks["recommendations"].append("All workflow steps performing within target times")

        logger.info(f"🔍 Workflow bottlenecks analysis completed")

        return bottlenecks

    def generate_hitl_optimization_report(self) -> Dict:
        """Generate comprehensive HITL optimization report"""

        logger.info("📊 Generating HITL optimization report")

        # Get DORA metrics
        dora_report = self.dora_engine.generate_comprehensive_report()

        # Analyze bottlenecks
        bottlenecks = self.identify_workflow_bottlenecks()

        # Calculate workflow statistics
        completed_workflows = [w for w in self.workflow_executions.values() if w.status == "completed"]
        failed_workflows = [w for w in self.workflow_executions.values() if w.status == "failed"]

        workflow_stats = {
            "total_workflows": len(self.workflow_executions),
            "completed_workflows": len(completed_workflows),
            "failed_workflows": len(failed_workflows),
            "success_rate": len(completed_workflows) / len(self.workflow_executions) if self.workflow_executions else 0,
        }

        # Calculate average workflow duration
        if completed_workflows:
            workflow_durations = []
            for workflow in completed_workflows:
                if workflow.end_time:
                    duration = (workflow.end_time - workflow.start_time).total_seconds() / 60  # minutes
                    workflow_durations.append(duration)

            avg_workflow_duration = sum(workflow_durations) / len(workflow_durations) if workflow_durations else 0
        else:
            avg_workflow_duration = 0

        # Cross-validation accuracy
        cross_validation_stats = {
            "tolerance_percentage": self.tolerance,
            "validation_enabled": self.optimization_config["cross_validation"],
        }

        report = {
            "report_type": "hitl_optimization",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_statistics": workflow_stats,
            "average_workflow_duration_minutes": avg_workflow_duration,
            "cross_validation": cross_validation_stats,
            "bottleneck_analysis": bottlenecks,
            "dora_metrics_integration": {
                "lead_time_hours": dora_report["dora_metrics"]["lead_time"]["value"],
                "approval_time_minutes": dora_report["hitl_metrics"].get("approval_time", {}).get("value", 0),
            },
            "optimization_recommendations": self._generate_optimization_recommendations(workflow_stats, bottlenecks),
            "performance_grade": dora_report["performance_analysis"]["performance_grade"],
        }

        # Save report
        report_file = self.artifacts_dir / f"hitl_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✅ HITL optimization report saved to: {report_file}")

        return report

    def _generate_optimization_recommendations(self, workflow_stats: Dict, bottlenecks: Dict) -> List[str]:
        """Generate optimization recommendations"""

        recommendations = []

        # Success rate recommendations
        success_rate = workflow_stats["success_rate"]
        if success_rate < 0.95:  # <95% target from CLAUDE.md
            recommendations.append(f"📈 Improve workflow success rate: Currently {success_rate:.1%}, target >95%")

        # Bottleneck recommendations
        for step, perf in bottlenecks["step_performance"].items():
            if perf["is_bottleneck"]:
                recommendations.append(
                    f"⚡ Optimize '{step}' step: Average {perf['average_duration_minutes']:.1f} minutes exceeds 30-minute target"
                )

        # Cross-validation recommendations
        if self.tolerance > 10:
            recommendations.append(
                f"🎯 Tighten cross-validation tolerance: Current {self.tolerance}% could be reduced for better accuracy"
            )

        # General optimizations
        if not recommendations:
            recommendations.extend(
                [
                    "✅ All HITL metrics within target ranges",
                    "🔍 Consider implementing advanced workflow optimizations:",
                    "  - Parallel approval processing",
                    "  - AI-assisted pre-validation",
                    "  - Predictive bottleneck detection",
                ]
            )

        return recommendations


# Async integration functions
async def simulate_hitl_workflow_optimization(duration_minutes: int = 10) -> Dict:
    """Simulate HITL workflow optimization for demonstration"""

    from ..metrics.dora_metrics_engine import DORAMetricsEngine

    dora_engine = DORAMetricsEngine()
    hitl_engine = EnhancedHITLWorkflowEngine(dora_engine)

    logger.info(f"🧪 Starting {duration_minutes}-minute HITL optimization simulation")

    # Simulate various approval requests
    requests = [
        (
            "deployment_approval",
            "Deploy VPC Wrapper v1.2.0",
            "Deploy enhanced VPC wrapper with Rich integration",
            "developer",
            "high",
            {"environment": "production", "service_name": "vpc-wrapper", "version": "v1.2.0", "cost_impact": 500},
        ),
        (
            "architecture_review",
            "Multi-Account Organizations API",
            "Review Organizations API integration architecture",
            "architect",
            "medium",
            {"scope": "multi-account", "compliance_required": True},
        ),
        (
            "cost_optimization",
            "FinOps Dashboard Enhancement",
            "Cost optimization for FinOps dashboard",
            "finops",
            "medium",
            {"expected_savings": 2500, "actual_estimate": 2400, "cost_impact": 1200},
        ),
    ]

    # Submit approval requests
    for req_type, title, desc, requester, priority, metadata in requests:
        request_id = await hitl_engine.submit_approval_request(req_type, title, desc, requester, priority, metadata)

        # Simulate manual approval for some requests
        if "deployment" in req_type:
            hitl_engine.record_manual_approval(
                request_id, "management", ApprovalStatus.APPROVED, "Approved for production deployment"
            )

    # Allow workflows to complete
    await asyncio.sleep(3)

    # Generate optimization report
    optimization_report = hitl_engine.generate_hitl_optimization_report()

    return optimization_report


if __name__ == "__main__":
    # CLI execution
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced HITL Workflow Engine")
    parser.add_argument("--simulate", action="store_true", help="Run optimization simulation")
    parser.add_argument("--duration", type=int, default=10, help="Simulation duration in minutes")
    parser.add_argument("--output", "-o", default="./artifacts/hitl", help="Output directory")

    args = parser.parse_args()

    async def main():
        if args.simulate:
            report = await simulate_hitl_workflow_optimization(args.duration)
            print("✅ HITL optimization simulation completed")
            print(f"📊 Performance grade: {report['performance_grade']}")
            print(f"⚡ Average workflow duration: {report['average_workflow_duration_minutes']:.1f} minutes")
            print(f"🎯 Success rate: {report['workflow_statistics']['success_rate']:.1%}")
        else:
            from ..metrics.dora_metrics_engine import DORAMetricsEngine

            dora_engine = DORAMetricsEngine(args.output)
            hitl_engine = EnhancedHITLWorkflowEngine(dora_engine, args.output)
            report = hitl_engine.generate_hitl_optimization_report()
            print("✅ HITL optimization report generated")
            print(f"📊 Report saved to: {hitl_engine.artifacts_dir}")

    asyncio.run(main())
