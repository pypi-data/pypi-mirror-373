"""
GitLab CI/CD template for Clyrdia AI benchmarking.
Provides real, working GitLab CI pipelines for automated AI model testing.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GitLabCITemplate:
    """GitLab CI/CD template generator"""
    
    def generate_basic_pipeline(self,
                               pipeline_name: str = "AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate basic GitLab CI pipeline for AI benchmarking"""
        
        pipeline = f"""# {pipeline_name}
# GitLab CI pipeline for automated AI benchmarking with Clyrdia

variables:
  PYTHON_VERSION: "{python_version}"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/
    - ~/.clyrdia/

stages:
  - setup
  - benchmark
  - results

before_script:
  - python --version
  - pip install --upgrade pip

setup:
  stage: setup
  image: python:{python_version}-slim
  script:
    - echo "🔧 Setting up environment..."
    - pip install clyrdia-cli
    - pip install -r requirements.txt || echo "No requirements.txt found"
    - |
      echo "🔧 Setting up environment variables..."
      # Create .env file from GitLab CI variables
      cat > .env << EOF
      # Clyrdia API key (if you have one)
      CLYRIDIA_API_KEY=$CLYRIDIA_API_KEY
      
      # AI Provider API keys
      OPENAI_API_KEY=$OPENAI_API_KEY
      ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
      EOF
      echo "✅ Environment variables configured"
    - clyrdia-cli status
  artifacts:
    paths:
      - ~/.clyrdia/
      - .env
    expire_in: 1 hour

benchmark:
  stage: benchmark
  image: python:{python_version}-slim
  dependencies:
    - setup
  script:
    - echo "🚀 Starting AI benchmark with Clyrdia..."
    - clyrdia-cli run --config {benchmark_file} --output-format json
    - echo "✅ Benchmark completed successfully"
  artifacts:
    paths:
      - benchmark_results/
      - *.json
      - *.csv
    reports:
      junit: benchmark_results/*.xml
    expire_in: 1 week
  only:
    - main
    - develop
    - merge_requests

results:
  stage: results
  image: python:{python_version}-slim
  dependencies:
    - benchmark
  script:
    - echo "📊 Processing benchmark results..."
    - |
      if [ -f "benchmark_results.json" ]; then
        echo "Results found, processing..."
        python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    print(f'Models tested: {{len(data.get(\"models\", []))}}')
    print(f'Total cost: ${{data.get(\"total_cost\", 0.0):.2f}}')
            if 'quality_scores' in data:
                scores = data['quality_scores']
                avg_score = sum(scores.values()) / len(scores)
                print(f'Average quality score: {{avg_score}}')
        "
      else
        echo "No benchmark results found"
      fi
  artifacts:
    paths:
      - benchmark_results/
    expire_in: 1 month
  only:
    - main
    - develop
    - merge_requests
"""
        return pipeline
    
    def generate_advanced_pipeline(self,
                                  pipeline_name: str = "Advanced AI Benchmark",
                                  benchmark_file: str = "benchmark.yaml",
                                  python_version: str = "3.9",
                                  quality_gate: float = 0.8,
                                  cost_threshold: float = 10.0) -> str:
        """Generate advanced GitLab CI pipeline with quality gates and cost monitoring"""
        
        pipeline = f"""# {pipeline_name}
# Advanced GitLab CI pipeline for AI benchmarking with quality gates and cost monitoring

variables:
  CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
  PYTHON_VERSION: "{python_version}"
  QUALITY_GATE: "{quality_gate}"
  COST_THRESHOLD: "{cost_threshold}"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/
    - ~/.clyrdia/

stages:
  - setup
  - benchmark
  - analyze
  - quality-gate
  - cost-check
  - results

before_script:
  - python --version
  - pip install --upgrade pip

setup:
  stage: setup
  image: python:{python_version}-slim
  script:
    - echo "🔧 Setting up advanced environment..."
    - pip install clyrdia-cli
    - pip install -r requirements.txt || echo "No requirements.txt found"
    - clyrdia-cli status
    - echo "💰 Credit balance checked"
  artifacts:
    paths:
      - ~/.clyrdia/
    expire_in: 1 hour

benchmark:
  stage: benchmark
  image: python:{python_version}-slim
  dependencies:
    - setup
  script:
    - echo "🚀 Starting advanced AI benchmark..."
    - clyrdia-cli run --config {benchmark_file} --output-format json --save-results
    - echo "✅ Benchmark completed successfully"
  artifacts:
    paths:
      - benchmark_results/
      - *.json
      - *.csv
      - *.log
    expire_in: 1 week
  only:
    - main
    - develop
    - merge_requests

analyze:
  stage: analyze
  image: python:{python_version}-slim
  dependencies:
    - benchmark
  script:
    - echo "📊 Analyzing benchmark results..."
    - |
      if [ -f "benchmark_results.json" ]; then
        # Extract quality score
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
        
        # Extract cost
        TOTAL_COST=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    cost = data.get('total_cost', 0.0)
    print('cost'.format(cost))
")
        
        echo "QUALITY_SCORE=$QUALITY_SCORE" >> variables.env
        echo "TOTAL_COST=$TOTAL_COST" >> variables.env
        
        echo "Quality Score: $QUALITY_SCORE"
        echo "Total Cost: $$TOTAL_COST"
      else
        echo "QUALITY_SCORE=0.0" >> variables.env
        echo "TOTAL_COST=0.0" >> variables.env
        echo "No benchmark results found"
      fi
  artifacts:
    reports:
      dotenv: variables.env
    paths:
      - variables.env
    expire_in: 1 hour

quality-gate:
  stage: quality-gate
  image: python:{python_version}-slim
  dependencies:
    - analyze
  script:
    - echo "🎯 Checking quality gate..."
    - source variables.env
    - echo "Quality Score: $QUALITY_SCORE"
    - echo "Quality Gate: $QUALITY_GATE"
    - |
      if (( $(echo "$QUALITY_SCORE >= $QUALITY_GATE" | bc -l) )); then
        echo "✅ Quality gate PASSED: $QUALITY_SCORE >= $QUALITY_GATE"
      else
        echo "❌ Quality gate FAILED: $QUALITY_SCORE < $QUALITY_GATE"
        exit 1
      fi
  only:
    - main
    - develop
    - merge_requests

cost-check:
  stage: cost-check
  image: python:{python_version}-slim
  dependencies:
    - analyze
  script:
    - echo "💰 Checking cost threshold..."
    - source variables.env
    - echo "Total Cost: $$TOTAL_COST"
    - echo "Cost Threshold: $$COST_THRESHOLD"
    - |
      if (( $(echo "$TOTAL_COST <= $COST_THRESHOLD" | bc -l) )); then
        echo "✅ Cost threshold PASSED: $$TOTAL_COST <= $$COST_THRESHOLD"
      else
        echo "⚠️ Cost threshold EXCEEDED: $$TOTAL_COST > $$COST_THRESHOLD"
        # Don't fail the pipeline, just warn
      fi
  allow_failure: true
  only:
    - main
    - develop
    - merge_requests

results:
  stage: results
  image: python:{python_version}-slim
  dependencies:
    - quality-gate
    - cost-check
  script:
    - echo "📋 Creating benchmark summary..."
    - source variables.env
    - |
      echo "# 🤖 AI Benchmark Summary" > benchmark_summary.md
      echo "" >> benchmark_summary.md
      echo "## Results" >> benchmark_summary.md
      echo "- **Quality Score:** $QUALITY_SCORE" >> benchmark_summary.md
      echo "- **Total Cost:** $$TOTAL_COST" >> benchmark_summary.md
      echo "- **Quality Gate:** $QUALITY_GATE" >> benchmark_summary.md
      echo "- **Cost Threshold:** $$COST_THRESHOLD" >> benchmark_summary.md
      echo "" >> benchmark_summary.md
      
      if (( $(echo "$QUALITY_SCORE >= $QUALITY_GATE" | bc -l) )); then
        echo "✅ **Quality Gate: PASSED**" >> benchmark_summary.md
      else
        echo "❌ **Quality Gate: FAILED**" >> benchmark_summary.md
      fi
      
      if (( $(echo "$TOTAL_COST <= $COST_THRESHOLD" | bc -l) )); then
        echo "✅ **Cost Threshold: PASSED**" >> benchmark_summary.md
      else
        echo "⚠️ **Cost Threshold: EXCEEDED**" >> benchmark_summary.md
      fi
      
      cat benchmark_summary.md
  artifacts:
    paths:
      - benchmark_summary.md
      - benchmark_results/
    expire_in: 1 month
  only:
    - main
    - develop
    - merge_requests
"""
        return pipeline
    
    def generate_mlops_pipeline(self,
                               pipeline_name: str = "MLOps AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               model_registry: str = "mlflow",
                               deployment_target: str = "kubernetes",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate MLOps-focused GitLab CI pipeline for AI model deployment"""
        
        pipeline = f"""# {pipeline_name}
# MLOps GitLab CI pipeline for AI benchmarking and model deployment

variables:
  CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
  PYTHON_VERSION: "3.9"
  MODEL_REGISTRY: "{model_registry}"
  DEPLOYMENT_TARGET: "{deployment_target}"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/
    - ~/.clyrdia/
    - models/

stages:
  - setup
  - version
  - benchmark
  - quality-gate
  - mlflow-log
  - deploy-staging
  - deploy-production
  - release

before_script:
  - python --version
  - pip install --upgrade pip

setup:
  stage: setup
  image: python:3.9-slim
  script:
    - echo "🔧 Setting up MLOps environment..."
    - pip install clyrdia-cli mlflow kubernetes
    - pip install -r requirements.txt || echo "No requirements.txt found"
    - clyrdia-cli status
  artifacts:
    paths:
      - ~/.clyrdia/
    expire_in: 1 hour

version:
  stage: version
  image: python:3.9-slim
  dependencies:
    - setup
  script:
    - echo "🏷️ Versioning model..."
    - VERSION=$(date +%Y%m%d.%H%M%S)
    - echo "MODEL_VERSION=$VERSION" >> variables.env
    - echo "Model version: $VERSION"
  artifacts:
    reports:
      dotenv: variables.env
    paths:
      - variables.env
    expire_in: 1 hour

benchmark:
  stage: benchmark
  image: python:3.9-slim
  dependencies:
    - version
  script:
    - echo "🚀 Running AI benchmark..."
    - source variables.env
    - echo "Benchmarking model version: $MODEL_VERSION"
    - clyrdia-cli run --config {benchmark_file} --output-format json --save-results
    - echo "✅ Benchmark completed successfully"
  artifacts:
    paths:
      - benchmark_results/
      - *.json
      - *.csv
      - *.log
    expire_in: 1 week
  only:
    - main
    - develop
    - merge_requests

quality-gate:
  stage: quality-gate
  image: python:3.9-slim
  dependencies:
    - benchmark
  script:
    - echo "🎯 Quality gate check..."
    - |
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
        
        echo "QUALITY_SCORE=$QUALITY_SCORE" >> variables.env
        echo "Quality Score: $QUALITY_SCORE"
        
        if (( $(echo "$QUALITY_SCORE >= 0.8" | bc -l) )); then
          echo "✅ Quality gate passed: $QUALITY_SCORE >= 0.8"
        else
          echo "❌ Quality gate failed: $QUALITY_SCORE < 0.8"
          exit 1
        fi
      else
        echo "❌ No benchmark results found"
        exit 1
      fi
  artifacts:
    reports:
      dotenv: variables.env
    paths:
      - variables.env
    expire_in: 1 hour

mlflow-log:
  stage: mlflow-log
  image: python:3.9-slim
  dependencies:
    - quality-gate
  script:
    - echo "📝 Logging to MLflow..."
    - source variables.env
    - |
      if [ "$MODEL_REGISTRY" = "mlflow" ]; then
        echo "Logging model version $MODEL_VERSION to MLflow..."
        mlflow run . --env-manager=local || echo "MLflow logging failed, continuing..."
      else
        echo "Skipping MLflow logging for registry: $MODEL_REGISTRY"
      fi
  only:
    - main
    - develop
  allow_failure: true

deploy-staging:
  stage: deploy-staging
  image: python:3.9-slim
  dependencies:
    - quality-gate
  script:
    - echo "🚀 Deploying to staging..."
    - source variables.env
    - echo "Deploying model version $MODEL_VERSION to staging"
    - |
      if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
        echo "Deploying to Kubernetes staging..."
        # Add your Kubernetes staging deployment logic here
        # kubectl apply -f k8s/staging/
      else
        echo "Deployment target $DEPLOYMENT_TARGET not implemented"
      fi
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop
  when: manual

deploy-production:
  stage: deploy-production
  image: python:3.9-slim
  dependencies:
    - quality-gate
  script:
    - echo "🚀 Deploying to production..."
    - source variables.env
    - echo "Deploying model version $MODEL_VERSION to production"
    - |
      if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
        echo "Deploying to Kubernetes production..."
        # Add your Kubernetes production deployment logic here
        # kubectl apply -f k8s/production/
      else
        echo "Deployment target $DEPLOYMENT_TARGET not implemented"
      fi
  environment:
    name: production
    url: https://example.com
  only:
    - main
  when: manual

release:
  stage: release
  image: python:3.9-slim
  dependencies:
    - deploy-production
  script:
    - echo "🎉 Creating release..."
    - source variables.env
    - echo "Creating release for model version $MODEL_VERSION"
    - |
      # Add your release logic here
      # git tag -a "v$MODEL_VERSION" -m "Release version $MODEL_VERSION"
      # git push origin "v$MODEL_VERSION"
  only:
    - main
  when: manual
"""
        return pipeline
    
    def generate_pipeline_file(self,
                              template_type: str = "basic",
                              **kwargs) -> str:
        """Generate pipeline file based on template type"""
        
        if template_type == "basic":
            return self.generate_basic_pipeline(**kwargs)
        elif template_type == "advanced":
            return self.generate_advanced_pipeline(**kwargs)
        elif template_type == "mlops":
            return self.generate_mlops_pipeline(**kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def save_pipeline(self,
                     template_type: str = "basic",
                     output_path: str = ".gitlab-ci",
                     **kwargs) -> str:
        """Generate and save pipeline file"""
        
        pipeline_content = self.generate_pipeline_file(template_type, **kwargs)
        
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if template_type == "basic":
            filename = ".gitlab-ci.yml"
        elif template_type == "advanced":
            filename = "advanced-gitlab-ci.yml"
        elif template_type == "mlops":
            filename = "mlops-gitlab-ci.yml"
        else:
            filename = f"{template_type}-gitlab-ci.yml"
        
        # Save pipeline file
        pipeline_path = output_dir / filename
        with open(pipeline_path, 'w') as f:
            f.write(pipeline_content)
        
        return str(pipeline_path)
