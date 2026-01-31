"""
Advanced AI Detection Module for Django
Detects AI-generated content in student writing
"""

import re
import numpy as np
from typing import Tuple, List, Dict


class AdvancedAIDetector:
    """
    Advanced AI detection using multiple heuristics:
    - Pattern matching
    - Statistical analysis
    - Vocabulary analysis
    - Structure analysis
    """
    
    def __init__(self):
        self.ai_phrases = [
            r'\b(furthermore|moreover|in conclusion|to summarize)\b',
            r'\b(it is worth noting|one might argue|it can be observed)\b',
            r'\b(additionally|consequently|therefore|thus|hence)\b',
            r'\b(in essence|to put it simply|in other words)\b',
            r'\b(it is important to note|it should be noted)\b',
            r'\b(it is crucial to|it is essential to|it is vital to)\b',
        ]
        
        self.sophisticated_vocab = [
            'paradigm', 'facilitate', 'utilize', 'implement', 'comprehensive',
            'substantial', 'significant', 'considerable', 'noteworthy',
            'remarkable', 'exemplify', 'demonstrate', 'illustrate', 'elucidate'
        ]
        
        self.transition_words = [
            'furthermore', 'moreover', 'additionally', 'consequently',
            'therefore', 'thus', 'hence', 'accordingly', 'subsequently'
        ]
    
    def analyze_text_statistics(self, text: str) -> Dict:
        """Analyze statistical features of text"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {}
        
        words = text.split()
        word_lengths = [len(w) for w in words]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        stats = {
            'avg_word_length': float(np.mean(word_lengths)) if word_lengths else 0,
            'avg_sentence_length': float(np.mean(sentence_lengths)) if sentence_lengths else 0,
            'sentence_length_std': float(np.std(sentence_lengths)) if len(sentence_lengths) > 1 else 0,
            'total_sentences': len(sentences),
            'total_words': len(words),
            'unique_words_ratio': len(set(words)) / len(words) if words else 0
        }
        
        return stats
    
    def detect_patterns(self, text: str) -> Tuple[int, List[str]]:
        """Detect AI indicator patterns"""
        text_lower = text.lower()
        matches = 0
        detected_patterns = []
        
        for pattern in self.ai_phrases:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                matches += len(found)
                detected_patterns.append(pattern)
        
        # Check for sophisticated vocabulary
        sophisticated_count = sum(1 for word in self.sophisticated_vocab if word in text_lower)
        if sophisticated_count >= 3:
            matches += 2
            detected_patterns.append('SOPHISTICATED_VOCAB')
        
        # Check for excessive transition words
        transition_count = sum(1 for word in self.transition_words if word in text_lower)
        if transition_count >= 5:
            matches += 1
            detected_patterns.append('EXCESSIVE_TRANSITIONS')
        
        return matches, detected_patterns
    
    def calculate_ai_confidence(self, text: str) -> float:
        """
        Calculate confidence score (0-1) that text is AI-generated
        """
        if not text or len(text.strip()) < 50:
            return 0.0
        
        confidence = 0.0
        
        # Pattern detection
        pattern_matches, patterns = self.detect_patterns(text)
        if pattern_matches >= 5:
            confidence += 0.4
        elif pattern_matches >= 3:
            confidence += 0.3
        elif pattern_matches >= 2:
            confidence += 0.2
        elif pattern_matches >= 1:
            confidence += 0.1
        
        # Statistical analysis
        stats = self.analyze_text_statistics(text)
        
        # Very consistent sentence length (AI characteristic)
        if stats.get('sentence_length_std', 100) < 15 and stats.get('total_sentences', 0) > 3:
            confidence += 0.2
        
        # High average sentence length (AI often writes longer sentences)
        if stats.get('avg_sentence_length', 0) > 20:
            confidence += 0.1
        
        # Low vocabulary diversity (AI might repeat phrases)
        if stats.get('unique_words_ratio', 1) < 0.5 and stats.get('total_words', 0) > 100:
            confidence += 0.1
        
        # Check for explicit AI markers
        text_lower = text.lower()
        if '[ai enhanced' in text_lower or '[ai assisted' in text_lower:
            confidence = 1.0
        
        return min(confidence, 1.0)
    
    def detect(self, text: str) -> Dict:
        """
        Main detection method
        Returns: {
            'is_ai_used': bool,
            'confidence': float,
            'patterns': List[str],
            'statistics': dict
        }
        """
        if not text or len(text.strip()) < 50:
            return {
                'is_ai_used': False,
                'confidence': 0.0,
                'patterns': [],
                'statistics': {}
            }
        
        confidence = self.calculate_ai_confidence(text)
        _, patterns = self.detect_patterns(text)
        stats = self.analyze_text_statistics(text)
        
        is_ai_used = confidence >= 0.4
        
        return {
            'is_ai_used': is_ai_used,
            'confidence': round(confidence, 3),
            'patterns': patterns,
            'statistics': stats
        }


# Export singleton instance
ai_detector = AdvancedAIDetector()
