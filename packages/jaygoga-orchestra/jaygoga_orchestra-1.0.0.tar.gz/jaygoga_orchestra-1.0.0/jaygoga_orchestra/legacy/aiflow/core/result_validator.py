"""
Result Validation System for AIFlow.

Prevents hallucination and ensures real outputs from agents and tools.
NO TOLERANCE FOR SIMULATION OR FAKE RESULTS.
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime


class HallucinationDetector:
    """Detects and prevents hallucination in agent outputs."""
    
    # Simulation keywords that indicate fake results
    SIMULATION_KEYWORDS = [
        'simulation', 'simulated', 'mock', 'mocked', 'placeholder', 'example',
        'demo', 'fake', 'test data', 'sample data', 'dummy', 'fictional',
        'hypothetical', 'imaginary', 'pretend', 'artificial', 'synthetic'
    ]
    
    # Fake URL patterns
    FAKE_URL_PATTERNS = [
        'example.com', 'test.com', 'demo.com', 'placeholder.com',
        'sample.com', 'fake.com', 'mock.com', 'dummy.com'
    ]
    
    # Generic response patterns that indicate simulation
    GENERIC_PATTERNS = [
        r'task completed successfully',
        r'operation finished',
        r'process complete',
        r'analysis complete',
        r'done',
        r'finished',
        r'completed as requested',
        r'here is your result',
        r'i have completed'
    ]
    
    @classmethod
    def detect_simulation(cls, content: Any) -> Tuple[bool, List[str]]:
        """
        Detect if content contains simulation or fake data.
        
        Returns:
            (is_simulation, list_of_issues)
        """
        issues = []
        content_str = str(content).lower()
        
        # Check for simulation keywords
        for keyword in cls.SIMULATION_KEYWORDS:
            if keyword in content_str:
                issues.append(f"Simulation keyword detected: '{keyword}'")
        
        # Check for fake URLs
        for pattern in cls.FAKE_URL_PATTERNS:
            if pattern in content_str:
                issues.append(f"Fake URL pattern detected: '{pattern}'")
        
        # Check for generic responses
        for pattern in cls.GENERIC_PATTERNS:
            if re.search(pattern, content_str) and len(content_str.strip()) < 100:
                issues.append(f"Generic response pattern detected: '{pattern}'")
        
        # Check for insufficient content
        if len(content_str.strip()) < 10:
            issues.append("Insufficient content - likely placeholder")
        
        # Check for repeated patterns (common in generated fake data)
        words = content_str.split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # If any word appears more than 30% of the time, it's suspicious
            max_freq = max(word_freq.values())
            if max_freq > len(words) * 0.3:
                issues.append("Repetitive content detected - possible generated text")
        
        return len(issues) > 0, issues


class OutputValidator:
    """Validates specific types of outputs for authenticity."""
    
    def __init__(self):
        self.detector = HallucinationDetector()
    
    def validate_web_search_results(self, results: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate web search results for authenticity."""
        if not results.get('success'):
            return True, "Failed search is valid"
        
        search_results = results.get('results', [])
        if not search_results:
            return True, "Empty results are valid"
        
        for result in search_results:
            # Check URL authenticity
            url = result.get('url', '')
            if any(fake_pattern in url for fake_pattern in self.detector.FAKE_URL_PATTERNS):
                return False, f"Fake URL detected in search results: {url}"
            
            # Check source field
            source = result.get('source', '').lower()
            if 'demo' in source or 'fake' in source or 'mock' in source:
                return False, f"Fake source detected: {source}"
            
            # Check content for simulation
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            is_sim, issues = self.detector.detect_simulation(f"{title} {snippet}")
            if is_sim:
                return False, f"Simulation detected in search result: {', '.join(issues)}"
        
        return True, "Valid web search results"
    
    def validate_file_operation(self, result: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate file operation results."""
        if not result.get('success'):
            return True, "Failed operation is valid"
        
        operation = result.get('operation')
        filepath = result.get('filepath')
        
        if not filepath:
            return False, "No filepath provided in file operation result"
        
        path = Path(filepath)
        
        # For write operations, verify file actually exists
        if operation == 'write':
            if not path.exists():
                return False, f"Write operation claimed success but file doesn't exist: {filepath}"
            
            # Check file size consistency
            if 'file_size' in result:
                actual_size = path.stat().st_size
                claimed_size = result['file_size']
                if abs(actual_size - claimed_size) > 100:  # Allow small differences
                    return False, f"File size mismatch: claimed {claimed_size}, actual {actual_size}"
        
        # For read operations, verify content makes sense
        if operation == 'read':
            if not path.exists():
                return False, f"Read operation claimed success but file doesn't exist: {filepath}"
            
            content = result.get('content')
            if content is None:
                return False, "Read operation missing content"
            
            # Check if content contains simulation markers
            is_sim, issues = self.detector.detect_simulation(content)
            if is_sim:
                return False, f"Simulation detected in file content: {', '.join(issues)}"
        
        return True, "Valid file operation"
    
    def validate_data_analysis(self, result: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data analysis results."""
        if not result.get('success'):
            return True, "Failed analysis is valid"
        
        # Check for realistic data ranges
        if 'statistics' in result:
            stats = result['statistics']
            for column, column_stats in stats.items():
                # Check for unrealistic values
                mean = column_stats.get('mean')
                std = column_stats.get('std')
                
                if mean is not None and std is not None:
                    # Standard deviation shouldn't be negative
                    if std < 0:
                        return False, f"Invalid negative standard deviation for {column}: {std}"
                    
                    # Check for impossible statistical relationships
                    min_val = column_stats.get('min')
                    max_val = column_stats.get('max')
                    if min_val is not None and max_val is not None:
                        if min_val > max_val:
                            return False, f"Invalid min > max for {column}: {min_val} > {max_val}"
                        
                        if mean < min_val or mean > max_val:
                            return False, f"Mean outside min/max range for {column}"
        
        # Check for simulation in analysis content
        is_sim, issues = self.detector.detect_simulation(result)
        if is_sim:
            return False, f"Simulation detected in analysis: {', '.join(issues)}"
        
        return True, "Valid data analysis"
    
    def validate_llm_response(self, response: str) -> Tuple[bool, str]:
        """Validate LLM response for authenticity."""
        # Check for simulation markers
        is_sim, issues = self.detector.detect_simulation(response)
        if is_sim:
            return False, f"Simulation detected in LLM response: {', '.join(issues)}"
        
        # Check for overly generic responses
        if len(response.strip()) < 20:
            return False, "Response too short - likely generic"
        
        # Check for common AI refusal patterns that might indicate simulation
        refusal_patterns = [
            "i cannot", "i'm unable to", "i don't have access",
            "as an ai", "i'm an ai", "i cannot provide"
        ]
        
        response_lower = response.lower()
        refusal_count = sum(1 for pattern in refusal_patterns if pattern in response_lower)
        
        # If response is mostly refusals, it might be simulated
        if refusal_count > 2 and len(response.split()) < 50:
            return False, "Response appears to be simulated AI refusal"
        
        return True, "Valid LLM response"


class ResultValidationSystem:
    """Complete result validation system for AIFlow."""
    
    def __init__(self):
        self.validator = OutputValidator()
        self.validation_log = []
    
    def validate_result(self, result: Any, result_type: str = "general") -> Tuple[bool, str]:
        """
        Validate any result based on its type.
        
        Args:
            result: The result to validate
            result_type: Type of result ("web_search", "file_operation", "data_analysis", "llm_response", "general")
            
        Returns:
            (is_valid, reason)
        """
        validation_entry = {
            "timestamp": datetime.now().isoformat(),
            "result_type": result_type,
            "result_size": len(str(result)),
            "validation_passed": False,
            "issues": []
        }
        
        try:
            if result_type == "web_search":
                is_valid, reason = self.validator.validate_web_search_results(result)
            elif result_type == "file_operation":
                is_valid, reason = self.validator.validate_file_operation(result)
            elif result_type == "data_analysis":
                is_valid, reason = self.validator.validate_data_analysis(result)
            elif result_type == "llm_response":
                is_valid, reason = self.validator.validate_llm_response(result)
            else:
                # General validation
                is_sim, issues = self.validator.detector.detect_simulation(result)
                is_valid = not is_sim
                reason = f"Simulation detected: {', '.join(issues)}" if is_sim else "Valid result"
            
            validation_entry["validation_passed"] = is_valid
            validation_entry["reason"] = reason
            
            if not is_valid:
                validation_entry["issues"].append(reason)
            
        except Exception as e:
            is_valid = False
            reason = f"Validation error: {str(e)}"
            validation_entry["validation_passed"] = False
            validation_entry["reason"] = reason
            validation_entry["issues"].append(reason)
        
        self.validation_log.append(validation_entry)
        return is_valid, reason
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations performed."""
        total_validations = len(self.validation_log)
        passed_validations = sum(1 for entry in self.validation_log if entry["validation_passed"])
        
        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "success_rate": passed_validations / total_validations if total_validations > 0 else 0,
            "validation_log": self.validation_log[-10:]  # Last 10 entries
        }
    
    def clear_log(self):
        """Clear validation log."""
        self.validation_log.clear()
    
    def save_validation_log(self, filepath: str = None) -> str:
        """Save validation log to file."""
        if not filepath:
            filepath = f"validation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            "summary": self.get_validation_summary(),
            "full_log": self.validation_log
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return filepath
