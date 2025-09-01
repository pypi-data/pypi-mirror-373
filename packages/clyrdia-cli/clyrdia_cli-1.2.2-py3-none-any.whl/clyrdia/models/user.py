"""
User models for Clyrdia CLI authentication and licensing.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class PlanTier(Enum):
    """Subscription plan tiers"""
    DEVELOPER = "developer"  # Free tier
    PRO = "pro"              # $25/month
    BUSINESS = "business"    # $500/month

class UserRole(Enum):
    """User roles within a team"""
    OWNER = "owner"          # Team owner with full access
    ADMIN = "admin"          # Admin with user management
    MEMBER = "member"        # Regular team member
    VIEWER = "viewer"        # Read-only access

@dataclass
class UserStatus:
    """User subscription and credit status"""
    user_name: str
    plan: PlanTier
    credits_remaining: int
    credits_monthly_limit: int
    resets_on: str
    api_key: str
    team_id: Optional[str] = None
    role: Optional[UserRole] = None
    team_name: Optional[str] = None
    max_team_members: Optional[int] = None
    has_cicd_access: bool = False

@dataclass
class CreditEstimate:
    """Credit cost estimation for a benchmark run"""
    total_tests: int
    cache_hits: int
    live_api_calls: int
    estimated_credits: int
    current_balance: int
    test_breakdown: Dict[str, int]

@dataclass
class TeamMember:
    """Team member information"""
    user_id: str
    user_name: str
    email: str
    role: UserRole
    joined_at: str
    last_active: str

@dataclass
class TeamInfo:
    """Team information and settings"""
    team_id: str
    team_name: str
    owner_id: str
    plan: PlanTier
    member_count: int
    max_members: int
    credits_monthly_limit: int
    has_cicd_access: bool
    created_at: str
    members: List[TeamMember]

@dataclass
class PlanFeatures:
    """Features available for each plan tier"""
    tier: PlanTier
    monthly_credits: int
    max_users: int
    has_cicd: bool
    has_advanced_reporting: bool
    has_team_management: bool
    has_priority_support: bool
    price_usd: int

# Plan configuration moved to config/tiers.py
