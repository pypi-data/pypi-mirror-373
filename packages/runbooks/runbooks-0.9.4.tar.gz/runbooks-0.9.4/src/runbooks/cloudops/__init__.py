"""
CloudOps Automation API Wrapper
Enterprise-grade business scenario automation

Transforms CloudOps-Automation notebooks into unified business-focused APIs
with Rich CLI integration and type-safe business models.

Strategic Context:
- Source: 61 CloudOps-Automation notebooks in /README/CloudOps-Automation/AWS/
- Target: Business scenarios for CloudOps/SRE/FinOps stakeholders
- Integration: Multi-account strategies with Landing Zone support

NEW: Business Interface Layer for Notebook Usage
- Simple synchronous functions wrapping complex async operations
- Business-friendly parameters (cost thresholds, risk levels, savings targets)
- Executive-ready results with export capabilities
- Professional Rich CLI integration
"""

# Core async API classes (for advanced users)
from .cost_optimizer import CostOptimizer
from .security_enforcer import SecurityEnforcer  
from .lifecycle_manager import ResourceLifecycleManager
from .infrastructure_optimizer import InfrastructureOptimizer
from .monitoring_automation import MonitoringAutomation

# Business Interface Layer (recommended for notebook usage)
from .interfaces import (
    BusinessResultSummary,
    emergency_cost_response,
    optimize_unused_resources,
    governance_campaign,
    security_incident_response,
    optimize_infrastructure
)

# Enterprise Notebook Framework (NEW in v0.9.1)
from .notebook_framework import (
    NotebookFramework,
    NotebookMode,
    AuthenticationStatus,
    ScenarioMetadata
)

# Type-safe models
from .models import (
    CloudOpsExecutionResult,
    CostOptimizationResult,
    SecurityEnforcementResult,
    BusinessScenario,
    ResourceImpact
)

# Import centralized version from main runbooks package
from runbooks import __version__

__author__ = "CloudOps Enterprise Team"

__all__ = [
    # RECOMMENDED: Business Interface Functions (simple notebook usage)
    "BusinessResultSummary",
    "emergency_cost_response",
    "optimize_unused_resources",
    "governance_campaign", 
    "security_incident_response",
    "optimize_infrastructure",
    
    # ENTERPRISE NOTEBOOK FRAMEWORK (v0.9.1)
    "NotebookFramework",
    "NotebookMode", 
    "AuthenticationStatus",
    "ScenarioMetadata",
    
    # ADVANCED: Core API Classes (async operations)
    "CostOptimizer", 
    "SecurityEnforcer",
    "ResourceLifecycleManager", 
    "InfrastructureOptimizer",
    "MonitoringAutomation",
    
    # Type-Safe Models
    "CloudOpsExecutionResult",
    "CostOptimizationResult", 
    "SecurityEnforcementResult",
    "BusinessScenario",
    "ResourceImpact"
]

# Enterprise Usage Examples - Business Interface Layer
BUSINESS_SCENARIO_EXAMPLES = {
    "notebook_consolidation": {
        "description": "Enterprise notebook framework for consolidated scenarios (NEW in v0.9.1)",
        "simple_example": "from runbooks.cloudops import NotebookFramework, NotebookMode; framework = NotebookFramework(profile='default', mode=NotebookMode.EXECUTIVE)",
        "advanced_example": "See notebooks/cloudops/consolidated-cost-optimization.ipynb for comprehensive example"
    },
    "cost_emergency": {
        "description": "Emergency cost optimization for $10K+ monthly spikes",
        "simple_example": "from runbooks.cloudops import emergency_cost_response; result = emergency_cost_response(profile='billing', cost_spike_threshold=25000)",
        "advanced_example": "from runbooks.cloudops import CostOptimizer; optimizer = CostOptimizer(); optimizer.optimize_nat_gateways()"
    },
    "unused_resources": {
        "description": "Find unused AWS resources for immediate cost savings",
        "simple_example": "from runbooks.cloudops import optimize_unused_resources; result = optimize_unused_resources(profile='operations', minimum_cost_threshold=50)",
        "advanced_example": "from runbooks.cloudops import CostOptimizer; optimizer = CostOptimizer(); optimizer.optimize_idle_ec2_instances()"
    },
    "security_incident": {
        "description": "Automated security compliance remediation", 
        "simple_example": "from runbooks.cloudops import security_incident_response; result = security_incident_response(profile='security', incident_type='s3_encryption')",
        "advanced_example": "from runbooks.cloudops import SecurityEnforcer; enforcer = SecurityEnforcer(); enforcer.enforce_s3_encryption()"
    },
    "governance_campaign": {
        "description": "Multi-account governance and cleanup operations",
        "simple_example": "from runbooks.cloudops import governance_campaign; result = governance_campaign(management_profile='org-management', scope='organization')",
        "advanced_example": "from runbooks.cloudops import ResourceLifecycleManager; manager = ResourceLifecycleManager(); manager.enforce_tagging_standards()"
    },
    "infrastructure_optimization": {
        "description": "Infrastructure optimization and performance recovery",
        "simple_example": "from runbooks.cloudops import optimize_infrastructure; result = optimize_infrastructure(profile='operations', cost_reduction_target=25)",
        "advanced_example": "from runbooks.cloudops import InfrastructureOptimizer; optimizer = InfrastructureOptimizer(); optimizer.optimize_load_balancers()"
    }
}

def get_business_scenarios():
    """Get available business scenarios with examples."""
    return BUSINESS_SCENARIO_EXAMPLES