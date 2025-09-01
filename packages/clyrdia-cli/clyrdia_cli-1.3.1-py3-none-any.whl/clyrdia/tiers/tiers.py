"""
Tier system configuration for Clyrdia CLI.
Defines the three subscription tiers: Developer (Free), Pro, and Business.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class PlanTier(Enum):
    """Subscription plan tiers"""
    DEVELOPER = "developer"
    PRO = "pro"
    BUSINESS = "business"

class Feature(Enum):
    """Available features"""
    TEAM_MANAGEMENT = "team_management"
    CI_CD_INTEGRATION = "ci_cd_integration"
    ADVANCED_REPORTING = "advanced_reporting"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_BENCHMARKS = "custom_benchmarks"
    WHITE_LABEL = "white_label"
    API_ACCESS = "api_access"
    WEBHOOKS = "webhooks"
    AUDIT_LOGS = "audit_logs"
    SLA_GUARANTEES = "sla_guarantees"

@dataclass
class PlanFeatures:
    """Features available for each plan tier"""
    tier: PlanTier
    name: str
    monthly_credits: int
    max_users: int
    price_usd: int
    features: List[Feature]
    description: str
    target_audience: str
    upgrade_path: Optional[PlanTier] = None

# Plan configuration
TIER_CONFIG = {
    PlanTier.DEVELOPER: PlanFeatures(
        tier=PlanTier.DEVELOPER,
        name="Developer",
        monthly_credits=100,
        max_users=1,
        price_usd=0,
        features=[
            # Basic features only
        ],
        description="Free tier for individual developers to get started with AI benchmarking",
        target_audience="Individual developers, students, hobbyists",
        upgrade_path=PlanTier.PRO
    ),
    
    PlanTier.PRO: PlanFeatures(
        tier=PlanTier.PRO,
        name="Pro",
        monthly_credits=1000,
        max_users=1,
        price_usd=25,
        features=[
            Feature.CUSTOM_BENCHMARKS,
            Feature.API_ACCESS,
        ],
        description="Professional tier for serious individual developers and freelancers",
        target_audience="Professional developers, freelancers, small startups",
        upgrade_path=PlanTier.BUSINESS
    ),
    
    PlanTier.BUSINESS: PlanFeatures(
        tier=PlanTier.BUSINESS,
        name="Business",
        monthly_credits=25000,
        max_users=10,
        price_usd=500,
        features=[
            Feature.TEAM_MANAGEMENT,
            Feature.CI_CD_INTEGRATION,
            Feature.ADVANCED_REPORTING,
            Feature.PRIORITY_SUPPORT,
            Feature.CUSTOM_BENCHMARKS,
            Feature.API_ACCESS,
            Feature.WEBHOOKS,
            Feature.AUDIT_LOGS,
        ],
        description="Enterprise-grade tier for professional teams with advanced collaboration needs",
        target_audience="Professional teams of 2-10 developers, growing startups",
        upgrade_path=None
    )
}

def get_plan_features(tier: PlanTier) -> Optional[PlanFeatures]:
    """Get features for a specific plan tier"""
    return TIER_CONFIG.get(tier)

def get_all_plans() -> List[PlanFeatures]:
    """Get all available plans"""
    return list(TIER_CONFIG.values())

def get_upgrade_path(current_tier: PlanTier) -> Optional[PlanFeatures]:
    """Get the next tier for upgrading"""
    current_plan = TIER_CONFIG.get(current_tier)
    if current_plan and current_plan.upgrade_path:
        return TIER_CONFIG.get(current_plan.upgrade_path)
    return None

def has_feature(tier: PlanTier, feature: Feature) -> bool:
    """Check if a tier has access to a specific feature"""
    plan = TIER_CONFIG.get(tier)
    if plan:
        return feature in plan.features
    return False

def get_feature_comparison() -> Dict[str, List[bool]]:
    """Get feature comparison matrix for all plans"""
    comparison = {}
    
    for feature in Feature:
        feature_name = feature.value.replace('_', ' ').title()
        comparison[feature_name] = []
        
        for tier in PlanTier:
            comparison[feature_name].append(has_feature(tier, feature))
    
    return comparison

def get_plan_summary() -> str:
    """Get a formatted summary of all plans"""
    summary = "📋 Clyrdia Subscription Plans\n\n"
    
    for tier in PlanTier:
        plan = TIER_CONFIG[tier]
        summary += f"🔹 {plan.name} Tier\n"
        summary += f"   💰 Price: ${plan.price_usd}/month\n"
        summary += f"   🎯 Credits: {plan.monthly_credits:,}/month\n"
        summary += f"   👥 Users: {plan.max_users}\n"
        summary += f"   🎯 Target: {plan.target_audience}\n"
        
        if plan.upgrade_path:
            upgrade_plan = TIER_CONFIG[plan.upgrade_path]
            summary += f"   ⬆️  Upgrade to: {upgrade_plan.name} (${upgrade_plan.price_usd}/month)\n"
        
        summary += "\n"
    
    return summary

# Feature descriptions for help text
FEATURE_DESCRIPTIONS = {
    Feature.TEAM_MANAGEMENT: "Manage team members, roles, and permissions",
    Feature.CI_CD_INTEGRATION: "Integrate with CI/CD pipelines for automated testing",
    Feature.ADVANCED_REPORTING: "Advanced analytics, drift detection, and cost breakdowns",
    Feature.PRIORITY_SUPPORT: "Priority customer support with faster response times",
    Feature.CUSTOM_BENCHMARKS: "Create and customize benchmark test suites",
    Feature.API_ACCESS: "Programmatic access via REST API",
    Feature.WEBHOOKS: "Real-time notifications for benchmark results",
    Feature.AUDIT_LOGS: "Comprehensive audit trail for compliance",
    Feature.SLA_GUARANTEES: "Service level agreement guarantees",
    Feature.WHITE_LABEL: "White-label solutions for resellers"
}
