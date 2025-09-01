"""
GitHub Actions CI/CD template for Clyrdia AI benchmarking.
Provides real, working GitHub Actions workflows for automated AI model testing.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GitHubActionsTemplate:
    """GitHub Actions CI/CD template generator"""
    
    def generate_basic_workflow(self, 
                               workflow_name: str = "AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               python_version: str = "3.9",
                               trigger_on: List[str] = None,
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate basic GitHub Actions workflow for AI benchmarking"""
        
        if trigger_on is None:
            trigger_on = ["push", "pull_request"]
        
        workflow = f"""name: {workflow_name}

on:
  {chr(10).join(f'  {trigger}:' for trigger in trigger_on)}
    branches: [ main, develop ]
  workflow_dispatch:  # Allow manual trigger

env:
  PYTHON_VERSION: '{python_version}'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{{{ runner.os }}}}-pip-${{{{ hashFiles('**/requirements.txt') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-pip-
          
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install clyrdia-cli
        pip install -r requirements.txt || echo "No requirements.txt found"
        
    - name: Setup environment variables
      run: |
        echo "🔧 Setting up environment variables..."
        # Create .env file from GitHub secrets
        cat > .env << EOF
        # Clyrdia API key (if you have one)
        CLYRIDIA_API_KEY=${{{{ secrets.CLYRDIA_API_KEY }}}}
        
        # AI Provider API keys
        OPENAI_API_KEY=${{{{ secrets.OPENAI_API_KEY }}}}
        ANTHROPIC_API_KEY=${{{{ secrets.ANTHROPIC_API_KEY }}}}
        EOF
        
        echo "✅ Environment variables configured"
        
    - name: Run Clyrdia benchmark
      run: |
        echo "🚀 Starting AI benchmark with Clyrdia..."
        clyrdia-cli run --config {benchmark_file} --output-format json
        
    - name: Upload benchmark results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results
        path: |
          benchmark_results/
          *.json
          *.csv
          
    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          let comment = '🤖 **AI Benchmark Results**\\n\\n';
          
          try {{
            const results = JSON.parse(fs.readFileSync('benchmark_results.json', 'utf8'));
            comment += `✅ **Benchmark completed successfully**\\n`;
            comment += `📊 **Models tested:** ${{results.models?.length || 'N/A'}}\\n`;
            comment += `💰 **Credits used:** ${{results.credits_used || 'N/A'}}\\n`;
            comment += `⏱️ **Total time:** ${{results.total_time || 'N/A'}}s\\n\\n`;
            
            if (results.quality_scores) {{
              comment += '**Quality Scores:**\\n';
              Object.entries(results.quality_scores).forEach(([model, score]) => {{
                comment += `- ${{model}}: ${{score.toFixed(2)}}\\n`;
              }});
            }}
          }} catch (error) {{
            comment += '❌ **Benchmark failed or results not found**\\n';
            comment += `Error: ${{error.message}}`;
          }}
          
          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});
"""
        return workflow
    
    def generate_advanced_workflow(self,
                                  workflow_name: str = "Advanced AI Benchmark",
                                  benchmark_file: str = "benchmark.yaml",
                                  python_version: str = "3.9",
                                  quality_gate: float = 0.8,
                                  cost_threshold: float = 10.0,
                                  trigger_on: List[str] = None) -> str:
        """Generate advanced GitHub Actions workflow with quality gates and cost monitoring"""
        
        workflow = f"""name: {workflow_name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Run weekly on Monday at 2 AM
  workflow_dispatch:

env:
  PYTHON_VERSION: '{python_version}'
  QUALITY_GATE: {quality_gate}
  COST_THRESHOLD: {cost_threshold}

jobs:
  benchmark:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
        
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.cache/pip
          ~/.clyrdia
        key: ${{{{ runner.os }}}}-deps-${{{{ hashFiles('**/requirements.txt', '**/benchmark.yaml') }}}}
        restore-keys: |
          ${{{{ runner.os }}}}-deps-
          
    - name: Install Clyrdia CLI
      run: |
        python -m pip install --upgrade pip
        pip install clyrdia-cli
        pip install -r requirements.txt || echo "No requirements.txt found"
        
    - name: Setup environment variables
      run: |
        echo "🔧 Setting up environment variables..."
        # Create .env file from GitHub secrets
        cat > .env << EOF
        # Clyrdia API key (if you have one)
        CLYRIDIA_API_KEY=${{{{ secrets.CLYRDIA_API_KEY }}}}
        
        # AI Provider API keys
        OPENAI_API_KEY=${{{{ secrets.OPENAI_API_KEY }}}}
        ANTHROPIC_API_KEY=${{{{ secrets.ANTHROPIC_API_KEY }}}}
        EOF
        
        echo "✅ Environment variables configured"
        
    - name: Check credit balance
      run: |
        echo "💰 Checking Clyrdia credit balance..."
        clyrdia-cli status
        
    - name: Run AI benchmark
      id: benchmark
      run: |
        echo "🚀 Starting advanced AI benchmark..."
        clyrdia-cli run --config {benchmark_file} --output-format json --save-results
        
    - name: Analyze results
      id: analyze
      run: |
        echo "📊 Analyzing benchmark results..."
        
        # Parse results and set outputs
        if [ -f "benchmark_results.json" ]; then
          echo "::set-output name=has_results::true"
          
          # Extract quality scores
          QUALITY_SCORE=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    scores = data.get("quality_scores", {{}})
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        print("{{:.3f}}".format(avg_score))
    else:
        print('0.0')
")
          
          echo "::set-output name=quality_score::$QUALITY_SCORE"
          
          # Extract cost
          COST=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    cost = data.get('total_cost', 0.0)
    print("{{:.2f}}".format(cost))
")
          
          echo "::set-output name=total_cost::$COST"
          
          echo "Quality Score: $QUALITY_SCORE"
          echo "Total Cost: $$COST"
        else
          echo "::set-output name=has_results::false"
          echo "::set-output name=quality_score::0.0"
          echo "::set-output name=total_cost::0.0"
        fi
        
    - name: Quality Gate Check
      if: steps.analyze.outputs.has_results == 'true'
      run: |
        QUALITY_SCORE="${{{{ steps.analyze.outputs.quality_score }}}}"
        QUALITY_GATE="${{{{ env.QUALITY_GATE }}}}"
        
        echo "Quality Score: $QUALITY_SCORE"
        echo "Quality Gate: $QUALITY_GATE"
        
        if (( $(echo "$QUALITY_SCORE >= $QUALITY_GATE" | bc -l) )); then
          echo "✅ Quality gate passed: $QUALITY_SCORE >= $QUALITY_GATE"
        else
          echo "❌ Quality gate failed: $QUALITY_SCORE < $QUALITY_GATE"
          exit 1
        fi
        
    - name: Cost Threshold Check
      if: steps.analyze.outputs.has_results == 'true'
      run: |
        TOTAL_COST="${{{{ steps.analyze.outputs.total_cost }}}}"
        COST_THRESHOLD="${{{{ env.COST_THRESHOLD }}}}"
        
        echo "Total Cost: $$TOTAL_COST"
        echo "Cost Threshold: $$COST_THRESHOLD"
        
        if (( $(echo "$TOTAL_COST <= $COST_THRESHOLD" | bc -l) )); then
          echo "✅ Cost threshold passed: $$TOTAL_COST <= $$COST_THRESHOLD"
        else
          echo "⚠️ Cost threshold exceeded: $$TOTAL_COST > $$COST_THRESHOLD"
          # Don't fail the build, just warn
        fi
        
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results-${{{{ github.run_number }}}}
        path: |
          benchmark_results/
          *.json
          *.csv
          *.log
          
    - name: Create summary
      if: always()
      run: |
        echo "## 🤖 AI Benchmark Summary" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        
        if [ "${{{{ steps.analyze.outputs.has_results }}}}" == "true" ]; then
          echo "✅ **Benchmark completed successfully**" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Results:**" >> $GITHUB_STEP_SUMMARY
          echo "- Quality Score: ${{{{ steps.analyze.outputs.quality_score }}}}" >> $GITHUB_STEP_SUMMARY
          echo "- Total Cost: $${{{{ steps.analyze.outputs.total_cost }}}}" >> $GITHUB_STEP_SUMMARY
          echo "- Quality Gate: ${{{{ env.QUALITY_GATE }}}}" >> $GITHUB_STEP_SUMMARY
          echo "- Cost Threshold: $${{{{ env.COST_THRESHOLD }}}}" >> $GITHUB_STEP_SUMMARY
        else
          echo "❌ **Benchmark failed or no results found**" >> $GITHUB_STEP_SUMMARY
        fi
        
    - name: Comment on PR
      if: github.event_name == 'pull_request' && steps.analyze.outputs.has_results == 'true'
      uses: actions/github-script@v6
      with:
        script: |
          const qualityScore = parseFloat('${{{{ steps.analyze.outputs.quality_score }}}}');
          const totalCost = parseFloat('${{{{ steps.analyze.outputs.total_cost }}}}');
          const qualityGate = parseFloat('${{{{ env.QUALITY_GATE }}}}');
          const costThreshold = parseFloat('${{{{ env.COST_THRESHOLD }}}}');
          
          let comment = '🤖 **AI Benchmark Results**\\n\\n';
          
          // Quality gate status
          if (qualityScore >= qualityGate) {{
            comment += '✅ **Quality Gate PASSED** (' + qualityScore.toFixed(3) + ' >= ' + qualityGate + ')\\n';
          }} else {{
            comment += '❌ **Quality Gate FAILED** (' + qualityScore.toFixed(3) + ' < ' + qualityGate + ')\\n';
          }}
          
          // Cost threshold status
          if (totalCost <= costThreshold) {{
            comment += '✅ **Cost Threshold PASSED** ($' + totalCost.toFixed(2) + ' <= $' + costThreshold + ')\\n';
          }} else {{
            comment += '⚠️ **Cost Threshold EXCEEDED** ($' + totalCost.toFixed(2) + ' > $' + costThreshold + ')\\n';
          }}
          
          comment += '\\n📊 **Details:**\\n';
          comment += '- Quality Score: ' + qualityScore.toFixed(3) + '\\n';
          comment += '- Total Cost: $' + totalCost.toFixed(2) + '\\n';
          comment += '- Quality Gate: ' + qualityGate + '\\n';
          comment += '- Cost Threshold: $' + costThreshold + '\\n';
          
          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});
"""
        return workflow
    
    def generate_mlops_workflow(self,
                               workflow_name: str = "MLOps AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               model_registry: str = "mlflow",
                               deployment_target: str = "kubernetes",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0,
                               trigger_on: List[str] = None) -> str:
        """Generate MLOps-focused workflow for AI model deployment"""
        
        workflow = f"""name: {workflow_name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [published]
  workflow_dispatch:

env:
  MODEL_REGISTRY: {model_registry}
  DEPLOYMENT_TARGET: {deployment_target}

jobs:
  benchmark:
    runs-on: ubuntu-latest
    outputs:
      quality_score: ${{{{ steps.analyze.outputs.quality_score }}}}
      model_version: ${{{{ steps.version.outputs.version }}}}
      
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install clyrdia-cli mlflow kubernetes || echo "Installing core dependencies"
        
    - name: Setup environment variables
      run: |
        echo "🔧 Setting up environment variables..."
        # Create .env file from GitHub secrets
        cat > .env << EOF
        # Clyrdia API key (if you have one)
        CLYRIDIA_API_KEY=${{{{ secrets.CLYRDIA_API_KEY }}}}
        
        # AI Provider API keys
        OPENAI_API_KEY=${{{{ secrets.OPENAI_API_KEY }}}}
        ANTHROPIC_API_KEY=${{{{ secrets.ANTHROPIC_API_KEY }}}}
        EOF
        
        echo "✅ Environment variables configured"
        
    - name: Version model
      id: version
      run: |
        echo "🏷️ Versioning model..."
        VERSION=$(date +%Y%m%d.%H%M%S)
        echo "::set-output name=version::$VERSION"
        echo "Model version: $VERSION"
        
    - name: Run AI benchmark
      run: |
        echo "🚀 Running AI benchmark for version ${{{{ steps.version.outputs.version }}}}..."
        clyrdia-cli run --config {benchmark_file} --output-format json --save-results
        
    - name: Analyze benchmark results
      id: analyze
      run: |
        echo "📊 Analyzing benchmark results..."
        
        if [ -f "benchmark_results.json" ]; then
          QUALITY_SCORE=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    scores = data.get("quality_scores", {{}})
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        print("{{:.3f}}".format(avg_score))
    else:
        print('0.0')
")
          
          echo "::set-output name=quality_score::$QUALITY_SCORE"
          echo "Quality Score: $QUALITY_SCORE"
        else
          echo "::set-output name=quality_score::0.0"
        fi
        
    - name: Quality gate
      run: |
        QUALITY_SCORE="${{{{ steps.analyze.outputs.quality_score }}}}"
        
        if (( $(echo "$QUALITY_SCORE >= 0.8" | bc -l) )); then
          echo "✅ Quality gate passed: $QUALITY_SCORE >= 0.8"
        else
          echo "❌ Quality gate failed: $QUALITY_SCORE < 0.8"
          exit 1
        fi
        
    - name: Log to MLflow
      if: env.MODEL_REGISTRY == 'mlflow'
      run: |
        echo "📝 Logging to MLflow..."
        mlflow run . --env-manager=local
        
    - name: Deploy to staging
      if: github.ref == 'refs/heads/develop'
      run: |
        echo "🚀 Deploying to staging..."
        # Add your staging deployment logic here
        
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: |
        echo "🚀 Deploying to production..."
        # Add your production deployment logic here
        
    - name: Create release
      if: github.event_name == 'release'
      run: |
        echo "🎉 Creating release for version ${{{{ steps.version.outputs.version }}}}..."
        # Add your release logic here
        
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: mlops-artifacts-${{{{ steps.version.outputs.version }}}}
        path: |
          benchmark_results/
          models/
          *.json
          *.log
"""
        return workflow
    
    def generate_workflow_file(self, 
                              template_type: str = "basic",
                              **kwargs) -> str:
        """Generate workflow file based on template type"""
        
        if template_type == "basic":
            return self.generate_basic_workflow(**kwargs)
        elif template_type == "advanced":
            return self.generate_advanced_workflow(**kwargs)
        elif template_type == "mlops":
            return self.generate_mlops_workflow(**kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def save_workflow(self, 
                     template_type: str = "basic",
                     output_path: str = ".github/workflows",
                     **kwargs) -> str:
        """Generate and save workflow file"""
        
        workflow_content = self.generate_workflow_file(template_type, **kwargs)
        
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if template_type == "basic":
            filename = "ai-benchmark.yml"
        elif template_type == "advanced":
            filename = "advanced-ai-benchmark.yml"
        elif template_type == "mlops":
            filename = "mlops-ai-benchmark.yml"
        else:
            filename = f"{template_type}-ai-benchmark.yml"
        
        # Save workflow file
        workflow_path = output_dir / filename
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        return str(workflow_path)
