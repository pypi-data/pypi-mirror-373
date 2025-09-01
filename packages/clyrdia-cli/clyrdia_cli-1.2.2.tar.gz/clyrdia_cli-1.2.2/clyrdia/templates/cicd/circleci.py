"""
CircleCI template for Clyrdia AI benchmarking.
Provides real, working CircleCI configuration files for automated AI model testing.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CircleCITemplate:
    """CircleCI template generator"""
    
    def generate_basic_config(self,
                             config_name: str = "AI Benchmark",
                             benchmark_file: str = "benchmark.yaml",
                             python_version: str = "3.9",
                             quality_gate: float = 0.8,
                             cost_threshold: float = 10.0) -> str:
        """Generate basic CircleCI configuration for AI benchmarking"""
        
        config = f"""# {config_name}
# CircleCI configuration for automated AI benchmarking with Clyrdia

version: 2.1

orbs:
  python: circleci/python@2.1

jobs:
  benchmark:
    docker:
      - image: cimg/python:{python_version}
    environment:
      PYTHON_VERSION: "{python_version}"
    steps:
      - checkout
      
      - python/install-packages:
          pkg-manager: pip
          app-dir: ./
          
      - run:
          name: Install Clyrdia CLI
          command: |
            echo "🔧 Installing Clyrdia CLI..."
            pip install clyrdia-cli
            
      - run:
          name: Setup environment variables
          command: |
            echo "🔧 Setting up environment variables..."
            # Create .env file from CircleCI environment variables
            cat > .env << EOF
            # Clyrdia API key (if you have one)
            CLYRIDIA_API_KEY=$CLYRIDIA_API_KEY
            
            # AI Provider API keys
            OPENAI_API_KEY=$OPENAI_API_KEY
            ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
            EOF
            echo "✅ Environment variables configured"
            
      - run:
          name: Check Clyrdia status
          command: |
            echo "💰 Checking credit balance..."
            clyrdia-cli status
            
      - run:
          name: Run AI benchmark
          command: |
            echo "🚀 Starting AI benchmark with Clyrdia..."
            clyrdia-cli run --config {benchmark_file} --output-format json
            echo "✅ Benchmark completed successfully"
            
      - run:
          name: Process results
          command: |
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
            
      - store_artifacts:
          path: benchmark_results/
          destination: benchmark-results
          
      - store_artifacts:
          path: *.json
          destination: json-results
          
      - store_artifacts:
          path: *.csv
          destination: csv-results

workflows:
  version: 2
  benchmark:
    jobs:
      - benchmark:
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
"""
        return config
    
    def generate_advanced_config(self,
                                config_name: str = "Advanced AI Benchmark",
                                benchmark_file: str = "benchmark.yaml",
                                python_version: str = "3.9",
                                quality_gate: float = 0.8,
                                cost_threshold: float = 10.0) -> str:
        """Generate advanced CircleCI configuration with quality gates and cost monitoring"""
        
        config = f"""# {config_name}
# Advanced CircleCI configuration for AI benchmarking with quality gates and cost monitoring

version: 2.1

orbs:
  python: circleci/python@2.1

jobs:
  setup:
    docker:
      - image: cimg/python:{python_version}
    environment:
      CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
      PYTHON_VERSION: "{python_version}"
    steps:
      - checkout
      
      - python/install-packages:
          pkg-manager: pip
          app-dir: ./
          
      - run:
          name: Install Clyrdia CLI
          command: |
            echo "🔧 Installing Clyrdia CLI..."
            pip install clyrdia-cli
            
      - run:
          name: Check Clyrdia status
          command: |
            echo "💰 Checking credit balance..."
            clyrdia-cli status
            
      - persist_to_workspace:
          root: .
          paths:
            - .venv/
            - ~/.clyrdia/
            
  benchmark:
    docker:
      - image: cimg/python:{python_version}
    environment:
      CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
      PYTHON_VERSION: "{python_version}"
      QUALITY_GATE: "{quality_gate}"
      COST_THRESHOLD: "{cost_threshold}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Run AI benchmark
          command: |
            echo "🚀 Starting advanced AI benchmark..."
            clyrdia-cli run --config {benchmark_file} --output-format json --save-results
            echo "✅ Benchmark completed successfully"
            
      - store_artifacts:
          path: benchmark_results/
          destination: benchmark-results
          
      - store_artifacts:
          path: *.json
          destination: json-results
          
      - store_artifacts:
          path: *.csv
          destination: csv-results
          
  analyze:
    docker:
      - image: cimg/python:{python_version}
    environment:
      QUALITY_GATE: "{quality_gate}"
      COST_THRESHOLD: "{cost_threshold}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Analyze benchmark results
          command: |
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
            
      - store_artifacts:
          path: variables.env
          destination: variables
          
  quality-gate:
    docker:
      - image: cimg/python:{python_version}
    environment:
      QUALITY_GATE: "{quality_gate}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Check quality gate
          command: |
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
            
  cost-check:
    docker:
      - image: cimg/python:{python_version}
    environment:
      COST_THRESHOLD: "{cost_threshold}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Check cost threshold
          command: |
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
            
  results:
    docker:
      - image: cimg/python:{python_version}
    environment:
      QUALITY_GATE: "{quality_gate}"
      COST_THRESHOLD: "{cost_threshold}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Create benchmark summary
          command: |
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
            
      - store_artifacts:
          path: benchmark_summary.md
          destination: summary
          
      - store_artifacts:
          path: benchmark_results/
          destination: final-results

workflows:
  version: 2
  advanced-benchmark:
    jobs:
      - setup:
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
                
      - benchmark:
          requires:
            - setup
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
                
      - analyze:
          requires:
            - benchmark
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
                
      - quality-gate:
          requires:
            - analyze
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
                
      - cost-check:
          requires:
            - analyze
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
                
      - results:
          requires:
            - quality-gate
            - cost-check
          filters:
            branches:
              only:
                - main
                - develop
                - /^feature\/.*/
"""
        return config
    
    def generate_mlops_config(self,
                             config_name: str = "MLOps AI Benchmark",
                             benchmark_file: str = "benchmark.yaml",
                             model_registry: str = "mlflow",
                             deployment_target: str = "kubernetes",
                             python_version: str = "3.9",
                             quality_gate: float = 0.8,
                             cost_threshold: float = 10.0) -> str:
        """Generate MLOps-focused CircleCI configuration for AI model deployment"""
        
        config = f"""# {config_name}
# MLOps CircleCI configuration for AI benchmarking and model deployment

version: 2.1

orbs:
  python: circleci/python@2.1
  kubernetes: circleci/kubernetes@1.3

jobs:
  setup:
    docker:
      - image: cimg/python:3.9
    environment:
      CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
      MODEL_REGISTRY: "{model_registry}"
      DEPLOYMENT_TARGET: "{deployment_target}"
    steps:
      - checkout
      
      - python/install-packages:
          pkg-manager: pip
          app-dir: ./
          
      - run:
          name: Install MLOps dependencies
          command: |
            echo "🔧 Installing MLOps dependencies..."
            pip install clyrdia-cli mlflow kubernetes
            echo "✅ Dependencies installed"
            
      - run:
          name: Check Clyrdia status
          command: |
            echo "💰 Checking credit balance..."
            clyrdia-cli status
            
      - persist_to_workspace:
          root: .
          paths:
            - .venv/
            - ~/.clyrdia/
            
  version:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Version model
          command: |
            echo "🏷️ Versioning model..."
            VERSION=$(date +%Y%m%d.%H%M%S)
            echo "MODEL_VERSION=$VERSION" > variables.env
            echo "Model version: $VERSION"
            
      - store_artifacts:
          path: variables.env
          destination: variables
          
  benchmark:
    docker:
      - image: cimg/python:3.9
    environment:
      CLYRIDIA_API_KEY: $CLYRIDIA_API_KEY
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Run AI benchmark
          command: |
            echo "🚀 Running AI benchmark..."
            source variables.env
            echo "Benchmarking model version: $MODEL_VERSION"
            clyrdia-cli run --config {benchmark_file} --output-format json --save-results
            echo "✅ Benchmark completed successfully"
            
      - store_artifacts:
          path: benchmark_results/
          destination: benchmark-results
          
      - store_artifacts:
          path: *.json
          destination: json-results
          
  quality-gate:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Check quality gate
          command: |
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
            
      - store_artifacts:
          path: variables.env
          destination: updated-variables
          
  mlflow-log:
    docker:
      - image: cimg/python:3.9
    environment:
      MODEL_REGISTRY: "{model_registry}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Log to MLflow
          command: |
            echo "📝 Logging to MLflow..."
            source variables.env
            if [ "$MODEL_REGISTRY" = "mlflow" ]; then
              echo "Logging model version $MODEL_VERSION to MLflow..."
              mlflow run . --env-manager=local || echo "MLflow logging failed, continuing..."
            else
              echo "Skipping MLflow logging for registry: $MODEL_REGISTRY"
            fi
            
  deploy-staging:
    docker:
      - image: cimg/python:3.9
    environment:
      DEPLOYMENT_TARGET: "{deployment_target}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Deploy to staging
          command: |
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
            
      - store_artifacts:
          path: deployment-logs/
          destination: staging-deployment
          
  deploy-production:
    docker:
      - image: cimg/python:3.9
    environment:
      DEPLOYMENT_TARGET: "{deployment_target}"
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Deploy to production
          command: |
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
            
      - store_workspace:
          root: .
          paths:
            - deployment-logs/
            
      - store_artifacts:
          path: deployment-logs/
          destination: production-deployment
          
  release:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      
      - attach_workspace:
          at: .
          
      - run:
          name: Activate virtual environment
          command: |
            source .venv/bin/activate
            echo "Virtual environment activated"
            
      - run:
          name: Create release
          command: |
            echo "🎉 Creating release..."
            source variables.env
            echo "Creating release for model version $MODEL_VERSION"
            
            # Add your release logic here
            # git tag -a "v$MODEL_VERSION" -m "Release version $MODEL_VERSION"
            # git push origin "v$MODEL_VERSION"
            
      - store_artifacts:
          path: release-info/
          destination: release

workflows:
  version: 2
  mlops-benchmark:
    jobs:
      - setup:
          filters:
            branches:
              only:
                - main
                - develop
                
      - version:
          requires:
            - setup
          filters:
            branches:
              only:
                - main
                - develop
                
      - benchmark:
          requires:
            - version
          filters:
            branches:
              only:
                - main
                - develop
                
      - quality-gate:
          requires:
            - benchmark
          filters:
            branches:
              only:
                - main
                - develop
                
      - mlflow-log:
          requires:
            - quality-gate
          filters:
            branches:
              only:
                - main
                - develop
                
      - deploy-staging:
          requires:
            - quality-gate
          filters:
            branches:
              only:
                - develop
                
      - deploy-production:
          requires:
            - quality-gate
          filters:
            branches:
              only:
                - main
                
      - release:
          requires:
            - deploy-production
          filters:
            branches:
              only:
                - main
"""
        return config
    
    def generate_config_file(self,
                            template_type: str = "basic",
                            **kwargs) -> str:
        """Generate config file based on template type"""
        
        if template_type == "basic":
            return self.generate_basic_config(**kwargs)
        elif template_type == "advanced":
            return self.generate_advanced_config(**kwargs)
        elif template_type == "mlops":
            return self.generate_mlops_config(**kwargs)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
    
    def save_config(self,
                   template_type: str = "basic",
                   output_path: str = ".circleci",
                   **kwargs) -> str:
        """Generate and save config file"""
        
        config_content = self.generate_config_file(template_type, **kwargs)
        
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if template_type == "basic":
            filename = "config.yml"
        elif template_type == "advanced":
            filename = "config.advanced.yml"
        elif template_type == "mlops":
            filename = "config.mlops.yml"
        else:
            filename = f"config.{template_type}.yml"
        
        # Save config file
        config_path = output_dir / filename
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return str(config_path)
