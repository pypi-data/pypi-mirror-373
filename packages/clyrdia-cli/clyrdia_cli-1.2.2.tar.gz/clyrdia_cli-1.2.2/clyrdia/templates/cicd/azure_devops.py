"""
Azure DevOps template for Clyrdia AI benchmarking.
Provides real, working Azure DevOps pipeline YAML files for automated AI model testing.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AzureDevOpsTemplate:
    """Azure DevOps template generator"""
    
    def generate_basic_pipeline(self,
                               pipeline_name: str = "AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate basic Azure DevOps pipeline for AI benchmarking"""
        
        pipeline = f"""# {pipeline_name}
# Azure DevOps pipeline for automated AI benchmarking with Clyrdia

trigger:
  branches:
    include:
    - main
    - develop
    - feature/*
  paths:
    include:
    - {benchmark_file}
    - requirements.txt
    - '**/*.py'

pool:
  vmImage: 'ubuntu-latest'

variables:
  PYTHON_VERSION: '{python_version}'
  PIP_CACHE_DIR: '$(Pipeline.Workspace)/.pip-cache'

stages:
- stage: Benchmark
  displayName: 'AI Benchmark'
  jobs:
  - job: Benchmark
    displayName: 'Run AI Benchmark'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python $(PYTHON_VERSION)'
      inputs:
        versionSpec: '$(PYTHON_VERSION)'
        addToPath: true
        
    - script: |
        python --version
        pip --version
      displayName: 'Check Python installation'
      
    - script: |
        python -m pip install --upgrade pip
        pip install clyrdia-cli
        pip install -r requirements.txt || echo "No requirements.txt found"
      displayName: 'Install dependencies'
      
    - script: |
        echo "🔧 Setting up environment variables..."
        # Create .env file from Azure DevOps variables
        cat > .env << EOF
        # Clyrdia API key (if you have one)
        CLYRIDIA_API_KEY=$(CLYRIDIA_API_KEY)
        
        # AI Provider API keys
        OPENAI_API_KEY=$(OPENAI_API_KEY)
        ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY)
        EOF
        echo "✅ Environment variables configured"
      displayName: 'Setup environment variables'
      
    - script: |
        echo "💰 Checking Clyrdia credit balance..."
        clyrdia-cli status
      displayName: 'Check Clyrdia status'
      
    - script: |
        echo "🚀 Starting AI benchmark with Clyrdia..."
        clyrdia-cli run --config {benchmark_file} --output-format json
        echo "✅ Benchmark completed successfully"
      displayName: 'Run AI benchmark'
      
    - script: |
        echo "📊 Processing benchmark results..."
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
      displayName: 'Process results'
      
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'benchmark_results/*.xml'
        testRunTitle: 'AI Benchmark Results'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish benchmark results'
      inputs:
        pathToPublish: 'benchmark_results/'
        artifactName: 'benchmark-results'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish JSON results'
      inputs:
        pathToPublish: '*.json'
        artifactName: 'json-results'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish CSV results'
      inputs:
        pathToPublish: '*.csv'
        artifactName: 'csv-results'
      condition: succeededOrFailed()
"""
        return pipeline
    
    def generate_advanced_pipeline(self,
                                  pipeline_name: str = "Advanced AI Benchmark",
                                  benchmark_file: str = "benchmark.yaml",
                                  python_version: str = "3.9",
                                  quality_gate: float = 0.8,
                                  cost_threshold: float = 10.0) -> str:
        """Generate advanced Azure DevOps pipeline with quality gates and cost monitoring"""
        
        pipeline = f"""# {pipeline_name}
# Advanced Azure DevOps pipeline for AI benchmarking with quality gates and cost monitoring

trigger:
  branches:
    include:
    - main
    - develop
    - feature/*
  paths:
    include:
    - {benchmark_file}
    - requirements.txt
    - '**/*.py'

pr:
  branches:
    include:
    - main
    - develop

schedules:
- cron: "0 2 * * 1"  # Weekly on Monday at 2 AM
  displayName: 'Weekly benchmark'
  branches:
    include:
    - main
  always: true

pool:
  vmImage: 'ubuntu-latest'

variables:
  CLYRIDIA_API_KEY: $(CLYRIDIA_API_KEY)
  PYTHON_VERSION: '{python_version}'
  QUALITY_GATE: '{quality_gate}'
  COST_THRESHOLD: '{cost_threshold}'
  PIP_CACHE_DIR: '$(Pipeline.Workspace)/.pip-cache'

stages:
- stage: Setup
  displayName: 'Setup Environment'
  jobs:
  - job: Setup
    displayName: 'Setup and Install'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python $(PYTHON_VERSION)'
      inputs:
        versionSpec: '$(PYTHON_VERSION)'
        addToPath: true
        
    - script: |
        python --version
        pip --version
      displayName: 'Check Python installation'
      
    - script: |
        python -m pip install --upgrade pip
        pip install clyrdia-cli
        pip install -r requirements.txt || echo "No requirements.txt found"
      displayName: 'Install dependencies'
      
    - script: |
        echo "💰 Checking Clyrdia credit balance..."
        clyrdia-cli status
        echo "✅ Setup completed successfully"
      displayName: 'Check Clyrdia status'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish setup artifacts'
      inputs:
        pathToPublish: '~/.clyrdia/'
        artifactName: 'clyrdia-config'
      condition: succeededOrFailed()

- stage: Benchmark
  displayName: 'AI Benchmark'
  dependsOn: Setup
  jobs:
  - job: Benchmark
    displayName: 'Run AI Benchmark'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python $(PYTHON_VERSION)'
      inputs:
        versionSpec: '$(PYTHON_VERSION)'
        addToPath: true
        
    - download: current
      artifact: clyrdia-config
      displayName: 'Download Clyrdia config'
      
    - script: |
        echo "🚀 Starting advanced AI benchmark..."
        clyrdia-cli run --config {benchmark_file} --output-format json --save-results
        echo "✅ Benchmark completed successfully"
      displayName: 'Run AI benchmark'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish benchmark results'
      inputs:
        pathToPublish: 'benchmark_results/'
        artifactName: 'benchmark-results'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish JSON results'
      inputs:
        pathToPublish: '*.json'
        artifactName: 'json-results'
      condition: succeededOrFailed()

- stage: Analyze
  displayName: 'Analyze Results'
  dependsOn: Benchmark
  jobs:
  - job: Analyze
    displayName: 'Analyze Benchmark Results'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python $(PYTHON_VERSION)'
      inputs:
        versionSpec: '$(PYTHON_VERSION)'
        addToPath: true
        
    - download: current
      artifact: benchmark-results
      displayName: 'Download benchmark results'
      
    - script: |
        echo "📊 Analyzing benchmark results..."
        
        if [ -f "benchmark_results.json" ]; then
          # Extract quality score
          QUALITY_SCORE=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    scores = data.get("quality_scores", {{}})
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        print('avg_score'.format(avg_score))
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
          
          echo "QUALITY_SCORE=$QUALITY_SCORE" > variables.env
          echo "TOTAL_COST=$TOTAL_COST" >> variables.env
          
          echo "Quality Score: $QUALITY_SCORE"
          echo "Total Cost: $$TOTAL_COST"
        else
          echo "QUALITY_SCORE=0.0" > variables.env
          echo "TOTAL_COST=0.0" >> variables.env
          echo "No benchmark results found"
        fi
      displayName: 'Analyze results'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish variables'
      inputs:
        pathToPublish: 'variables.env'
        artifactName: 'variables'
      condition: succeededOrFailed()

- stage: QualityGate
  displayName: 'Quality Gate'
  dependsOn: Analyze
  jobs:
  - job: QualityGate
    displayName: 'Check Quality Gate'
    steps:
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "🎯 Checking quality gate..."
        source variables.env
        echo "Quality Score: $QUALITY_SCORE"
        echo "Quality Gate: $QUALITY_GATE"
        
        if (( $(echo "$QUALITY_SCORE >= $QUALITY_GATE" | bc -l) )); then
          echo "✅ Quality gate PASSED: $QUALITY_SCORE >= $QUALITY_GATE"
        else
          echo "❌ Quality gate FAILED: $QUALITY_SCORE < $QUALITY_GATE"
          exit 1
        fi
      displayName: 'Quality gate check'

- stage: CostCheck
  displayName: 'Cost Check'
  dependsOn: Analyze
  jobs:
  - job: CostCheck
    displayName: 'Check Cost Threshold'
    steps:
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "💰 Checking cost threshold..."
        source variables.env
        echo "Total Cost: $$TOTAL_COST"
        echo "Cost Threshold: $$COST_THRESHOLD"
        
        if (( $(echo "$TOTAL_COST <= $COST_THRESHOLD" | bc -l) )); then
          echo "✅ Cost threshold PASSED: $$TOTAL_COST <= $$COST_THRESHOLD"
        else
          echo "⚠️ Cost threshold EXCEEDED: $$TOTAL_COST > $$COST_THRESHOLD"
          # Don't fail the pipeline, just warn
        fi
      displayName: 'Cost threshold check'
      continueOnError: true

- stage: Results
  displayName: 'Results Summary'
  dependsOn: 
  - QualityGate
  - CostCheck
  jobs:
  - job: Results
    displayName: 'Create Results Summary'
    steps:
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "📋 Creating benchmark summary..."
        source variables.env
        
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
      displayName: 'Create summary'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish summary'
      inputs:
        pathToPublish: 'benchmark_summary.md'
        artifactName: 'summary'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish final results'
      inputs:
        pathToPublish: 'benchmark_results/'
        artifactName: 'final-results'
      condition: succeededOrFailed()
      
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'benchmark_results/*.xml'
        testRunTitle: 'AI Benchmark Results'
      condition: succeededOrFailed()
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
        """Generate MLOps-focused Azure DevOps pipeline for AI model deployment"""
        
        pipeline = f"""# {pipeline_name}
# MLOps Azure DevOps pipeline for AI benchmarking and model deployment

trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - {benchmark_file}
    - requirements.txt
    - '**/*.py'

pr:
  branches:
    include:
    - main
    - develop

resources:
  repositories:
    - repository: self
      trigger:
        branches:
          include:
          - main
          - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  CLYRIDIA_API_KEY: $(CLYRIDIA_API_KEY)
  MODEL_REGISTRY: '{model_registry}'
  DEPLOYMENT_TARGET: '{deployment_target}'
  PIP_CACHE_DIR: '$(Pipeline.Workspace)/.pip-cache'

stages:
- stage: Setup
  displayName: 'Setup MLOps Environment'
  jobs:
  - job: Setup
    displayName: 'Setup and Install Dependencies'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - script: |
        python --version
        pip --version
      displayName: 'Check Python installation'
      
    - script: |
        echo "🔧 Installing MLOps dependencies..."
        python -m pip install --upgrade pip
        pip install clyrdia-cli mlflow kubernetes
        pip install -r requirements.txt || echo "No requirements.txt found"
        echo "✅ Dependencies installed"
      displayName: 'Install MLOps dependencies'
      
    - script: |
        echo "💰 Checking Clyrdia credit balance..."
        clyrdia-cli status
      displayName: 'Check Clyrdia status'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish setup artifacts'
      inputs:
        pathToPublish: '~/.clyrdia/'
        artifactName: 'clyrdia-config'
      condition: succeededOrFailed()

- stage: Version
  displayName: 'Model Versioning'
  dependsOn: Setup
  jobs:
  - job: Version
    displayName: 'Version Model'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - script: |
        echo "🏷️ Versioning model..."
        VERSION=$(date +%Y%m%d.%H%M%S)
        echo "MODEL_VERSION=$VERSION" > variables.env
        echo "Model version: $VERSION"
      displayName: 'Create model version'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish variables'
      inputs:
        pathToPublish: 'variables.env'
        artifactName: 'variables'
      condition: succeededOrFailed()

- stage: Benchmark
  displayName: 'AI Benchmark'
  dependsOn: Version
  jobs:
  - job: Benchmark
    displayName: 'Run AI Benchmark'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "🚀 Running AI benchmark..."
        source variables.env
        echo "Benchmarking model version: $MODEL_VERSION"
        clyrdia-cli run --config {benchmark_file} --output-format json --save-results
        echo "✅ Benchmark completed successfully"
      displayName: 'Run AI benchmark'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish benchmark results'
      inputs:
        pathToPublish: 'benchmark_results/'
        artifactName: 'benchmark-results'
      condition: succeededOrFailed()
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish JSON results'
      inputs:
        pathToPublish: '*.json'
        artifactName: 'json-results'
      condition: succeededOrFailed()

- stage: QualityGate
  displayName: 'Quality Gate'
  dependsOn: Benchmark
  jobs:
  - job: QualityGate
    displayName: 'Check Quality Gate'
    steps:
    - download: current
      artifact: benchmark-results
      displayName: 'Download benchmark results'
      
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - script: |
        echo "🎯 Quality gate check..."
        if [ -f "benchmark_results.json" ]; then
          QUALITY_SCORE=$(python -c "
import json
with open('benchmark_results.json') as f:
    data = json.load(f)
    scores = data.get("quality_scores", {{}})
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        print('avg_score'.format(avg_score))
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
      displayName: 'Quality gate check'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish updated variables'
      inputs:
        pathToPublish: 'variables.env'
        artifactName: 'updated-variables'
      condition: succeededOrFailed()

- stage: MLflowLog
  displayName: 'MLflow Logging'
  dependsOn: QualityGate
  jobs:
  - job: MLflowLog
    displayName: 'Log to MLflow'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "📝 Logging to MLflow..."
        source variables.env
        if [ "$MODEL_REGISTRY" = "mlflow" ]; then
          echo "Logging model version $MODEL_VERSION to MLflow..."
          mlflow run . --env-manager=local || echo "MLflow logging failed, continuing..."
        else
          echo "Skipping MLflow logging for registry: $MODEL_REGISTRY"
        fi
      displayName: 'MLflow logging'
      condition: eq(variables['MODEL_REGISTRY'], 'mlflow')

- stage: DeployStaging
  displayName: 'Deploy to Staging'
  dependsOn: QualityGate
  jobs:
  - job: DeployStaging
    displayName: 'Deploy to Staging Environment'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "🚀 Deploying to staging..."
        source variables.env
        echo "Deploying model version $MODEL_VERSION to staging"
        
        if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
          echo "Deploying to Kubernetes staging..."
          # Add your Kubernetes staging deployment logic here
          # kubectl apply -f k8s/staging/
        else
          echo "Deployment target $DEPLOYMENT_TARGET not implemented"
        fi
      displayName: 'Deploy to staging'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish staging deployment logs'
      inputs:
        pathToPublish: 'deployment-logs/'
        artifactName: 'staging-deployment'
      condition: succeededOrFailed()

- stage: DeployProduction
  displayName: 'Deploy to Production'
  dependsOn: QualityGate
  jobs:
  - job: DeployProduction
    displayName: 'Deploy to Production Environment'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "🚀 Deploying to production..."
        source variables.env
        echo "Deploying model version $MODEL_VERSION to production"
        
        if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
          echo "Deploying to Kubernetes production..."
          # Add your Kubernetes production deployment logic here
          # kubectl apply -f k8s/production/
        else
          echo "Deployment target $DEPLOYMENT_TARGET not implemented"
        fi
      displayName: 'Deploy to production'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish production deployment logs'
      inputs:
        pathToPublish: 'deployment-logs/'
        artifactName: 'production-deployment'
      condition: succeededOrFailed()

- stage: Release
  displayName: 'Create Release'
  dependsOn: DeployProduction
  jobs:
  - job: Release
    displayName: 'Create Model Release'
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python 3.9'
      inputs:
        versionSpec: '3.9'
        addToPath: true
        
    - download: current
      artifact: variables
      displayName: 'Download variables'
      
    - script: |
        echo "🎉 Creating release..."
        source variables.env
        echo "Creating release for model version $MODEL_VERSION"
        
        # Add your release logic here
        # git tag -a "v$MODEL_VERSION" -m "Release version $MODEL_VERSION"
        # git push origin "v$MODEL_VERSION"
      displayName: 'Create release'
      
    - task: PublishBuildArtifacts@1
      displayName: 'Publish release info'
      inputs:
        pathToPublish: 'release-info/'
        artifactName: 'release'
      condition: succeededOrFailed()
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
                     output_path: str = "azure-pipelines",
                     **kwargs) -> str:
        """Generate and save pipeline file"""
        
        pipeline_content = self.generate_pipeline_file(template_type, **kwargs)
        
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if template_type == "basic":
            filename = "azure-pipelines.yml"
        elif template_type == "advanced":
            filename = "azure-pipelines.advanced.yml"
        elif template_type == "mlops":
            filename = "azure-pipelines.mlops.yml"
        else:
            filename = f"azure-pipelines.{template_type}.yml"
        
        # Save pipeline file
        pipeline_path = output_dir / filename
        with open(pipeline_path, 'w') as f:
            f.write(pipeline_content)
        
        return str(pipeline_path)
