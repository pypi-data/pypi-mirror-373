"""
Local database management for Clyrdia CLI - handles SQLite storage.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from datetime import datetime, timedelta

from ..models.results import BenchmarkResult
from ..models.user import PlanTier, UserRole
from ..core.console import console

class LocalDatabase:
    """Local SQLite database for zero-knowledge storage"""
    
    def __init__(self):
        self.db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Create the main benchmark_results table that the dashboard expects
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT NOT NULL,
                    benchmark_name TEXT,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT,
                    response TEXT,
                    latency_ms INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    success BOOLEAN,
                    error TEXT,
                    quality_score REAL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config TEXT,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT,
                    response TEXT,
                    latency_ms INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    success BOOLEAN,
                    error TEXT,
                    quality_scores TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (benchmark_id) REFERENCES benchmarks(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    model TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    test_hash TEXT NOT NULL,
                    drift_score REAL,
                    details TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # NEW: Multi-user and tier system tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    plan_tier TEXT NOT NULL DEFAULT 'developer',
                    monthly_credits INTEGER NOT NULL DEFAULT 100,
                    credits_remaining INTEGER NOT NULL DEFAULT 100,
                    credits_reset_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    plan_tier TEXT NOT NULL DEFAULT 'developer',
                    monthly_credits INTEGER NOT NULL DEFAULT 100,
                    max_members INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (team_id) REFERENCES teams(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(team_id, user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    team_id TEXT,
                    transaction_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    benchmark_id TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (team_id) REFERENCES teams(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feature_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    team_id TEXT,
                    feature TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (team_id) REFERENCES teams(id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_benchmark ON benchmark_results(benchmark_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_model ON benchmark_results(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_timestamp ON benchmark_results(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_benchmark ON results(benchmark_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_model ON results(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_timestamp ON results(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_plan_tier ON users(plan_tier)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_credits ON users(credits_remaining)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_team ON credit_transactions(team_id)")
            
            conn.commit()
    
    def save_benchmark(self, benchmark_id: str, name: str, description: str, config: Dict, tags: List[str]) -> str:
        """Save benchmark configuration"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO benchmarks (id, name, description, config, tags) VALUES (?, ?, ?, ?, ?)",
                (benchmark_id, name, description, json.dumps(config), json.dumps(tags))
            )
        return benchmark_id
    
    def save_result(self, result: BenchmarkResult, benchmark_id: Optional[str] = None) -> int:
        """Save benchmark result to both tables for compatibility"""
        with sqlite3.connect(self.db_path) as conn:
            # Save to the original results table
            cursor = conn.execute(
                """INSERT INTO results 
                   (benchmark_id, model, provider, test_name, prompt, response, 
                    latency_ms, input_tokens, output_tokens, cost, success, error, 
                    quality_scores, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    benchmark_id,
                    result.model,
                    result.provider,
                    result.test_name,
                    result.prompt,
                    result.response,
                    result.latency_ms,
                    result.input_tokens,
                    result.output_tokens,
                    result.cost,
                    result.success,
                    result.error,
                    json.dumps(result.quality_scores),
                    json.dumps(result.metadata),
                    result.timestamp
                )
            )
            
            # Also save to the benchmark_results table that the dashboard expects
            # Extract quality score (use first score if multiple, or 0.0 if none)
            quality_score = 0.0
            if result.quality_scores and len(result.quality_scores) > 0:
                if isinstance(result.quality_scores, dict):
                    quality_score = list(result.quality_scores.values())[0]
                elif isinstance(result.quality_scores, list):
                    quality_score = result.quality_scores[0]
                else:
                    quality_score = float(result.quality_scores)
            
            # Get benchmark name if available
            benchmark_name = None
            if benchmark_id:
                try:
                    name_cursor = conn.execute(
                        "SELECT name FROM benchmarks WHERE id = ?",
                        (benchmark_id,)
                    )
                    name_row = name_cursor.fetchone()
                    if name_row:
                        benchmark_name = name_row[0]
                except:
                    pass
            
            conn.execute(
                """INSERT INTO benchmark_results 
                   (benchmark_id, benchmark_name, model, provider, test_name, prompt, response, 
                    latency_ms, input_tokens, output_tokens, cost, success, error, 
                    quality_score, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    benchmark_id,
                    benchmark_name,
                    result.model,
                    result.provider,
                    result.test_name,
                    result.prompt,
                    result.response,
                    result.latency_ms,
                    result.input_tokens,
                    result.output_tokens,
                    result.cost,
                    result.success,
                    result.error,
                    quality_score,
                    json.dumps(result.metadata),
                    result.timestamp
                )
            )
            
            return cursor.lastrowid
    
    def get_recent_benchmarks(self, limit: int = 10) -> List[Dict]:
        """Get recent benchmark runs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM benchmarks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_model_performance(self, model: str, days: int = 30) -> pd.DataFrame:
        """Get model performance over time"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT timestamp, latency_ms, cost, success, quality_scores
                FROM results
                WHERE model = ? AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            return pd.read_sql_query(query, conn, params=(model,))
    
    def migrate_existing_data(self) -> int:
        """Migrate existing data from results table to benchmark_results table"""
        migrated_count = 0
        with sqlite3.connect(self.db_path) as conn:
            # Check if there's data to migrate
            cursor = conn.execute("SELECT COUNT(*) FROM results")
            total_results = cursor.fetchone()[0]
            
            if total_results == 0:
                return 0
            
            # Check if benchmark_results already has data
            cursor = conn.execute("SELECT COUNT(*) FROM benchmark_results")
            existing_benchmark_results = cursor.fetchone()[0]
            
            if existing_benchmark_results > 0:
                return 0  # Already migrated
            
            console.print(f"[yellow]🔄 Migrating {total_results} existing results to dashboard format...[/yellow]")
            
            # Get all results and migrate them
            cursor = conn.execute("""
                SELECT r.*, b.name as benchmark_name
                FROM results r
                LEFT JOIN benchmarks b ON r.benchmark_id = b.id
                ORDER BY r.timestamp
            """)
            
            for row in cursor.fetchall():
                # Extract quality score
                quality_score = 0.0
                if row['quality_scores']:
                    try:
                        scores = json.loads(row['quality_scores'])
                        if isinstance(scores, dict) and scores:
                            quality_score = list(scores.values())[0]
                        elif isinstance(scores, list) and scores:
                            quality_score = scores[0]
                        else:
                            quality_score = float(scores)
                    except:
                        quality_score = 0.0
                
                # Insert into benchmark_results
                conn.execute("""
                    INSERT INTO benchmark_results 
                    (benchmark_id, benchmark_name, model, provider, test_name, prompt, response, 
                     latency_ms, input_tokens, output_tokens, cost, success, error, 
                     quality_score, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['benchmark_id'],
                    row['benchmark_name'],
                    row['model'],
                    row['provider'],
                    row['test_name'],
                    row['prompt'],
                    row['response'],
                    row['latency_ms'],
                    row['input_tokens'],
                    row['output_tokens'],
                    row['cost'],
                    row['success'],
                    row['error'],
                    quality_score,
                    row['metadata'],
                    row['timestamp']
                ))
                migrated_count += 1
            
            conn.commit()
            console.print(f"[green]✅ Successfully migrated {migrated_count} results[/green]")
        
        return migrated_count

    def create_user(self, user_id: str, username: str, email: str, plan_tier: str = "developer") -> bool:
        """Create a new user with default plan"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Set default credits based on plan
                monthly_credits = self._get_default_credits(plan_tier)
                credits_reset_date = self._get_next_reset_date()
                
                conn.execute("""
                    INSERT INTO users (id, username, email, plan_tier, monthly_credits, credits_remaining, credits_reset_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, username, email, plan_tier, monthly_credits, monthly_credits, credits_reset_date))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error creating user: {str(e)}[/red]")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            console.print(f"[red]Error getting user: {str(e)}[/red]")
            return None
    
    def update_user_plan(self, user_id: str, new_plan: str) -> bool:
        """Update user's plan tier and reset credits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                monthly_credits = self._get_default_credits(new_plan)
                credits_reset_date = self._get_next_reset_date()
                
                conn.execute("""
                    UPDATE users 
                    SET plan_tier = ?, monthly_credits = ?, credits_remaining = ?, credits_reset_date = ?
                    WHERE id = ?
                """, (new_plan, monthly_credits, monthly_credits, credits_reset_date, user_id))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error updating user plan: {str(e)}[/red]")
            return False
    
    def deduct_credits(self, user_id: str, amount: int, description: str, benchmark_id: str = None, team_id: str = None) -> bool:
        """Deduct credits from user account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check current balance
                cursor = conn.execute("SELECT credits_remaining FROM users WHERE id = ?", (user_id,))
                current_credits = cursor.fetchone()[0]
                
                if current_credits < amount:
                    return False  # Insufficient credits
                
                # Deduct credits
                conn.execute("""
                    UPDATE users 
                    SET credits_remaining = credits_remaining - ?, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (amount, user_id))
                
                # Record transaction
                conn.execute("""
                    INSERT INTO credit_transactions (user_id, team_id, transaction_type, amount, description, benchmark_id)
                    VALUES (?, ?, 'debit', ?, ?, ?)
                """, (user_id, team_id, amount, description, benchmark_id))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error deducting credits: {str(e)}[/red]")
            return False
    
    def add_credits(self, user_id: str, amount: int, description: str, team_id: str = None) -> bool:
        """Add credits to user account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Add credits
                conn.execute("""
                    UPDATE users 
                    SET credits_remaining = credits_remaining + ?, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (amount, user_id))
                
                # Record transaction
                conn.execute("""
                    INSERT INTO credit_transactions (user_id, team_id, transaction_type, amount, description)
                    VALUES (?, ?, 'credit', ?, ?)
                """, (user_id, team_id, amount, description))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error adding credits: {str(e)}[/red]")
            return False
    
    def create_team(self, team_id: str, name: str, owner_id: str, plan_tier: str = "developer") -> bool:
        """Create a new team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                monthly_credits = self._get_default_credits(plan_tier)
                max_members = self._get_max_members(plan_tier)
                
                conn.execute("""
                    INSERT INTO teams (id, name, owner_id, plan_tier, monthly_credits, max_members)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (team_id, name, owner_id, plan_tier, monthly_credits, max_members))
                
                # Add owner as team member
                conn.execute("""
                    INSERT INTO team_members (team_id, user_id, role)
                    VALUES (?, ?, 'owner')
                """, (team_id, owner_id))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error creating team: {str(e)}[/red]")
            return False
    
    def add_team_member(self, team_id: str, user_id: str, role: str = "member") -> bool:
        """Add a user to a team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check team member limit
                cursor = conn.execute("SELECT max_members FROM teams WHERE id = ?", (team_id,))
                max_members = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM team_members WHERE team_id = ? AND is_active = 1", (team_id,))
                current_members = cursor.fetchone()[0]
                
                if current_members >= max_members:
                    return False  # Team is full
                
                conn.execute("""
                    INSERT INTO team_members (team_id, user_id, role)
                    VALUES (?, ?, ?)
                """, (team_id, user_id, role))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error adding team member: {str(e)}[/red]")
            return False
    
    def get_team_info(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get team details
                cursor = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
                team = cursor.fetchone()
                if not team:
                    return None
                
                # Get team members
                cursor = conn.execute("""
                    SELECT tm.*, u.username, u.email 
                    FROM team_members tm 
                    JOIN users u ON tm.user_id = u.id 
                    WHERE tm.team_id = ? AND tm.is_active = 1
                """, (team_id,))
                members = [dict(row) for row in cursor.fetchall()]
                
                team_dict = dict(team)
                team_dict['members'] = members
                team_dict['member_count'] = len(members)
                
                return team_dict
        except Exception as e:
            console.print(f"[red]Error getting team info: {str(e)}[/red]")
            return None
    
    def record_feature_usage(self, user_id: str, feature: str, team_id: str = None, metadata: str = None) -> bool:
        """Record feature usage for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO feature_usage (user_id, team_id, feature, usage_count, last_used, metadata)
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT usage_count + 1 FROM feature_usage WHERE user_id = ? AND feature = ?), 1),
                        CURRENT_TIMESTAMP, ?)
                """, (user_id, team_id, feature, user_id, feature, metadata))
                
                conn.commit()
                return True
        except Exception as e:
            console.print(f"[red]Error recording feature usage: {str(e)}[/red]")
            return False
    
    def get_credit_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get credit transaction history for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM credit_transactions 
                    WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days), (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            console.print(f"[red]Error getting credit history: {str(e)}[/red]")
            return []
    
    def get_team_credit_history(self, team_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get credit transaction history for a team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM credit_transactions 
                    WHERE team_id = ? AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days), (team_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            console.print(f"[red]Error getting team credit history: {str(e)}[/red]")
            return []
    
    def reset_monthly_credits(self) -> int:
        """Reset monthly credits for all users (called by cron job)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get users whose credits need to be reset
                cursor = conn.execute("""
                    SELECT id, plan_tier FROM users 
                    WHERE credits_reset_date <= date('now') AND is_active = 1
                """)
                
                reset_count = 0
                for row in cursor.fetchall():
                    user_id, plan_tier = row
                    monthly_credits = self._get_default_credits(plan_tier)
                    next_reset = self._get_next_reset_date()
                    
                    conn.execute("""
                        UPDATE users 
                        SET credits_remaining = ?, credits_reset_date = ?
                        WHERE id = ?
                    """, (monthly_credits, next_reset, user_id))
                    
                    reset_count += 1
                
                conn.commit()
                return reset_count
        except Exception as e:
            console.print(f"[red]Error resetting monthly credits: {str(e)}[/red]")
            return 0
    
    def _get_default_credits(self, plan_tier: str) -> int:
        """Get default monthly credits for a plan tier"""
        credit_map = {
            "developer": 100,
            "pro": 1000,
            "business": 25000
        }
        return credit_map.get(plan_tier, 100)
    
    def _get_max_members(self, plan_tier: str) -> int:
        """Get maximum team members for a plan tier"""
        member_map = {
            "developer": 1,
            "pro": 1,
            "business": 10
        }
        return member_map.get(plan_tier, 1)
    
    def _get_next_reset_date(self) -> str:
        """Get the next monthly reset date"""
        now = datetime.now()
        if now.day >= 25:  # Reset on 25th of each month
            next_month = now.replace(day=25) + timedelta(days=32)
            next_month = next_month.replace(day=25)
        else:
            next_month = now.replace(day=25)
        
        return next_month.strftime("%Y-%m-%d")
