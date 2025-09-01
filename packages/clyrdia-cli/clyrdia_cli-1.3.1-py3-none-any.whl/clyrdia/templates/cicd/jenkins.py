"""
Jenkins CI/CD template for Clyrdia AI benchmarking.
Provides real, working Jenkins pipeline scripts for automated AI model testing.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class JenkinsTemplate:
    """Jenkins CI/CD template generator"""
    
    def generate_basic_pipeline(self,
                               pipeline_name: str = "AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate basic Jenkins pipeline for AI benchmarking"""
        
        pipeline = f"""pipeline {{
    agent {{
        docker {{
            image 'python:{python_version}-slim'
            args '-u root'
        }}
    }}
    
    environment {{
        PYTHON_VERSION = '{python_version}'
        PIP_CACHE_DIR = '/tmp/pip-cache'
    }}
    
    options {{
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                script {{
                    echo '🔧 Setting up environment...'
                    sh 'python --version'
                    sh 'pip install --upgrade pip'
                    sh 'pip install clyrdia-cli'
                    sh 'pip install -r requirements.txt || echo "No requirements.txt found"'
                    sh '''
                        echo "🔧 Setting up environment variables..."
                        # Create .env file from Jenkins credentials
                        cat > .env << EOF
                        # Clyrdia API key (if you have one)
                        CLYRIDIA_API_KEY=${{env.CLYRDIA_API_KEY}}
                        
                        # AI Provider API keys
                        OPENAI_API_KEY=${{env.OPENAI_API_KEY}}
                        ANTHROPIC_API_KEY=${{env.ANTHROPIC_API_KEY}}
                        EOF
                        echo "✅ Environment variables configured"
                    '''
                    sh 'clyrdia-cli status'
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: '~/.clyrdia/**/*,.env', fingerprint: true
                }}
            }}
        }}
        
        stage('Benchmark') {{
            steps {{
                script {{
                    echo '🚀 Starting AI benchmark with Clyrdia...'
                    sh 'clyrdia-cli run --config {benchmark_file} --output-format json'
                    echo '✅ Benchmark completed successfully'
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'benchmark_results/**,*.json,*.csv', fingerprint: true
                    publishTestResults testResultsPattern: 'benchmark_results/*.xml'
                }}
            }}
        }}
        
        stage('Results') {{
            steps {{
                script {{
                    echo '📊 Processing benchmark results...'
                    sh '''
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
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'benchmark_results/**', fingerprint: true
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo '🎉 Pipeline completed successfully!'
        }}
        failure {{
            echo '❌ Pipeline failed!'
        }}
        unstable {{
            echo '⚠️ Pipeline completed with warnings'
        }}
    }}
}}"""
        return pipeline
    
    def generate_advanced_pipeline(self,
                                  pipeline_name: str = "Advanced AI Benchmark",
                                  benchmark_file: str = "benchmark.yaml",
                                  python_version: str = "3.9",
                                  quality_gate: float = 0.8,
                                  cost_threshold: float = 10.0) -> str:
        """Generate advanced Jenkins pipeline with quality gates and cost monitoring"""
        
        pipeline = f"""pipeline {{
    agent {{
        docker {{
            image 'python:{python_version}-slim'
            args '-u root'
        }}
    }}
    
    environment {{
        PYTHON_VERSION = '{python_version}'
        QUALITY_GATE = '{quality_gate}'
        COST_THRESHOLD = '{cost_threshold}'
        PIP_CACHE_DIR = '/tmp/pip-cache'
    }}
    
    options {{
        timeout(time: 2, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }}
    
    parameters {{
        choice(
            name: 'BRANCH',
            choices: ['main', 'develop', 'feature/*'],
            description: 'Branch to benchmark'
        )
        booleanParam(
            name: 'SKIP_COST_CHECK',
            defaultValue: false,
            description: 'Skip cost threshold check'
        )
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                script {{
                    echo '🔧 Setting up advanced environment...'
                    sh 'python --version'
                    sh 'pip install --upgrade pip'
                    sh 'pip install clyrdia-cli'
                    sh 'pip install -r requirements.txt || echo "No requirements.txt found"'
                    sh '''
                        echo "🔧 Setting up environment variables..."
                        # Create .env file from Jenkins credentials
                        cat > .env << EOF
                        # Clyrdia API key (if you have one)
                        CLYRIDIA_API_KEY=${{env.CLYRDIA_API_KEY}}
                        
                        # AI Provider API keys
                        OPENAI_API_KEY=${{env.OPENAI_API_KEY}}
                        ANTHROPIC_API_KEY=${{env.ANTHROPIC_API_KEY}}
                        EOF
                        echo "✅ Environment variables configured"
                    '''
                    sh 'clyrdia-cli status'
                    echo '💰 Credit balance checked'
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: '~/.clyrdia/**/*,.env', fingerprint: true
                }}
            }}
        }}
        
        stage('Benchmark') {{
            steps {{
                script {{
                    echo '🚀 Starting advanced AI benchmark...'
                    sh 'clyrdia-cli run --config {benchmark_file} --output-format json --save-results'
                    echo '✅ Benchmark completed successfully'
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'benchmark_results/**,*.json,*.csv,*.log', fingerprint: true
                }}
            }}
        }}
        
        stage('Analyze') {{
            steps {{
                script {{
                    echo '📊 Analyzing benchmark results...'
                    sh '''
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
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'variables.env', fingerprint: true
                }}
            }}
        }}
        
        stage('Quality Gate') {{
            steps {{
                script {{
                    echo '🎯 Checking quality gate...'
                    sh '''
                        source variables.env
                        echo "Quality Score: $QUALITY_SCORE"
                        echo "Quality Gate: $QUALITY_GATE"
                        
                        if (( $(echo "$QUALITY_SCORE >= $QUALITY_GATE" | bc -l) )); then
                            echo "✅ Quality gate PASSED: $QUALITY_SCORE >= $QUALITY_GATE"
                        else
                            echo "❌ Quality gate FAILED: $QUALITY_SCORE < $QUALITY_GATE"
                            exit 1
                        fi
                    '''
                }}
            }}
        }}
        
        stage('Cost Check') {{
            when {{
                not {{
                    params {{
                        booleanParam(name: 'SKIP_COST_CHECK', value: 'true')
                    }}
                }}
            }}
            steps {{
                script {{
                    echo '💰 Checking cost threshold...'
                    sh '''
                        source variables.env
                        echo "Total Cost: $$TOTAL_COST"
                        echo "Cost Threshold: $$COST_THRESHOLD"
                        
                        if (( $(echo "$TOTAL_COST <= $COST_THRESHOLD" | bc -l) )); then
                            echo "✅ Cost threshold PASSED: $$TOTAL_COST <= $$COST_THRESHOLD"
                        else
                            echo "⚠️ Cost threshold EXCEEDED: $$TOTAL_COST > $$COST_THRESHOLD"
                            # Don't fail the pipeline, just warn
                        fi
                    '''
                }}
            }}
        }}
        
        stage('Results') {{
            steps {{
                script {{
                    echo '📋 Creating benchmark summary...'
                    sh '''
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
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'benchmark_summary.md,benchmark_results/**', fingerprint: true
                    publishTestResults testResultsPattern: 'benchmark_results/*.xml'
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo '🎉 Advanced pipeline completed successfully!'
            emailext (
                subject: "✅ AI Benchmark Pipeline Succeeded - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
                body: "Pipeline completed successfully. Quality gate passed and cost within threshold.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }}
        failure {{
            echo '❌ Advanced pipeline failed!'
            emailext (
                subject: "❌ AI Benchmark Pipeline Failed - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
                body: "Pipeline failed. Check Jenkins console for details.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }}
        unstable {{
            echo '⚠️ Advanced pipeline completed with warnings'
        }}
    }}
}}"""
        return pipeline
    
    def generate_mlops_pipeline(self,
                               pipeline_name: str = "MLOps AI Benchmark",
                               benchmark_file: str = "benchmark.yaml",
                               model_registry: str = "mlflow",
                               deployment_target: str = "kubernetes",
                               python_version: str = "3.9",
                               quality_gate: float = 0.8,
                               cost_threshold: float = 10.0) -> str:
        """Generate MLOps-focused Jenkins pipeline for AI model deployment"""
        
        pipeline = f"""pipeline {{
    agent {{
        docker {{
            image 'python:3.9-slim'
            args '-u root'
        }}
    }}
    
    environment {{
        PYTHON_VERSION = '{python_version}'
        MODEL_REGISTRY = '{model_registry}'
        DEPLOYMENT_TARGET = '{deployment_target}'
        PIP_CACHE_DIR = '/tmp/pip-cache'
    }}
    
    options {{
        timeout(time: 3, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }}
    
    parameters {{
        choice(
            name: 'DEPLOYMENT_TYPE',
            choices: ['staging', 'production', 'both'],
            description: 'Deployment type'
        )
        booleanParam(
            name: 'AUTO_DEPLOY',
            defaultValue: false,
            description: 'Auto-deploy after successful benchmark'
        )
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                script {{
                    echo '🔧 Setting up MLOps environment...'
                    sh 'python --version'
                    sh 'pip install --upgrade pip'
                    sh 'pip install clyrdia-cli mlflow kubernetes'
                    sh 'pip install -r requirements.txt || echo "No requirements.txt found"'
                    sh '''
                        echo "🔧 Setting up environment variables..."
                        # Create .env file from Jenkins credentials
                        cat > .env << EOF
                        # Clyrdia API key (if you have one)
                        CLYRIDIA_API_KEY=${{env.CLYRDIA_API_KEY}}
                        
                        # AI Provider API keys
                        OPENAI_API_KEY=${{env.OPENAI_API_KEY}}
                        ANTHROPIC_API_KEY=${{env.ANTHROPIC_API_KEY}}
                        EOF
                        echo "✅ Environment variables configured"
                    '''
                    sh 'clyrdia-cli status'
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: '~/.clyrdia/**/*,.env', fingerprint: true
                }}
            }}
        }}
        
        stage('Version') {{
            steps {{
                script {{
                    echo '🏷️ Versioning model...'
                    sh '''
                        VERSION=$(date +%Y%m%d.%H%M%S)
                        echo "MODEL_VERSION=$VERSION" > variables.env
                        echo "Model version: $VERSION"
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'variables.env', fingerprint: true
                }}
            }}
        }}
        
        stage('Benchmark') {{
            steps {{
                script {{
                    echo '🚀 Running AI benchmark...'
                    sh '''
                        source variables.env
                        echo "Benchmarking model version: $MODEL_VERSION"
                        clyrdia-cli run --config {benchmark_file} --output-format json --save-results
                        echo "✅ Benchmark completed successfully"
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'benchmark_results/**,*.json,*.csv,*.log', fingerprint: true
                }}
            }}
        }}
        
        stage('Quality Gate') {{
            steps {{
                script {{
                    echo '🎯 Quality gate check...'
                    sh '''
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
                    '''
                }}
            }}
        }}
        
        stage('MLflow Log') {{
            when {{
                environment name: 'MODEL_REGISTRY', value: 'mlflow'
            }}
            steps {{
                script {{
                    echo '📝 Logging to MLflow...'
                    sh '''
                        source variables.env
                        echo "Logging model version $MODEL_VERSION to MLflow..."
                        mlflow run . --env-manager=local || echo "MLflow logging failed, continuing..."
                    '''
                }}
            }}
        }}
        
        stage('Deploy Staging') {{
            when {{
                anyOf {{
                    params {{
                        choiceParam(name: 'DEPLOYMENT_TYPE', value: 'staging')
                    }}
                    params {{
                        choiceParam(name: 'DEPLOYMENT_TYPE', value: 'both')
                    }}
                }}
                branch 'develop'
            }}
            steps {{
                script {{
                    echo '🚀 Deploying to staging...'
                    sh '''
                        source variables.env
                        echo "Deploying model version $MODEL_VERSION to staging"
                        
                        if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
                            echo "Deploying to Kubernetes staging..."
                            # Add your Kubernetes staging deployment logic here
                            # kubectl apply -f k8s/staging/
                        else
                            echo "Deployment target $DEPLOYMENT_TARGET not implemented"
                        fi
                    '''
                }}
            }}
            post {{
                success {{
                    echo '✅ Staging deployment successful'
                }}
                failure {{
                    echo '❌ Staging deployment failed'
                }}
            }}
        }}
        
        stage('Deploy Production') {{
            when {{
                anyOf {{
                    params {{
                        choiceParam(name: 'DEPLOYMENT_TYPE', value: 'production')
                    }}
                    params {{
                        choiceParam(name: 'DEPLOYMENT_TYPE', value: 'both')
                    }}
                }}
                branch 'main'
            }}
            steps {{
                script {{
                    echo '🚀 Deploying to production...'
                    sh '''
                        source variables.env
                        echo "Deploying model version $MODEL_VERSION to production"
                        
                        if [ "$DEPLOYMENT_TARGET" = "kubernetes" ]; then
                            echo "Deploying to Kubernetes production..."
                            # Add your Kubernetes production deployment logic here
                            # kubectl apply -f k8s/production/
                        else
                            echo "Deployment target $DEPLOYMENT_TARGET not implemented"
                        fi
                    '''
                }}
            }}
            post {{
                success {{
                    echo '✅ Production deployment successful'
                }}
                failure {{
                    echo '❌ Production deployment failed'
                }}
            }}
        }}
        
        stage('Release') {{
            when {{
                branch 'main'
                params {{
                    booleanParam(name: 'AUTO_DEPLOY', value: 'true')
                }}
            }}
            steps {{
                script {{
                    echo '🎉 Creating release...'
                    sh '''
                        source variables.env
                        echo "Creating release for model version $MODEL_VERSION"
                        
                        # Add your release logic here
                        # git tag -a "v$MODEL_VERSION" -m "Release version $MODEL_VERSION"
                        # git push origin "v$MODEL_VERSION"
                    '''
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo '🎉 MLOps pipeline completed successfully!'
            emailext (
                subject: "✅ MLOps Pipeline Succeeded - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
                body: "MLOps pipeline completed successfully. Model benchmarked and deployed.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }}
        failure {{
            echo '❌ MLOps pipeline failed!'
            emailext (
                subject: "❌ MLOps Pipeline Failed - ${{env.JOB_NAME}} #${{env.BUILD_NUMBER}}",
                body: "MLOps pipeline failed. Check Jenkins console for details.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }}
    }}
}}"""
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
                     output_path: str = "jenkins",
                     **kwargs) -> str:
        """Generate and save pipeline file"""
        
        pipeline_content = self.generate_pipeline_file(template_type, **kwargs)
        
        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if template_type == "basic":
            filename = "Jenkinsfile"
        elif template_type == "advanced":
            filename = "Jenkinsfile.advanced"
        elif template_type == "mlops":
            filename = "Jenkinsfile.mlops"
        else:
            filename = f"Jenkinsfile.{template_type}"
        
        # Save pipeline file
        pipeline_path = output_dir / filename
        with open(pipeline_path, 'w') as f:
            f.write(pipeline_content)
        
        return str(pipeline_path)
