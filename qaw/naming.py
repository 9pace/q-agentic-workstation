"""
Semantic agent naming utilities.

Generates meaningful agent names from task descriptions instead of random UUIDs.
"""

import re
from typing import Optional


class AgentNamer:
    """Generate semantic names for agents based on task descriptions."""
    
    # Common stop words to remove
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Action words to prioritize
    ACTION_WORDS = {
        'add', 'create', 'build', 'implement', 'fix', 'debug', 'refactor',
        'update', 'modify', 'delete', 'remove', 'test', 'verify', 'review',
        'optimize', 'improve', 'migrate', 'deploy', 'setup', 'configure',
        'integrate', 'document', 'analyze', 'design', 'validate'
    }
    
    @classmethod
    def generate_name(
        cls,
        task_description: str,
        agent_type: str,
        max_length: int = 40,
        custom_name: Optional[str] = None,
    ) -> str:
        """
        Generate a semantic agent name.
        
        Args:
            task_description: The task the agent will perform
            agent_type: Type of agent (e.g., 'frontend', 'backend', 'test')
            max_length: Maximum name length
            custom_name: Optional custom name override
            
        Returns:
            Semantic agent name like 'backend-auth-login' or 'frontend-navbar-refactor'
            
        Examples:
            >>> AgentNamer.generate_name("Add user authentication with JWT", "backend")
            'backend-auth-user-jwt'
            
            >>> AgentNamer.generate_name("Fix navbar scrolling bug", "frontend")
            'frontend-fix-navbar-scroll'
            
            >>> AgentNamer.generate_name("Refactor database queries", "backend")
            'backend-refactor-db-queries'
        """
        if custom_name:
            return cls._sanitize_name(custom_name, max_length)
        
        # Extract key terms from task description
        key_terms = cls._extract_key_terms(task_description, max_words=3)
        
        # Build name: agent_type-key_term1-key_term2-key_term3
        name_parts = [agent_type] + key_terms
        name = '-'.join(name_parts)
        
        # Truncate if too long
        if len(name) > max_length:
            name = name[:max_length].rsplit('-', 1)[0]  # Cut at word boundary
        
        return name
    
    @classmethod
    def _extract_key_terms(cls, text: str, max_words: int = 3) -> list[str]:
        """
        Extract the most important terms from text.
        
        Prioritizes:
        1. Action words (add, fix, create, etc.)
        2. Technical terms (auth, database, api, etc.)
        3. Domain-specific words
        
        Args:
            text: Input text
            max_words: Maximum number of words to extract
            
        Returns:
            List of key terms
        """
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Remove stop words
        words = [w for w in words if w not in cls.STOP_WORDS and len(w) > 2]
        
        if not words:
            return ['task']
        
        # Prioritize action words
        action_words = [w for w in words if w in cls.ACTION_WORDS]
        other_words = [w for w in words if w not in cls.ACTION_WORDS]
        
        # Start with action word if present
        key_terms = []
        if action_words:
            key_terms.append(action_words[0])
            max_words -= 1
        
        # Add remaining words (up to max_words)
        key_terms.extend(other_words[:max_words])
        
        # Abbreviate common long words
        key_terms = [cls._abbreviate(term) for term in key_terms]
        
        return key_terms[:max_words]
    
    @classmethod
    def _abbreviate(cls, word: str) -> str:
        """Abbreviate common long technical terms."""
        abbreviations = {
            'authentication': 'auth',
            'authorization': 'authz',
            'database': 'db',
            'configuration': 'config',
            'application': 'app',
            'development': 'dev',
            'production': 'prod',
            'environment': 'env',
            'repository': 'repo',
            'documentation': 'docs',
            'javascript': 'js',
            'typescript': 'ts',
            'python': 'py',
            'integration': 'integ',
            'implementation': 'impl',
            'component': 'comp',
            'navigation': 'nav',
            'administration': 'admin',
            'utilities': 'utils',
            'middleware': 'mw',
            'endpoint': 'ep',
        }
        return abbreviations.get(word, word)
    
    @classmethod
    def _sanitize_name(cls, name: str, max_length: int) -> str:
        """Sanitize a custom name to be filesystem/identifier safe."""
        # Convert to lowercase, replace spaces/special chars with dashes
        name = re.sub(r'[^a-z0-9]+', '-', name.lower())
        # Remove leading/trailing dashes
        name = name.strip('-')
        # Truncate if needed
        if len(name) > max_length:
            name = name[:max_length].rsplit('-', 1)[0]
        return name or 'agent'
    
    @classmethod
    def generate_display_name(cls, agent_name: str, task_description: str) -> str:
        """
        Generate a human-readable display name.
        
        Args:
            agent_name: Generated agent name
            task_description: Original task
            
        Returns:
            Display name like "Backend Auth (Add user authentication)"
        """
        # Capitalize and format agent name
        parts = agent_name.split('-')
        formatted = ' '.join(part.capitalize() for part in parts)
        
        # Truncate task description for display
        task_preview = task_description[:50]
        if len(task_description) > 50:
            task_preview += "..."
        
        return f"{formatted} ({task_preview})"


def generate_manager_name(plan_summary: str) -> str:
    """
    Generate a name for a manager agent orchestrating a plan.
    
    Args:
        plan_summary: Summary of the plan being executed
        
    Returns:
        Manager name like 'manager-auth-system' or 'manager-refactor-api'
    """
    key_terms = AgentNamer._extract_key_terms(plan_summary, max_words=2)
    name = 'manager-' + '-'.join(key_terms)
    return name[:40]


def generate_verifier_name(stage: str, target: str) -> str:
    """
    Generate a name for a verification agent.
    
    Args:
        stage: Verification stage ('alignment', 'review', 'test')
        target: What's being verified
        
    Returns:
        Verifier name like 'alignment-auth-login' or 'test-verify-api'
    """
    key_terms = AgentNamer._extract_key_terms(target, max_words=2)
    name = f"{stage}-" + '-'.join(key_terms)
    return name[:40]
