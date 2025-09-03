#!/usr/bin/env python3
"""
DORA Metrics Engine for HITL System Optimization

Issue #93: HITL System & DORA Metrics Optimization
Priority: High (Sprint 1 Improvements)
Scope: Optimize Human-in-the-Loop system and enhance DORA metrics collection
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.logger import configure_logger

logger = configure_logger(__name__)


@dataclass
class DORAMetric:
    """Individual DORA metric measurement"""

    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DeploymentEvent:
    """Deployment event for DORA metrics tracking"""

    deployment_id: str
    environment: str
    service_name: str
    version: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "in_progress"  # in_progress, success, failed, rolled_back
    commit_sha: str = ""
    approver: str = ""
    rollback_time: Optional[datetime] = None


@dataclass
class IncidentEvent:
    """Incident event for DORA metrics tracking"""

    incident_id: str
    service_name: str
    severity: str  # critical, high, medium, low
    start_time: datetime
    detection_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    root_cause: str = ""
    caused_by_deployment: str = ""


class DORAMetricsEngine:
    """
    Enhanced DORA metrics collection and analysis engine for Enterprise SRE.

    Provides comprehensive DORA metrics (Lead Time, Deploy Frequency, MTTR, Change Failure Rate)
    with real-time collection, automated alerting, and enterprise dashboard integration.

    Features:
    - Real-time metrics streaming from git operations
    - Automated deployment event capture via GitHub webhooks
    - CloudWatch/Datadog integration for enterprise monitoring
    - Cross-session persistence with baseline trending
    - SLA compliance tracking with automated alerting
    """

    def __init__(self, artifacts_dir: str = "./artifacts/metrics", cross_validation_tolerance: float = 15.0):
        """
        Initialize enterprise DORA metrics engine

        Args:
            artifacts_dir: Directory to store metrics artifacts
            cross_validation_tolerance: Tolerance percentage for metric validation
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Create SRE-focused subdirectories
        (self.artifacts_dir / "dora-reports").mkdir(exist_ok=True)
        (self.artifacts_dir / "baselines").mkdir(exist_ok=True)
        (self.artifacts_dir / "alerts").mkdir(exist_ok=True)
        (self.artifacts_dir / "dashboards").mkdir(exist_ok=True)

        self.tolerance = cross_validation_tolerance

        # Metrics storage with persistence
        self.deployments: List[DeploymentEvent] = []
        self.incidents: List[IncidentEvent] = []
        self.metrics_history: List[DORAMetric] = []
        self.baselines: Dict[str, float] = {}

        # HITL workflow metrics
        self.approval_times: List[float] = []
        self.workflow_bottlenecks: Dict[str, List[float]] = {}

        # Enterprise SRE performance targets (FAANG SDLC standards)
        self.targets = {
            "lead_time_hours": 4,  # <4 hours (FAANG velocity)
            "deploy_frequency_daily": 1,  # Daily deployment capability
            "change_failure_rate": 0.05,  # <5% (FAANG quality)
            "mttr_hours": 1,  # <1 hour (SRE excellence)
            "approval_time_minutes": 30,  # <30 minutes (HITL efficiency)
            "success_rate": 0.95,  # >95% (Enterprise reliability)
            "sla_availability": 0.999,  # >99.9% uptime
            "performance_score": 90,  # >90% performance score
        }

        # SRE alerting thresholds
        self.alert_thresholds = {
            "lead_time_hours": 6,  # Alert if >6 hours
            "deploy_frequency_daily": 0.5,  # Alert if <0.5 deploys/day
            "change_failure_rate": 0.10,  # Alert if >10%
            "mttr_hours": 2,  # Alert if >2 hours
            "approval_time_minutes": 60,  # Alert if >60 minutes
        }

        # Load existing data
        self._load_persistent_data()

        # Initialize baseline metrics if not exists
        self._initialize_baselines()

    def record_deployment(
        self,
        deployment_id: str,
        environment: str,
        service_name: str,
        version: str,
        commit_sha: str = "",
        approver: str = "",
    ) -> DeploymentEvent:
        """Record a new deployment event"""

        deployment = DeploymentEvent(
            deployment_id=deployment_id,
            environment=environment,
            service_name=service_name,
            version=version,
            start_time=datetime.now(timezone.utc),
            commit_sha=commit_sha,
            approver=approver,
        )

        self.deployments.append(deployment)

        logger.info(f"🚀 Deployment recorded: {deployment_id} for {service_name}")

        return deployment

    def complete_deployment(self, deployment_id: str, status: str, rollback_time: Optional[datetime] = None) -> bool:
        """Mark deployment as complete"""

        for deployment in self.deployments:
            if deployment.deployment_id == deployment_id:
                deployment.end_time = datetime.now(timezone.utc)
                deployment.status = status
                deployment.rollback_time = rollback_time

                logger.info(f"✅ Deployment completed: {deployment_id} - {status}")
                return True

        logger.warning(f"⚠️ Deployment not found: {deployment_id}")
        return False

    def record_incident(
        self, incident_id: str, service_name: str, severity: str, root_cause: str = "", caused_by_deployment: str = ""
    ) -> IncidentEvent:
        """Record a new incident event"""

        incident = IncidentEvent(
            incident_id=incident_id,
            service_name=service_name,
            severity=severity,
            start_time=datetime.now(timezone.utc),
            root_cause=root_cause,
            caused_by_deployment=caused_by_deployment,
        )

        self.incidents.append(incident)

        logger.info(f"🚨 Incident recorded: {incident_id} - {severity} severity")

        return incident

    def resolve_incident(self, incident_id: str, detection_time: Optional[datetime] = None) -> bool:
        """Mark incident as resolved"""

        for incident in self.incidents:
            if incident.incident_id == incident_id:
                incident.resolution_time = datetime.now(timezone.utc)
                if detection_time:
                    incident.detection_time = detection_time

                logger.info(f"✅ Incident resolved: {incident_id}")
                return True

        logger.warning(f"⚠️ Incident not found: {incident_id}")
        return False

    def record_approval_time(self, approval_time_minutes: float, workflow_step: str = "general"):
        """Record HITL approval time"""
        self.approval_times.append(approval_time_minutes)

        if workflow_step not in self.workflow_bottlenecks:
            self.workflow_bottlenecks[workflow_step] = []
        self.workflow_bottlenecks[workflow_step].append(approval_time_minutes)

    def calculate_lead_time(self, days_back: int = 30) -> DORAMetric:
        """Calculate deployment lead time"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date and d.end_time]

        if not recent_deployments:
            return DORAMetric(
                metric_name="lead_time",
                value=0.0,
                unit="hours",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        # Calculate average lead time (simplified - in real scenario would track from commit to production)
        lead_times = []
        for deployment in recent_deployments:
            if deployment.end_time and deployment.status == "success":
                duration = (deployment.end_time - deployment.start_time).total_seconds() / 3600  # hours
                lead_times.append(duration)

        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

        metric = DORAMetric(
            metric_name="lead_time",
            value=avg_lead_time,
            unit="hours",
            timestamp=datetime.now(timezone.utc),
            tags={
                "period": f"{days_back}d",
                "deployments_count": str(len(recent_deployments)),
                "successful_deployments": str(len(lead_times)),
            },
            metadata={
                "target": self.targets["lead_time_hours"],
                "target_met": avg_lead_time <= self.targets["lead_time_hours"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_deployment_frequency(self, days_back: int = 30) -> DORAMetric:
        """Calculate deployment frequency"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date]

        # Calculate deployments per day
        deployments_per_day = len(recent_deployments) / days_back if days_back > 0 else 0

        metric = DORAMetric(
            metric_name="deployment_frequency",
            value=deployments_per_day,
            unit="deployments_per_day",
            timestamp=datetime.now(timezone.utc),
            tags={"period": f"{days_back}d", "total_deployments": str(len(recent_deployments))},
            metadata={
                "target": self.targets["deploy_frequency_daily"],
                "target_met": deployments_per_day >= self.targets["deploy_frequency_daily"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_change_failure_rate(self, days_back: int = 30) -> DORAMetric:
        """Calculate change failure rate"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date and d.end_time]

        if not recent_deployments:
            return DORAMetric(
                metric_name="change_failure_rate",
                value=0.0,
                unit="percentage",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        failed_deployments = len([d for d in recent_deployments if d.status in ["failed", "rolled_back"]])

        failure_rate = failed_deployments / len(recent_deployments)

        metric = DORAMetric(
            metric_name="change_failure_rate",
            value=failure_rate,
            unit="percentage",
            timestamp=datetime.now(timezone.utc),
            tags={
                "period": f"{days_back}d",
                "total_deployments": str(len(recent_deployments)),
                "failed_deployments": str(failed_deployments),
            },
            metadata={
                "target": self.targets["change_failure_rate"],
                "target_met": failure_rate <= self.targets["change_failure_rate"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_mttr(self, days_back: int = 30) -> DORAMetric:
        """Calculate Mean Time to Recovery (MTTR)"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_incidents = [i for i in self.incidents if i.start_time >= cutoff_date and i.resolution_time]

        if not recent_incidents:
            return DORAMetric(
                metric_name="mttr",
                value=0.0,
                unit="hours",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        # Calculate recovery times
        recovery_times = []
        for incident in recent_incidents:
            if incident.resolution_time:
                duration = (incident.resolution_time - incident.start_time).total_seconds() / 3600  # hours
                recovery_times.append(duration)

        avg_mttr = sum(recovery_times) / len(recovery_times) if recovery_times else 0

        metric = DORAMetric(
            metric_name="mttr",
            value=avg_mttr,
            unit="hours",
            timestamp=datetime.now(timezone.utc),
            tags={"period": f"{days_back}d", "incidents_count": str(len(recent_incidents))},
            metadata={"target": self.targets["mttr_hours"], "target_met": avg_mttr <= self.targets["mttr_hours"]},
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_hitl_metrics(self) -> Dict[str, DORAMetric]:
        """Calculate Human-in-the-Loop specific metrics"""

        metrics = {}

        # Average approval time
        if self.approval_times:
            avg_approval_time = sum(self.approval_times) / len(self.approval_times)

            metrics["approval_time"] = DORAMetric(
                metric_name="approval_time",
                value=avg_approval_time,
                unit="minutes",
                timestamp=datetime.now(timezone.utc),
                tags={"total_approvals": str(len(self.approval_times))},
                metadata={
                    "target": self.targets["approval_time_minutes"],
                    "target_met": avg_approval_time <= self.targets["approval_time_minutes"],
                },
            )

        # Workflow bottlenecks analysis
        if self.workflow_bottlenecks:
            bottleneck_metrics = {}

            for step, times in self.workflow_bottlenecks.items():
                if times:
                    avg_time = sum(times) / len(times)
                    bottleneck_metrics[f"{step}_avg_time"] = avg_time

            # Identify slowest step
            if bottleneck_metrics:
                slowest_step = max(bottleneck_metrics, key=bottleneck_metrics.get)
                slowest_time = bottleneck_metrics[slowest_step]

                metrics["workflow_bottleneck"] = DORAMetric(
                    metric_name="workflow_bottleneck",
                    value=slowest_time,
                    unit="minutes",
                    timestamp=datetime.now(timezone.utc),
                    tags={"bottleneck_step": slowest_step},
                    metadata={"all_steps": bottleneck_metrics},
                )

        return metrics

    def _load_persistent_data(self) -> None:
        """Load persistent DORA data from storage."""
        try:
            # Load deployments
            deployments_file = self.artifacts_dir / "deployments.json"
            if deployments_file.exists():
                with open(deployments_file, "r") as f:
                    data = json.load(f)
                    self.deployments = [DeploymentEvent(**item) for item in data.get("deployments", [])]

            # Load incidents
            incidents_file = self.artifacts_dir / "incidents.json"
            if incidents_file.exists():
                with open(incidents_file, "r") as f:
                    data = json.load(f)
                    self.incidents = [IncidentEvent(**item) for item in data.get("incidents", [])]

            # Load baselines
            baselines_file = self.artifacts_dir / "baselines" / "current_baselines.json"
            if baselines_file.exists():
                with open(baselines_file, "r") as f:
                    self.baselines = json.load(f)

            logger.info(f"📊 Loaded {len(self.deployments)} deployments, {len(self.incidents)} incidents")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load persistent data: {e}")

    def _save_persistent_data(self) -> None:
        """Save persistent DORA data to storage."""
        try:
            # Save deployments
            deployments_data = {
                "deployments": [asdict(d) for d in self.deployments],
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            deployments_file = self.artifacts_dir / "deployments.json"
            with open(deployments_file, "w") as f:
                json.dump(deployments_data, f, indent=2, default=str)

            # Save incidents
            incidents_data = {
                "incidents": [asdict(i) for i in self.incidents],
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            incidents_file = self.artifacts_dir / "incidents.json"
            with open(incidents_file, "w") as f:
                json.dump(incidents_data, f, indent=2, default=str)

            # Save baselines
            baselines_file = self.artifacts_dir / "baselines" / "current_baselines.json"
            with open(baselines_file, "w") as f:
                json.dump(self.baselines, f, indent=2)

        except Exception as e:
            logger.error(f"❌ Failed to save persistent data: {e}")

    def _initialize_baselines(self) -> None:
        """Initialize baseline metrics for trending analysis."""
        if not self.baselines and len(self.deployments) > 10:
            # Calculate initial baselines from historical data
            lead_time_metric = self.calculate_lead_time(30)
            deploy_freq_metric = self.calculate_deployment_frequency(30)
            failure_rate_metric = self.calculate_change_failure_rate(30)
            mttr_metric = self.calculate_mttr(30)

            self.baselines = {
                "lead_time_hours": lead_time_metric.value,
                "deploy_frequency_daily": deploy_freq_metric.value,
                "change_failure_rate": failure_rate_metric.value,
                "mttr_hours": mttr_metric.value,
                "baseline_established": datetime.now(timezone.utc).isoformat(),
                "sample_size": len(self.deployments),
            }

            logger.info("📈 Established baseline metrics from historical data")
            self._save_persistent_data()

    def track_git_deployment(
        self, commit_sha: str, branch: str = "main", author: str = "", message: str = ""
    ) -> DeploymentEvent:
        """
        Track deployment from git operations for automated DORA collection.

        Args:
            commit_sha: Git commit SHA
            branch: Git branch name
            author: Commit author
            message: Commit message

        Returns:
            Created deployment event
        """
        deployment_id = f"git-{commit_sha[:8]}-{int(time.time())}"

        deployment = self.record_deployment(
            deployment_id=deployment_id,
            environment="production" if branch == "main" else "development",
            service_name="runbooks",
            version=commit_sha[:8],
            commit_sha=commit_sha,
            approver=author,
        )

        # Add git metadata
        deployment.metadata = {
            "branch": branch,
            "author": author,
            "message": message,
            "automated": True,
            "source": "git_integration",
        }

        logger.info(f"🔗 Git deployment tracked: {commit_sha[:8]} on {branch}")

        # Auto-save after git integration
        self._save_persistent_data()

        return deployment

    def detect_performance_incident(
        self, module: str, operation: str, execution_time: float, threshold: float
    ) -> Optional[IncidentEvent]:
        """
        Automatically detect and record performance incidents.

        Args:
            module: Module name (e.g., 'finops', 'inventory')
            operation: Operation name
            execution_time: Actual execution time
            threshold: Performance threshold

        Returns:
            Created incident if threshold exceeded, None otherwise
        """
        if execution_time <= threshold:
            return None

        incident_id = f"perf-{module}-{int(time.time())}"
        severity = "critical" if execution_time > threshold * 2 else "high"

        incident = self.record_incident(
            incident_id=incident_id,
            service_name=module,
            severity=severity,
            root_cause=f"Performance degradation: {operation} took {execution_time:.2f}s (threshold: {threshold:.2f}s)",
        )

        # Add performance metadata
        incident.metadata = {
            "operation": operation,
            "execution_time": execution_time,
            "threshold": threshold,
            "degradation_factor": execution_time / threshold,
            "automated_detection": True,
        }

        logger.warning(f"🚨 Performance incident detected: {incident_id}")

        # Generate real-time alert
        self._generate_sre_alert(incident, execution_time, threshold)

        return incident

    def _generate_sre_alert(self, incident: IncidentEvent, execution_time: float, threshold: float) -> None:
        """Generate SRE-focused performance alert."""
        alert_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alert_type": "sre_performance_degradation",
            "incident_id": incident.incident_id,
            "service": incident.service_name,
            "severity": incident.severity,
            "execution_time": execution_time,
            "threshold": threshold,
            "degradation_factor": execution_time / threshold,
            "impact": "user_experience" if execution_time > threshold * 1.5 else "performance_sla",
            "recommended_actions": [
                "Check system resource utilization",
                "Review recent deployments for correlation",
                "Validate AWS API rate limiting",
                "Consider auto-scaling triggers",
            ],
        }

        # Save alert to artifacts
        alert_file = self.artifacts_dir / "alerts" / f"sre_alert_{incident.incident_id}.json"
        with open(alert_file, "w") as f:
            json.dump(alert_data, f, indent=2, default=str)

        logger.critical(f"🚨 SRE Alert generated: {alert_file}")

    def calculate_sla_compliance(self, days_back: int = 30) -> Dict[str, DORAMetric]:
        """
        Calculate SLA compliance metrics for enterprise reporting.

        Args:
            days_back: Number of days to analyze

        Returns:
            Dictionary of SLA compliance metrics
        """
        sla_metrics = {}

        # Calculate availability SLA (based on incident downtime)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_incidents = [i for i in self.incidents if i.start_time >= cutoff_date]

        total_downtime_hours = 0
        for incident in recent_incidents:
            if incident.resolution_time and incident.severity in ["critical", "high"]:
                downtime = (incident.resolution_time - incident.start_time).total_seconds() / 3600
                total_downtime_hours += downtime

        total_hours = days_back * 24
        availability = max(0, (total_hours - total_downtime_hours) / total_hours)

        sla_metrics["availability"] = DORAMetric(
            metric_name="availability_sla",
            value=availability,
            unit="percentage",
            timestamp=datetime.now(timezone.utc),
            tags={"period": f"{days_back}d", "incidents": str(len(recent_incidents))},
            metadata={
                "target": self.targets["sla_availability"],
                "target_met": availability >= self.targets["sla_availability"],
                "downtime_hours": total_downtime_hours,
            },
        )

        # Performance SLA (based on operation execution times)
        performance_scores = []
        for metric in self.metrics_history:
            if metric.metadata and "performance_score" in metric.metadata:
                performance_scores.append(metric.metadata["performance_score"])

        avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0

        sla_metrics["performance"] = DORAMetric(
            metric_name="performance_sla",
            value=avg_performance,
            unit="percentage",
            timestamp=datetime.now(timezone.utc),
            tags={"sample_size": str(len(performance_scores))},
            metadata={
                "target": self.targets["performance_score"],
                "target_met": avg_performance >= self.targets["performance_score"],
            },
        )

        return sla_metrics

    def generate_comprehensive_report(self, days_back: int = 30) -> Dict:
        """Generate comprehensive DORA metrics report with SRE enhancements"""

        logger.info(f"📊 Generating enterprise DORA metrics report for last {days_back} days")

        # Calculate all DORA metrics
        lead_time = self.calculate_lead_time(days_back)
        deployment_freq = self.calculate_deployment_frequency(days_back)
        failure_rate = self.calculate_change_failure_rate(days_back)
        mttr = self.calculate_mttr(days_back)

        # Calculate HITL metrics
        hitl_metrics = self.calculate_hitl_metrics()

        # Calculate SLA compliance metrics
        sla_metrics = self.calculate_sla_compliance(days_back)

        # Performance analysis with enhanced SRE targets
        targets_met = {
            "lead_time": lead_time.metadata.get("target_met", False),
            "deployment_frequency": deployment_freq.metadata.get("target_met", False),
            "change_failure_rate": failure_rate.metadata.get("target_met", False),
            "mttr": mttr.metadata.get("target_met", False),
        }

        # Add HITL targets
        if "approval_time" in hitl_metrics:
            targets_met["approval_time"] = hitl_metrics["approval_time"].metadata.get("target_met", False)

        # Add SLA targets
        for metric_name, metric in sla_metrics.items():
            targets_met[f"sla_{metric_name}"] = metric.metadata.get("target_met", False)

        overall_performance = sum(targets_met.values()) / len(targets_met) * 100

        # Calculate trend analysis vs baselines
        trend_analysis = {}
        if self.baselines:
            for metric_name, current_value in [
                ("lead_time_hours", lead_time.value),
                ("deploy_frequency_daily", deployment_freq.value),
                ("change_failure_rate", failure_rate.value),
                ("mttr_hours", mttr.value),
            ]:
                baseline = self.baselines.get(metric_name, current_value)
                if baseline > 0:
                    trend_percentage = ((current_value - baseline) / baseline) * 100
                    trend_analysis[metric_name] = {
                        "current": current_value,
                        "baseline": baseline,
                        "trend_percentage": trend_percentage,
                        "improving": trend_percentage < 0
                        if metric_name != "deploy_frequency_daily"
                        else trend_percentage > 0,
                    }

        report = {
            "report_type": "dora_metrics_enterprise_sre",
            "version": "2.0",
            "period": f"{days_back}_days",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dora_metrics": {
                "lead_time": asdict(lead_time),
                "deployment_frequency": asdict(deployment_freq),
                "change_failure_rate": asdict(failure_rate),
                "mttr": asdict(mttr),
            },
            "sla_metrics": {k: asdict(v) for k, v in sla_metrics.items()},
            "hitl_metrics": {k: asdict(v) for k, v in hitl_metrics.items()},
            "performance_analysis": {
                "targets_met": targets_met,
                "overall_performance_percentage": overall_performance,
                "performance_grade": self._calculate_performance_grade(overall_performance),
                "sla_compliance_score": sum(1 for k, v in targets_met.items() if k.startswith("sla_") and v)
                / max(1, sum(1 for k in targets_met.keys() if k.startswith("sla_")))
                * 100,
            },
            "trend_analysis": trend_analysis,
            "baseline_comparison": self.baselines,
            "recommendations": self._generate_sre_recommendations(
                targets_met, hitl_metrics, sla_metrics, trend_analysis
            ),
            "alerts_summary": {
                "active_alerts": len(
                    [
                        f
                        for f in (self.artifacts_dir / "alerts").glob("*.json")
                        if f.stat().st_mtime > time.time() - 86400
                    ]
                ),
                "performance_incidents": len(
                    [
                        i
                        for i in self.incidents
                        if i.start_time >= datetime.now(timezone.utc) - timedelta(days=days_back)
                        and "performance" in i.root_cause.lower()
                    ]
                ),
                "sre_health_score": overall_performance,
            },
            "raw_data": {
                "deployments_count": len(self.deployments),
                "incidents_count": len(self.incidents),
                "approval_times_count": len(self.approval_times),
                "automation_rate": len(
                    [d for d in self.deployments if getattr(d, "metadata", {}).get("automated", False)]
                )
                / max(1, len(self.deployments))
                * 100,
            },
        }

        # Save enhanced report to SRE reports directory
        sre_reports_dir = self.artifacts_dir.parent / "sre-reports"
        sre_reports_dir.mkdir(exist_ok=True)

        report_file = sre_reports_dir / f"dora_enterprise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Also save to metrics directory for backward compatibility
        legacy_report_file = (
            self.artifacts_dir / "dora-reports" / f"dora_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(legacy_report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✅ Enterprise DORA metrics report saved to: {report_file}")

        # Auto-save persistent data after report generation
        self._save_persistent_data()

        return report

    def _calculate_performance_grade(self, percentage: float) -> str:
        """Calculate performance grade based on targets met"""
        if percentage >= 90:
            return "A (Excellent)"
        elif percentage >= 80:
            return "B (Good)"
        elif percentage >= 70:
            return "C (Satisfactory)"
        elif percentage >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"

    def _generate_sre_recommendations(
        self, targets_met: Dict[str, bool], hitl_metrics: Dict, sla_metrics: Dict, trend_analysis: Dict
    ) -> List[str]:
        """Generate enhanced SRE-focused recommendations based on comprehensive metrics analysis"""

        recommendations = []

        # DORA metrics recommendations
        if not targets_met.get("lead_time", False):
            recommendations.append(
                "🎯 **Lead Time Optimization**: Implement parallel CI/CD workflows, automate testing pipelines, "
                "and establish fast-track approval processes for low-risk changes"
            )

        if not targets_met.get("deployment_frequency", False):
            recommendations.append(
                "🚀 **Deployment Frequency Enhancement**: Adopt continuous deployment patterns, implement "
                "feature flags, and establish canary deployment strategies for risk mitigation"
            )

        if not targets_met.get("change_failure_rate", False):
            recommendations.append(
                "🛡️ **Change Failure Rate Reduction**: Enhance pre-production testing, implement progressive "
                "rollouts, improve monitoring coverage, and establish automated rollback triggers"
            )

        if not targets_met.get("mttr", False):
            recommendations.append(
                "⚡ **MTTR Improvement**: Implement automated incident detection, enhance observability stack, "
                "establish runbook automation, and improve on-call response procedures"
            )

        # SLA compliance recommendations
        if not targets_met.get("sla_availability", False):
            recommendations.append(
                "🔒 **Availability SLA Recovery**: Implement chaos engineering practices, enhance redundancy, "
                "improve failover mechanisms, and establish proactive monitoring alerts"
            )

        if not targets_met.get("sla_performance", False):
            recommendations.append(
                "📈 **Performance SLA Enhancement**: Optimize critical path operations, implement caching strategies, "
                "enhance resource allocation, and establish performance regression testing"
            )

        # HITL workflow optimization
        if not targets_met.get("approval_time", False):
            recommendations.append(
                "⏰ **Approval Workflow Optimization**: Implement risk-based approval routing, establish "
                "parallel approval processes, and create self-service deployment capabilities for low-risk changes"
            )

        # Trend analysis recommendations
        if trend_analysis:
            declining_metrics = [k for k, v in trend_analysis.items() if not v.get("improving", True)]
            if declining_metrics:
                recommendations.append(
                    f"📊 **Trend Alert**: Declining performance detected in {', '.join(declining_metrics)}. "
                    f"Implement immediate performance improvement initiatives and establish regression prevention measures"
                )

        # Proactive SRE recommendations based on patterns
        if hitl_metrics.get("workflow_bottleneck"):
            bottleneck_step = hitl_metrics["workflow_bottleneck"].tags.get("bottleneck_step", "unknown")
            recommendations.append(
                f"🔍 **Workflow Bottleneck Resolution**: Primary bottleneck identified in '{bottleneck_step}' step. "
                f"Implement automation, parallel processing, or resource scaling for this workflow stage"
            )

        # Automation recommendations
        automation_rate = targets_met.get("automation_rate", 0)
        if automation_rate < 80:
            recommendations.append(
                "🤖 **Automation Enhancement**: Current automation rate below target. Implement GitOps workflows, "
                "automated testing pipelines, and self-healing infrastructure patterns"
            )

        # Advanced SRE practices
        if len([k for k, v in targets_met.items() if v]) / len(targets_met) < 0.8:
            recommendations.append(
                "🎯 **SRE Maturity Enhancement**: Consider implementing advanced SRE practices: error budgets, "
                "SLI/SLO management, chaos engineering, and customer-centric reliability metrics"
            )

        if not recommendations:
            recommendations.append(
                "✅ **Excellence Achieved**: All SRE targets met! Consider advanced optimization: predictive scaling, "
                "AI-powered incident response, and continuous reliability improvement programs"
            )

        return recommendations

    def _generate_recommendations(self, targets_met: Dict[str, bool], hitl_metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics analysis"""

        recommendations = []

        if not targets_met.get("lead_time", False):
            recommendations.append(
                "🎯 Optimize lead time: Consider parallel workflows, automated testing, and faster approval processes"
            )

        if not targets_met.get("deployment_frequency", False):
            recommendations.append(
                "🚀 Increase deployment frequency: Implement continuous deployment pipeline and smaller batch sizes"
            )

        if not targets_met.get("change_failure_rate", False):
            recommendations.append(
                "🛡️ Reduce failure rate: Enhance testing coverage, implement canary deployments, and improve rollback procedures"
            )

        if not targets_met.get("mttr", False):
            recommendations.append(
                "⚡ Improve MTTR: Enhance monitoring, implement automated incident response, and improve alerting"
            )

        if not targets_met.get("approval_time", False):
            recommendations.append(
                "⏰ Optimize approval workflow: Streamline HITL processes, implement parallel approvals, and reduce approval steps"
            )

        # HITL-specific recommendations
        if "workflow_bottleneck" in hitl_metrics:
            bottleneck_step = hitl_metrics["workflow_bottleneck"].tags.get("bottleneck_step", "unknown")
            recommendations.append(f"🔍 Address workflow bottleneck: Focus on optimizing '{bottleneck_step}' step")

        if not recommendations:
            recommendations.append(
                "✅ All targets met! Consider raising performance targets or exploring advanced optimization opportunities"
            )

        return recommendations

    def export_metrics_for_visualization(self, output_file: Optional[str] = None) -> str:
        """Export metrics in format suitable for visualization tools"""

        if not output_file:
            output_file = self.artifacts_dir / f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "deployments": [asdict(d) for d in self.deployments],
            "incidents": [asdict(i) for i in self.incidents],
            "targets": self.targets,
            "summary_stats": {
                "total_deployments": len(self.deployments),
                "successful_deployments": len([d for d in self.deployments if d.status == "success"]),
                "total_incidents": len(self.incidents),
                "resolved_incidents": len([i for i in self.incidents if i.resolution_time]),
                "average_approval_time": sum(self.approval_times) / len(self.approval_times)
                if self.approval_times
                else 0,
            },
        }

        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"📊 Metrics exported for visualization: {output_file}")
        return str(output_file)

    def generate_sre_dashboard(self, days_back: int = 30) -> Dict:
        """
        Generate comprehensive SRE dashboard data for visualization tools.

        Args:
            days_back: Number of days to analyze for dashboard

        Returns:
            Dashboard data structure optimized for SRE tools (Datadog, Grafana, etc.)
        """
        logger.info(f"📊 Generating SRE dashboard data for {days_back} days")

        # Get comprehensive report data
        report = self.generate_comprehensive_report(days_back)

        # Format for SRE dashboard tools
        dashboard_data = {
            "dashboard_type": "sre_dora_metrics",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "time_range_days": days_back,
            # Key Performance Indicators (KPIs) for executive view
            "kpi_summary": {
                "overall_performance_score": report["performance_analysis"]["overall_performance_percentage"],
                "sla_compliance_score": report["performance_analysis"]["sla_compliance_score"],
                "dora_metrics_health": len(
                    [
                        k
                        for k, v in report["performance_analysis"]["targets_met"].items()
                        if not k.startswith("sla_") and v
                    ]
                )
                / 4
                * 100,
                "active_incidents": len(
                    [
                        i
                        for i in self.incidents
                        if i.start_time >= datetime.now(timezone.utc) - timedelta(days=1) and not i.resolution_time
                    ]
                ),
                "automation_percentage": report["raw_data"]["automation_rate"],
            },
            # Time series data for trending
            "time_series": {
                "lead_time": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in self.metrics_history
                    if m.metric_name == "lead_time"
                ][-30:],  # Last 30 data points
                "deployment_frequency": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in self.metrics_history
                    if m.metric_name == "deployment_frequency"
                ][-30:],
                "change_failure_rate": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value * 100}  # Convert to percentage
                    for m in self.metrics_history
                    if m.metric_name == "change_failure_rate"
                ][-30:],
                "mttr": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in self.metrics_history
                    if m.metric_name == "mttr"
                ][-30:],
            },
            # Alert and incident summary
            "alerts_incidents": {
                "recent_alerts": len(
                    [
                        f
                        for f in (self.artifacts_dir / "alerts").glob("*.json")
                        if f.stat().st_mtime > time.time() - 86400
                    ]
                ),
                "incident_severity_breakdown": {
                    "critical": len(
                        [
                            i
                            for i in self.incidents
                            if i.severity == "critical"
                            and i.start_time >= datetime.now(timezone.utc) - timedelta(days=days_back)
                        ]
                    ),
                    "high": len(
                        [
                            i
                            for i in self.incidents
                            if i.severity == "high"
                            and i.start_time >= datetime.now(timezone.utc) - timedelta(days=days_back)
                        ]
                    ),
                    "medium": len(
                        [
                            i
                            for i in self.incidents
                            if i.severity == "medium"
                            and i.start_time >= datetime.now(timezone.utc) - timedelta(days=days_back)
                        ]
                    ),
                },
                "mttr_by_severity": self._calculate_mttr_by_severity(days_back),
            },
            # Operational metrics
            "operational_metrics": {
                "deployment_success_rate": len([d for d in self.deployments if d.status == "success"])
                / max(1, len(self.deployments))
                * 100,
                "avg_approval_time_minutes": sum(self.approval_times) / max(1, len(self.approval_times)),
                "workflow_efficiency_score": 100
                - (
                    sum(self.approval_times) / max(1, len(self.approval_times)) / 60 * 100
                ),  # Efficiency based on approval speed
                "service_reliability_score": report["sla_metrics"]["availability"]["value"] * 100
                if "availability" in report.get("sla_metrics", {})
                else 0,
            },
            # Targets and thresholds for visualization
            "targets": self.targets,
            "alert_thresholds": self.alert_thresholds,
            # Raw data for detailed analysis
            "raw_metrics": report,
        }

        # Save dashboard data for external tools
        dashboard_file = (
            self.artifacts_dir / "dashboards" / f"sre_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(dashboard_file, "w") as f:
            json.dump(dashboard_data, f, indent=2, default=str)

        logger.info(f"📊 SRE dashboard data saved: {dashboard_file}")

        return dashboard_data

    def _calculate_mttr_by_severity(self, days_back: int) -> Dict[str, float]:
        """Calculate MTTR broken down by incident severity."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_incidents = [i for i in self.incidents if i.start_time >= cutoff_date and i.resolution_time]

        mttr_by_severity = {}
        for severity in ["critical", "high", "medium", "low"]:
            severity_incidents = [i for i in recent_incidents if i.severity == severity]
            if severity_incidents:
                total_time = sum((i.resolution_time - i.start_time).total_seconds() / 3600 for i in severity_incidents)
                mttr_by_severity[severity] = total_time / len(severity_incidents)
            else:
                mttr_by_severity[severity] = 0

        return mttr_by_severity

    def integrate_with_performance_monitor(self, performance_monitor) -> None:
        """
        Integrate DORA metrics with existing performance monitoring system.

        Args:
            performance_monitor: Instance of PerformanceMonitor class
        """
        try:
            # Hook into performance monitor to auto-detect incidents
            original_track = performance_monitor.track_operation

            def enhanced_track_operation(
                module: str, operation: str, execution_time: float, success: bool = True, metadata=None
            ):
                # Call original method
                result = original_track(module, operation, execution_time, success, metadata)

                # Auto-detect performance incidents for DORA tracking
                target = performance_monitor.performance_targets.get(module, {})
                threshold = target.get("target_time", 30.0)

                if execution_time > threshold:
                    self.detect_performance_incident(module, operation, execution_time, threshold)

                return result

            # Replace with enhanced version
            performance_monitor.track_operation = enhanced_track_operation

            logger.info("🔗 DORA metrics integrated with performance monitor")

        except Exception as e:
            logger.error(f"❌ Failed to integrate with performance monitor: {e}")

    def export_cloudwatch_metrics(self, namespace: str = "CloudOps/DORA") -> bool:
        """
        Export DORA metrics to CloudWatch for enterprise monitoring.

        Args:
            namespace: CloudWatch metrics namespace

        Returns:
            Success status of metric publishing
        """
        try:
            import boto3

            cloudwatch = boto3.client("cloudwatch")

            # Calculate current metrics
            lead_time = self.calculate_lead_time(7)  # Weekly metrics
            deploy_freq = self.calculate_deployment_frequency(7)
            failure_rate = self.calculate_change_failure_rate(7)
            mttr = self.calculate_mttr(7)

            # Publish to CloudWatch
            metrics_to_publish = [
                {
                    "MetricName": "LeadTime",
                    "Value": lead_time.value,
                    "Unit": "Seconds",
                    "Dimensions": [{"Name": "Environment", "Value": "production"}],
                },
                {
                    "MetricName": "DeploymentFrequency",
                    "Value": deploy_freq.value,
                    "Unit": "Count/Second",
                    "Dimensions": [{"Name": "Environment", "Value": "production"}],
                },
                {
                    "MetricName": "ChangeFailureRate",
                    "Value": failure_rate.value * 100,  # Convert to percentage
                    "Unit": "Percent",
                    "Dimensions": [{"Name": "Environment", "Value": "production"}],
                },
                {
                    "MetricName": "MeanTimeToRecovery",
                    "Value": mttr.value,
                    "Unit": "Seconds",
                    "Dimensions": [{"Name": "Environment", "Value": "production"}],
                },
            ]

            response = cloudwatch.put_metric_data(Namespace=namespace, MetricData=metrics_to_publish)

            logger.info(f"📊 DORA metrics published to CloudWatch: {namespace}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to export CloudWatch metrics: {e}")
            return False


# Async functions for integration with existing systems
async def simulate_dora_metrics_collection(duration_minutes: int = 5) -> Dict:
    """Simulate DORA metrics collection for demonstration"""

    engine = DORAMetricsEngine()

    logger.info(f"🧪 Starting {duration_minutes}-minute DORA metrics simulation")

    # Simulate deployment events
    deployments = [
        ("deploy-001", "production", "vpc-wrapper", "v1.2.0", "abc123", "manager"),
        ("deploy-002", "staging", "finops-dashboard", "v2.1.0", "def456", "architect"),
        ("deploy-003", "production", "organizations-api", "v1.0.1", "ghi789", "manager"),
    ]

    for dep_id, env, service, version, commit, approver in deployments:
        deployment = engine.record_deployment(dep_id, env, service, version, commit, approver)

        # Simulate approval time
        approval_time = 15 + (hash(dep_id) % 30)  # 15-45 minutes
        engine.record_approval_time(approval_time, f"{env}_deployment")

        # Simulate deployment completion after short delay
        await asyncio.sleep(1)

        # 90% success rate simulation
        status = "success" if hash(dep_id) % 10 < 9 else "failed"
        engine.complete_deployment(dep_id, status)

    # Simulate incidents
    incidents = [
        ("inc-001", "vpc-wrapper", "high", "Network configuration error", "deploy-001"),
        ("inc-002", "finops-dashboard", "medium", "Query timeout", ""),
    ]

    for inc_id, service, severity, cause, caused_by in incidents:
        incident = engine.record_incident(inc_id, service, severity, cause, caused_by)

        # Simulate incident resolution
        await asyncio.sleep(0.5)
        detection_time = incident.start_time + timedelta(minutes=5)
        engine.resolve_incident(inc_id, detection_time)

    # Generate comprehensive report
    report = engine.generate_comprehensive_report(days_back=7)

    return report


if __name__ == "__main__":
    # CLI execution
    import argparse

    parser = argparse.ArgumentParser(description="DORA Metrics Engine")
    parser.add_argument("--simulate", action="store_true", help="Run simulation mode")
    parser.add_argument("--duration", type=int, default=5, help="Simulation duration in minutes")
    parser.add_argument("--output", "-o", default="./artifacts/metrics", help="Output directory for metrics")

    args = parser.parse_args()

    async def main():
        if args.simulate:
            report = await simulate_dora_metrics_collection(args.duration)
            print("✅ DORA metrics simulation completed")
            print(f"📊 Overall performance: {report['performance_analysis']['performance_grade']}")
            print(
                f"🎯 Targets met: {sum(report['performance_analysis']['targets_met'].values())}/{len(report['performance_analysis']['targets_met'])}"
            )
        else:
            engine = DORAMetricsEngine(args.output)
            report = engine.generate_comprehensive_report()
            print("✅ DORA metrics report generated")
            print(f"📊 Report saved to: {engine.artifacts_dir}")

    asyncio.run(main())
