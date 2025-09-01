"""
Simple Local Dashboard for Clyrdia CLI
This module provides a simple, always-available local dashboard
"""

import webbrowser
import socket
import threading
import time
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

console = Console()

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for the dashboard"""
    
    def log_message(self, format, *args):
        """Suppress HTTP server logging - users don't need to see this"""
        return
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/" or path == "":
            self.send_dashboard_page()
        elif path == "/api/status":
            self.send_api_response(self.get_status_data())
        elif path == "/api/metrics":
            self.send_api_response(self.get_metrics_data())
        elif path == "/api/benchmarks":
            self.send_api_response(self.get_benchmarks_data())
        elif path == "/api/models":
            self.send_api_response(self.get_models_data())
        elif path == "/api/costs":
            self.send_api_response(self.get_costs_data())
        else:
            self.send_error(404, "Not Found")
    
    def send_dashboard_page(self):
        """Send the main dashboard HTML page"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_response(self, data: Dict[str, Any]):
        """Send JSON API response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def get_status_data(self) -> Dict[str, Any]:
        """Get dashboard status data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {
                "status": "no_data",
                "message": "No benchmark data found",
                "database_exists": False,
                "total_results": 0,
                "total_models": 0,
                "total_tests": 0
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if tables exist first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {
                    "status": "no_data",
                    "message": "Database exists but no benchmark tables found",
                    "database_exists": True,
                    "total_results": 0,
                    "total_models": 0,
                    "total_tests": 0
                }
            
            # Get basic stats with safe defaults
            cursor.execute("SELECT COUNT(*) FROM benchmark_results")
            total_results = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT model) FROM benchmark_results")
            total_models = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT test_name) FROM benchmark_results")
            total_tests = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "status": "ready",
                "database_exists": True,
                "total_results": total_results,
                "total_models": total_models,
                "total_tests": total_tests
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database_exists": True,
                "total_results": 0,
                "total_models": 0,
                "total_tests": 0
            }
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """Get metrics data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "recent_benchmarks": [], "total_count": 0}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "recent_benchmarks": [], "total_count": 0}
            
            # Get recent benchmarks with safe column names
            cursor.execute("""
                SELECT test_name, model, quality_score, cost, timestamp
                FROM benchmark_results
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            recent_benchmarks = []
            for row in cursor.fetchall():
                recent_benchmarks.append({
                    "test_name": row[0] or "Unknown Test",
                    "model_name": row[1] or "Unknown Model",
                    "quality_score": row[2] or 0.0,
                    "total_cost": row[3] or 0.0,
                    "timestamp": row[4] or "Unknown"
                })
            
            conn.close()
            
            return {
                "recent_benchmarks": recent_benchmarks,
                "total_count": len(recent_benchmarks)
            }
        except Exception as e:
            return {"error": str(e), "recent_benchmarks": [], "total_count": 0}
    
    def get_benchmarks_data(self) -> Dict[str, Any]:
        """Get benchmarks data"""
        return self.get_metrics_data()
    
    def get_models_data(self) -> Dict[str, Any]:
        """Get models data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "models": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "models": []}
            
            # Get model performance with safe column names
            cursor.execute("""
                SELECT model, AVG(quality_score) as avg_score, COUNT(*) as test_count
                FROM benchmark_results
                GROUP BY model
                ORDER BY avg_score DESC
            """)
            
            models = []
            for row in cursor.fetchall():
                models.append({
                    "model_name": row[0] or "Unknown Model",
                    "avg_score": round(row[1], 3) if row[1] else 0,
                    "test_count": row[2] or 0
                })
            
            conn.close()
            
            return {"models": models}
        except Exception as e:
            return {"error": str(e), "models": []}
    
    def get_costs_data(self) -> Dict[str, Any]:
        """Get costs data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "total_cost": 0, "avg_cost": 0, "total_tests": 0}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "total_cost": 0, "avg_cost": 0, "total_tests": 0}
            
            # Get cost summary with safe column names
            cursor.execute("""
                SELECT 
                    SUM(cost) as total_cost,
                    AVG(cost) as avg_cost,
                    COUNT(*) as total_tests
                FROM benchmark_results
            """)
            
            row = cursor.fetchone()
            if row:
                cost_data = {
                    "total_cost": round(row[0], 4) if row[0] else 0,
                    "avg_cost": round(row[1], 4) if row[1] else 0,
                    "total_tests": row[2] or 0
                }
            else:
                cost_data = {"total_cost": 0, "avg_cost": 0, "total_tests": 0}
            
            conn.close()
            
            return cost_data
        except Exception as e:
            return {"error": str(e), "total_cost": 0, "avg_cost": 0, "total_tests": 0}
    
    def generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clyrdia Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        
        .metric-value {
            font-weight: bold;
            color: #333;
            font-size: 1.1rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #4CAF50;
        }
        
        .status-offline {
            background: #f44336;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s ease;
            margin-bottom: 20px;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Clyrdia Dashboard</h1>
            <p>AI Benchmarking & Performance Analytics</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>📊 System Status</h2>
                <div id="status-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 Model Performance</h2>
                <div id="models-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>💰 Cost Analysis</h2>
                <div id="costs-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Recent Benchmarks</h2>
                <div id="benchmarks-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAllData();
        });
        
        function loadAllData() {
            loadStatus();
            loadModels();
            loadCosts();
            loadBenchmarks();
        }
        
        function refreshData() {
            // Show loading state
            document.querySelectorAll('.loading').forEach(el => {
                el.style.display = 'block';
            });
            
            // Clear previous content
            document.getElementById('status-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('models-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('costs-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('benchmarks-content').innerHTML = '<div class="loading">Refreshing...</div>';
            
            // Load fresh data
            loadAllData();
            
            // Show success message
            setTimeout(() => {
                const refreshBtn = document.querySelector('.refresh-btn');
                const originalText = refreshBtn.textContent;
                refreshBtn.textContent = '✅ Refreshed!';
                refreshBtn.style.background = '#4CAF50';
                
                setTimeout(() => {
                    refreshBtn.textContent = originalText;
                    refreshBtn.style.background = '#667eea';
                }, 2000);
            }, 500);
        }
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayStatus(data);
            } catch (error) {
                console.error('Status load error:', error);
                document.getElementById('status-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading status:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadModels() {
            try {
                const response = await fetch('/api/models');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayModels(data);
            } catch (error) {
                console.error('Models load error:', error);
                document.getElementById('models-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading models:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadCosts() {
            try {
                const response = await fetch('/api/costs');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayCosts(data);
            } catch (error) {
                console.error('Costs load error:', error);
                document.getElementById('costs-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading costs:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadBenchmarks() {
            try {
                const response = await fetch('/api/benchmarks');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayBenchmarks(data);
            } catch (error) {
                console.error('Benchmarks load error:', error);
                document.getElementById('benchmarks-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading benchmarks:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        function displayStatus(data) {
            const content = document.getElementById('status-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (data.status === 'no_data') {
                content.innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value"><span class="status-indicator status-offline"></span>No Data</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Database</span>
                        <span class="metric-value">Not Found</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Message</span>
                        <span class="metric-value">Run your first benchmark</span>
                    </div>
                `;
            } else {
                content.innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value"><span class="status-indicator status-online"></span>Ready</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Results</span>
                        <span class="metric-value">${data.total_results}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Models Tested</span>
                        <span class="metric-value">${data.total_models}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Tests Run</span>
                        <span class="metric-value">${data.total_tests}</span>
                    </div>
                `;
            }
        }
        
        function displayModels(data) {
            const content = document.getElementById('models-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.models || data.models.length === 0) {
                content.innerHTML = '<div class="success">No models tested yet</div>';
                return;
            }
            
            let html = '';
            data.models.forEach(model => {
                html += `
                    <div class="metric">
                        <span class="metric-label">${model.model_name}</span>
                        <span class="metric-value">${model.avg_score} (${model.test_count} tests)</span>
                    </div>
                `;
            });
            
            content.innerHTML = html;
        }
        
        function displayCosts(data) {
            const content = document.getElementById('costs-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            content.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Total Cost</span>
                    <span class="metric-value">$${data.total_cost}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Average Cost</span>
                    <span class="metric-value">$${data.avg_cost}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">${data.total_tests}</span>
                </div>
            `;
        }
        
        function displayBenchmarks(data) {
            const content = document.getElementById('benchmarks-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.recent_benchmarks || data.recent_benchmarks.length === 0) {
                content.innerHTML = '<div class="success">No benchmarks run yet</div>';
                return;
            }
            
            let html = '';
            data.recent_benchmarks.slice(0, 5).forEach(benchmark => {
                html += `
                    <div class="metric">
                        <span class="metric-label">${benchmark.test_name}</span>
                        <span class="metric-value">${benchmark.model_name}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Score</span>
                        <span class="metric-value">${benchmark.quality_score}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Cost</span>
                        <span class="metric-value">$${benchmark.total_cost}</span>
                    </div>
                `;
            });
            
            content.innerHTML = html;
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadAllData, 30000);
    </script>
</body>
</html>
        """

class SimpleDashboard:
    """Simple dashboard server that works on any platform"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def is_dashboard_running(self) -> bool:
        """Check if dashboard is running on the specified port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except Exception:
            return False
    
    def start_dashboard(self):
        """Start the simple HTTP dashboard server"""
        if self.is_dashboard_running():
            console.print(f"[green]✅ Dashboard is already running on port {self.port}[/green]")
            return True
        
        try:
            # Start HTTP server in a separate thread
            self.server = HTTPServer((self.host, self.port), SimpleDashboardHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            # Wait a moment for server to start
            time.sleep(1)
            
            if self.is_dashboard_running():
                console.print(f"[green]✅ Simple Dashboard started successfully on port {self.port}[/green]")
                console.print(f"[dim]💡 Dashboard will continue running in the background[/dim]")
                console.print(f"[dim]💡 You can close this terminal and dashboard will remain accessible[/dim]")
                return True
            else:
                console.print(f"[red]❌ Failed to start dashboard on port {self.port}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error starting dashboard: {str(e)}[/red]")
            return False
    
    def stop_dashboard(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server = None
            console.print(f"[yellow]🛑 Dashboard stopped on port {self.port}[/yellow]")
        else:
            console.print(f"[yellow]🛑 No dashboard found running on port {self.port}[/yellow]")
    
    def open_dashboard_url(self):
        """Show the dashboard URL for user to click"""
        url = f"http://{self.host}:{self.port}"
        console.print(f"[green]🌐 Dashboard is ready![/green]")
        console.print(f"[blue]🔗 Dashboard URL: {url}[/blue]")
        console.print("[yellow]💡 To access your dashboard:[/yellow]")
        console.print(f"[yellow]   1. Copy this URL:[/yellow] [bold blue]{url}[/bold blue]")
        console.print("[yellow]   2. Paste it into your web browser[/yellow]")
        console.print(f"[yellow]   3. Or run:[/yellow] [bold]open {url}[/bold]")
        console.print(f"[dim]💡 If the link doesn't work, manually copy: {url}[/dim]")
        
        # Try to open the dashboard in the default browser
        try:
            webbrowser.open(url)
            console.print("[green]✅ Opened dashboard in your default browser![/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Couldn't auto-open browser: {str(e)}[/yellow]")
            console.print(f"[yellow]   Please manually copy and paste: {url}[/yellow]")
        
        console.print(f"\n[dim]💡 Dashboard is now running in the background on port {self.port}[/dim]")
        console.print(f"[dim]💡 You can run other commands while the dashboard continues running[/dim]")
    
    def show_dashboard_instructions(self):
        """Display dashboard information"""
        console.print()
        
        if self.is_dashboard_running():
            url = f"http://{self.host}:{self.port}"
            console.print(Panel.fit(
                f"[bold green]✅ Dashboard is running![/bold green]\n\n"
                f"🌐 Access your dashboard at: [bold blue][link={url}]{url}[/link][/bold blue]\n\n"
                "The dashboard is now available and will show:\n"
                "• 📊 Performance metrics (even with 0 data)\n"
                "• 🤖 Model comparisons\n"
                "• 💰 Cost analysis\n"
                "• 📈 Benchmark results\n\n"
                "💡 Click the link above to open in your browser\n"
                "🔄 Use the refresh button to update data\n"
                "📊 Dashboard works even with 0 credits - shows all historical data!",
                border_style="green",
                title="[bold]Dashboard Ready[/bold]"
            ))
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠️  Dashboard not running[/bold yellow]\n\n"
                "Starting simple dashboard...",
                border_style="yellow",
                title="[bold]Starting Dashboard[/bold]"
            ))
            
            if self.start_dashboard():
                self.show_dashboard_instructions()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def check_dashboard_status(self):
        """Check and display dashboard status"""
        console.print()
        
        if self.is_dashboard_running():
            status_text = f"[green]✅ Dashboard is running on port {self.port}[/green]"
            url = f"http://{self.host}:{self.port}"
            
            console.print(Panel.fit(
                f"{status_text}\n\n"
                f"[bold]🌐 Access at:[/bold] [bold blue][link={url}]{url}[/link][/bold blue]\n\n"
                "[bold]Features:[/bold]\n"
                "• 📊 Real-time metrics and analytics\n"
                "• 🤖 Model performance comparison\n"
                "• 💰 Cost analysis and optimization\n"
                "• 📈 Historical trend analysis\n"
                "• 🔍 Detailed result inspection\n\n"
                "💡 Click the link above to open in your browser\n"
                "🔄 Use the refresh button to update data\n"
                "📊 Dashboard works even with 0 credits - shows all historical data!\n\n"
                "[bold]Server Info:[/bold]\n"
                f"• Host: {self.host}\n"
                f"• Port: {self.port}\n"
                "• Status: Running in background\n"
                "• Persistence: Will continue after CLI closes",
                border_style="green",
                title="[bold]Dashboard Status[/bold]"
            ))
        else:
            console.print(Panel.fit(
                f"[yellow]⚠️  Dashboard is not running on port {self.port}[/yellow]\n\n"
                "Starting dashboard...",
                border_style="yellow",
                title="[bold]Dashboard Status[/bold]"
            ))
            
            if self.start_dashboard():
                self.check_dashboard_status()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def migrate_data(self):
        """Provide instructions for data migration"""
        console.print()
        
        console.print(Panel.fit(
            "[bold bright_cyan]🔄 Data Migration[/bold bright_cyan]\n\n"
            "Your existing benchmark data is automatically compatible with the dashboard!\n\n"
            "[bold]The dashboard will:[/bold]\n"
            "• 📊 Show all your historical results\n"
            "• 🤖 Compare model performance over time\n"
            "• 💰 Track cost trends and optimization\n"
            "• 📈 Provide insights and analytics\n\n"
            "[bold]No manual migration needed:[/bold]\n"
            "• Just run benchmarks normally\n"
            "• Data appears automatically in the dashboard\n"
            "• Real-time updates as you test\n\n"
            "🚀 Start benchmarking and see your data in the dashboard!",
            border_style="bright_cyan",
            title="[bold]Data Migration Guide[/bold]"
        ))

# Create a global dashboard instance
dashboard = SimpleDashboard()

# Export functions for CLI use
def start_dashboard():
    """Start the dashboard"""
    return dashboard.start_dashboard()

def stop_dashboard():
    """Stop the dashboard"""
    return dashboard.stop_dashboard()

def check_dashboard_status():
    """Check dashboard status"""
    return dashboard.check_dashboard_status()

def show_dashboard_instructions():
    """Show dashboard instructions"""
    return dashboard.show_dashboard_instructions()

def open_dashboard_url():
    """Open dashboard URL"""
    return dashboard.open_dashboard_url()

def migrate_data():
    """Show data migration info"""
    return dashboard.migrate_data()
