"""
Validation utilities for LangChain services
"""
from typing import Dict, Any, List, Optional, Union
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationUtils:
    """Utility class for validating inputs and outputs"""
    
    @staticmethod
    def validate_tenant_id(tenant_id: str) -> bool:
        """Validate tenant ID format"""
        if not tenant_id or not isinstance(tenant_id, str):
            return False
        
        # Basic format validation (alphanumeric, hyphens, underscores)
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, tenant_id)) and len(tenant_id) <= 100
    
    @staticmethod
    def validate_question(question: str) -> Dict[str, Any]:
        """Validate question format and content"""
        if not question or not isinstance(question, str):
            return {"valid": False, "error": "Question must be a non-empty string"}
        
        if len(question.strip()) < 3:
            return {"valid": False, "error": "Question must be at least 3 characters long"}
        
        if len(question) > 10000:
            return {"valid": False, "error": "Question must be less than 10000 characters"}
        
        # Check for potentially malicious content
        suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload=',
            r'onerror='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                return {"valid": False, "error": "Question contains potentially malicious content"}
        
        return {"valid": True, "error": None}
    
    @staticmethod
    def validate_document_content(content: bytes, file_type: str) -> Dict[str, Any]:
        """Validate document content"""
        if not content or not isinstance(content, bytes):
            return {"valid": False, "error": "Content must be bytes"}
        
        if len(content) == 0:
            return {"valid": False, "error": "Content cannot be empty"}
        
        # Check file size limits (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            return {"valid": False, "error": f"File size exceeds limit of {max_size} bytes"}
        
        # Validate file type
        valid_types = ['pdf', 'docx', 'doc', 'txt', 'md', 'markdown']
        if file_type.lower() not in valid_types:
            return {"valid": False, "error": f"Unsupported file type: {file_type}"}
        
        # Basic content validation based on file type
        if file_type.lower() == 'pdf':
            if not content.startswith(b'%PDF'):
                return {"valid": False, "error": "Invalid PDF file format"}
        
        elif file_type.lower() in ['docx', 'doc']:
            if not content.startswith(b'PK'):
                return {"valid": False, "error": "Invalid DOCX/DOC file format"}
        
        return {"valid": True, "error": None}
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['llm_provider', 'embedding_provider']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate LLM provider
        if 'llm_provider' in config:
            valid_providers = ['openai', 'ollama', 'huggingface']
            if config['llm_provider'] not in valid_providers:
                errors.append(f"Invalid LLM provider: {config['llm_provider']}")
        
        # Validate embedding provider
        if 'embedding_provider' in config:
            valid_providers = ['openai', 'huggingface']
            if config['embedding_provider'] not in valid_providers:
                errors.append(f"Invalid embedding provider: {config['embedding_provider']}")
        
        # Validate numeric parameters
        numeric_fields = {
            'chunk_size': (100, 10000),
            'chunk_overlap': (0, 1000),
            'max_hops': (1, 10),
            'temperature': (0.0, 2.0)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                try:
                    value = float(config[field])
                    if not (min_val <= value <= max_val):
                        errors.append(f"{field} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        # Validate string parameters
        string_fields = {
            'ollama_base_url': r'^https?://.+',
            'openai_model': r'^gpt-[0-9.-]+$',
            'embedding_model': r'^.+$'
        }
        
        for field, pattern in string_fields.items():
            if field in config:
                if not isinstance(config[field], str):
                    errors.append(f"{field} must be a string")
                elif not re.match(pattern, config[field]):
                    warnings.append(f"{field} format may be invalid: {config[field]}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response format"""
        errors = []
        
        # Required fields
        required_fields = ['answer', 'metadata']
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")
        
        # Validate answer
        if 'answer' in response:
            if not isinstance(response['answer'], str):
                errors.append("Answer must be a string")
            elif len(response['answer']) == 0:
                errors.append("Answer cannot be empty")
        
        # Validate confidence
        if 'confidence' in response:
            try:
                confidence = float(response['confidence'])
                if not (0.0 <= confidence <= 1.0):
                    errors.append("Confidence must be between 0.0 and 1.0")
            except (ValueError, TypeError):
                errors.append("Confidence must be a valid number")
        
        # Validate sources
        if 'sources' in response:
            if not isinstance(response['sources'], list):
                errors.append("Sources must be a list")
            else:
                for i, source in enumerate(response['sources']):
                    if not isinstance(source, dict):
                        errors.append(f"Source {i} must be a dictionary")
                    elif 'content' not in source:
                        errors.append(f"Source {i} missing content field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata format"""
        errors = []
        
        if not isinstance(metadata, dict):
            return {"valid": False, "errors": ["Metadata must be a dictionary"]}
        
        # Check for required fields
        if 'tenant_id' not in metadata:
            errors.append("Metadata missing tenant_id")
        elif not ValidationUtils.validate_tenant_id(metadata['tenant_id']):
            errors.append("Invalid tenant_id format")
        
        # Check for suspicious content
        for key, value in metadata.items():
            if isinstance(value, str):
                if len(value) > 1000:
                    errors.append(f"Metadata field '{key}' too long")
                
                # Check for potential injection
                if any(char in value for char in ['<', '>', '"', "'", '&']):
                    errors.append(f"Metadata field '{key}' contains potentially unsafe characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text"""
        if not isinstance(text, str):
            return ""
        
        # Remove or escape potentially dangerous characters
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:text/html', '', text, flags=re.IGNORECASE)
        text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
        
        # Limit length
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return text.strip()
    
    @staticmethod
    def validate_query_options(options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate query options"""
        errors = []
        
        if not isinstance(options, dict):
            return {"valid": False, "errors": ["Options must be a dictionary"]}
        
        # Validate top_k
        if 'top_k' in options:
            try:
                top_k = int(options['top_k'])
                if not (1 <= top_k <= 100):
                    errors.append("top_k must be between 1 and 100")
            except (ValueError, TypeError):
                errors.append("top_k must be a valid integer")
        
        # Validate use_conversational
        if 'use_conversational' in options:
            if not isinstance(options['use_conversational'], bool):
                errors.append("use_conversational must be a boolean")
        
        # Validate max_hops
        if 'max_hops' in options:
            try:
                max_hops = int(options['max_hops'])
                if not (1 <= max_hops <= 10):
                    errors.append("max_hops must be between 1 and 10")
            except (ValueError, TypeError):
                errors.append("max_hops must be a valid integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_health_check_response(response: Dict[str, Any]) -> bool:
        """Validate health check response format"""
        required_fields = ['overall', 'components']
        
        for field in required_fields:
            if field not in response:
                return False
        
        if not isinstance(response['overall'], bool):
            return False
        
        if not isinstance(response['components'], dict):
            return False
        
        return True
    
    @staticmethod
    def validate_tenant_stats_response(response: Dict[str, Any]) -> bool:
        """Validate tenant stats response format"""
        required_fields = ['tenant_id']
        
        for field in required_fields:
            if field not in response:
                return False
        
        if not isinstance(response['tenant_id'], str):
            return False
        
        return True
