"""
Quality evaluation for Clyrdia CLI - handles response quality assessment.
"""

import re
from typing import Dict, Any, List

class QualityEvaluator:
    """Evaluates the quality of AI model responses"""
    
    def __init__(self):
        # Define quality criteria weights
        self.criteria_weights = {
            'completeness': 0.3,
            'relevance': 0.25,
            'structure': 0.2,
            'specificity': 0.15,
            'professional_tone': 0.1
        }
    
    def evaluate_response(self, prompt: str, response: str, expected_output: str = None) -> Dict[str, float]:
        """Evaluate the quality of a response using multiple criteria"""
        if not response or not response.strip():
            return self._get_default_scores()
        
        scores = {}
        
        # 1. Completeness Score (how well the response addresses the prompt)
        scores['completeness'] = self._evaluate_completeness(prompt, response)
        
        # 2. Relevance Score (how relevant the response is to the prompt)
        scores['relevance'] = self._evaluate_relevance(prompt, response)
        
        # 3. Structure Score (how well-organized the response is)
        scores['structure'] = self._evaluate_structure(response)
        
        # 4. Specificity Score (how specific and actionable the response is)
        scores['specificity'] = self._evaluate_specificity(response)
        
        # 5. Professional Tone Score (how professional the response sounds)
        scores['professional_tone'] = self._evaluate_professional_tone(response)
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[criteria] * self.criteria_weights[criteria]
            for criteria in self.criteria_weights.keys()
        )
        scores['overall'] = max(0.1, overall_score)  # Ensure minimum score
        
        return scores
    
    def _get_default_scores(self) -> Dict[str, float]:
        """Return default scores when response is empty"""
        return {
            'completeness': 0.0,
            'relevance': 0.0,
            'structure': 0.0,
            'specificity': 0.0,
            'professional_tone': 0.0,
            'overall': 0.0
        }
    
    def _evaluate_completeness(self, prompt: str, response: str) -> float:
        """Evaluate how completely the response addresses the prompt"""
        if not response or len(response.strip()) < 10:
            return 0.1  # Minimum score instead of 0.0
        
        # Check if response length is appropriate for prompt complexity
        prompt_complexity = self._assess_prompt_complexity(prompt)
        expected_length = prompt_complexity * 100  # Base length expectation
        
        if len(response) < expected_length * 0.3:
            return 0.3  # Too short
        elif len(response) < expected_length * 0.6:
            return 0.6  # Moderately short
        elif len(response) < expected_length * 1.5:
            return 0.8  # Good length
        else:
            return 0.9  # Comprehensive
        
        return 0.7  # Default score
    
    def _evaluate_relevance(self, prompt: str, response: str) -> float:
        """Evaluate how relevant the response is to the prompt"""
        if not response:
            return 0.1  # Minimum score
        
        # Extract key concepts from prompt
        prompt_keywords = self._extract_keywords(prompt.lower())
        response_keywords = self._extract_keywords(response.lower())
        
        if not prompt_keywords:
            return 0.5  # Can't assess relevance
        
        # Calculate keyword overlap
        relevant_keywords = sum(1 for kw in prompt_keywords if any(kw in rk for rk in response_keywords))
        relevance_score = relevant_keywords / len(prompt_keywords)
        
        # Boost score for business-specific terms
        business_terms = ['strategy', 'analysis', 'assessment', 'recommendation', 'plan', 'approach']
        business_bonus = sum(0.1 for term in business_terms if term in response.lower())
        
        return max(0.1, min(1.0, relevance_score + business_bonus))
    
    def _evaluate_structure(self, response: str) -> float:
        """Evaluate how well-structured the response is"""
        if not response:
            return 0.1  # Minimum score
        
        score = 0.5  # Base score
        
        # Check for clear sections/paragraphs
        if re.search(r'\n\n', response):
            score += 0.2
        
        # Check for bullet points or numbered lists
        if re.search(r'^[\s]*[•\-\*]\s', response, re.MULTILINE) or re.search(r'^\d+\.\s', response, re.MULTILINE):
            score += 0.2
        
        # Check for headers or clear topic sentences
        if re.search(r'^[A-Z][^.!?]*[:]', response, re.MULTILINE):
            score += 0.1
        
        return max(0.1, min(1.0, score))
    
    def _evaluate_specificity(self, response: str) -> float:
        """Evaluate how specific and actionable the response is"""
        if not response:
            return 0.1  # Minimum score
        
        score = 0.3  # Base score
        
        # Check for specific numbers, percentages, or metrics
        if re.search(r'\d+%|\d+ percent|\$\d+|\d+ million|\d+ billion', response, re.IGNORECASE):
            score += 0.2
        
        # Check for actionable language
        action_words = ['should', 'must', 'need to', 'recommend', 'suggest', 'implement', 'establish', 'develop']
        action_count = sum(1 for word in action_words if word in response.lower())
        score += min(0.3, action_count * 0.1)
        
        # Check for concrete examples
        if re.search(r'for example|such as|including|specifically|in particular', response, re.IGNORECASE):
            score += 0.2
        
        return max(0.1, min(1.0, score))
    
    def _evaluate_professional_tone(self, response: str) -> float:
        """Evaluate how professional the response sounds"""
        if not response:
            return 0.1  # Minimum score
        
        score = 0.6  # Base score for business writing
        
        # Check for professional vocabulary
        professional_terms = ['strategy', 'implementation', 'optimization', 'efficiency', 'effectiveness', 'methodology']
        professional_count = sum(1 for term in professional_terms if term in response.lower())
        score += min(0.3, professional_count * 0.05)
        
        # Check for formal language structure
        if not re.search(r'\b(hey|hi|hello|thanks|thank you)\b', response, re.IGNORECASE):
            score += 0.1
        
        # Check for balanced, analytical language
        analytical_terms = ['however', 'furthermore', 'additionally', 'consequently', 'therefore', 'moreover']
        analytical_count = sum(1 for term in analytical_terms if term in response.lower())
        score += min(0.1, analytical_count * 0.02)
        
        return max(0.1, min(1.0, score))
    
    def _assess_prompt_complexity(self, prompt: str) -> float:
        """Assess the complexity of a prompt"""
        complexity = 1.0  # Base complexity
        
        # Increase complexity for business scenarios
        business_keywords = ['strategy', 'analysis', 'assessment', 'risk', 'legal', 'contract', 'architecture']
        business_count = sum(1 for keyword in business_keywords if keyword in prompt.lower())
        complexity += business_count * 0.3
        
        # Increase complexity for longer prompts
        if len(prompt) > 200:
            complexity += 0.5
        elif len(prompt) > 100:
            complexity += 0.3
        
        # Increase complexity for multi-step requests
        if re.search(r'and|also|additionally|furthermore|moreover', prompt, re.IGNORECASE):
            complexity += 0.2
        
        return min(3.0, complexity)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words and filter
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
