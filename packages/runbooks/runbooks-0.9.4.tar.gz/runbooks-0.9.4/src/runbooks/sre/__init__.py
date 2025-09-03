#!/usr/bin/env python3
"""
SRE (Site Reliability Engineering) Module for CloudOps-Runbooks

This module provides enterprise-grade SRE automation capabilities including:
- Infrastructure monitoring and alerting
- Automated incident response and recovery
- Performance optimization and capacity planning
- Reliability engineering and chaos testing
- MCP integration reliability and health monitoring

Components:
- mcp_reliability_engine: Enterprise MCP reliability automation
- incident_response: Automated incident detection and response
- performance_monitoring: Real-time performance tracking
- chaos_engineering: Resilience testing framework
"""

from .mcp_reliability_engine import (
    MCPConnectionPool,
    MCPHealthCheck,
    MCPReliabilityEngine,
    run_mcp_reliability_suite,
)

# Import centralized version from main runbooks package
from runbooks import __version__

__all__ = [
    "MCPReliabilityEngine",
    "MCPConnectionPool",
    "MCPHealthCheck",
    "run_mcp_reliability_suite",
]
