"""
Prompt Management System for configurable and tunable prompts.
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """Manages configurable prompts for agents."""
    
    def __init__(self, config_dir: str = None):
        """Initialize prompt manager."""
        if config_dir is None:
            # Default to config directory relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self._prompt_cache = {}
    
    def load_prompts(self, agent_name: str) -> Dict[str, Any]:
        """Load prompts for a specific agent."""
        config_file = self.config_dir / f"{agent_name}_prompts.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Prompt configuration not found: {config_file}")
        
        # Cache prompts to avoid re-reading
        cache_key = f"{agent_name}_{config_file.stat().st_mtime}"
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
        
        with open(config_file, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        
        self._prompt_cache[cache_key] = prompts
        return prompts
    
    def get_system_prompt(self, agent_name: str, variant: str = "default") -> str:
        """Get system prompt for an agent."""
        prompts = self.load_prompts(agent_name)
        
        if variant == "default":
            return prompts.get("system_prompt", "")
        else:
            variants = prompts.get("prompt_variants", {})
            if variant in variants:
                return variants[variant].get("system_prompt", "")
            else:
                raise ValueError(f"Prompt variant '{variant}' not found for agent '{agent_name}'")
    
    def get_user_prompt_template(self, agent_name: str, variant: str = "default") -> str:
        """Get user prompt template for an agent."""
        prompts = self.load_prompts(agent_name)
        
        if variant == "default":
            return prompts.get("user_prompt_template", "")
        else:
            variants = prompts.get("prompt_variants", {})
            if variant in variants:
                return variants[variant].get("user_template", "")
            else:
                raise ValueError(f"Prompt variant '{variant}' not found for agent '{agent_name}'")
    
    def format_user_prompt(self, agent_name: str, variant: str = "default", **kwargs) -> str:
        """Format user prompt with provided variables."""
        template = self.get_user_prompt_template(agent_name, variant)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable {e} for agent '{agent_name}' variant '{variant}'")
    
    def get_model_config(self, agent_name: str) -> Dict[str, Any]:
        """Get model configuration for an agent."""
        prompts = self.load_prompts(agent_name)
        return prompts.get("model_config", {})
    
    def get_response_cleaning_config(self, agent_name: str) -> Dict[str, Any]:
        """Get response cleaning configuration for an agent."""
        prompts = self.load_prompts(agent_name)
        return prompts.get("response_cleaning", {})
    
    def get_fallback_prompts(self, agent_name: str) -> list:
        """Get fallback prompts for an agent."""
        prompts = self.load_prompts(agent_name)
        return prompts.get("fallback_prompts", [])
    
    def save_prompts(self, agent_name: str, prompts: Dict[str, Any]):
        """Save updated prompts for an agent."""
        config_file = self.config_dir / f"{agent_name}_prompts.yaml"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(prompts, f, default_flow_style=False, allow_unicode=True)
        
        # Clear cache for this agent
        self._prompt_cache = {k: v for k, v in self._prompt_cache.items() 
                            if not k.startswith(f"{agent_name}_")}
    
    def list_available_variants(self, agent_name: str) -> list:
        """List available prompt variants for an agent."""
        prompts = self.load_prompts(agent_name)
        variants = ["default"]
        if "prompt_variants" in prompts:
            variants.extend(prompts["prompt_variants"].keys())
        return variants


# Global prompt manager instance
_global_prompt_manager = None


def get_prompt_manager(config_dir: str = None) -> PromptManager:
    """Get global prompt manager instance."""
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager(config_dir)
    return _global_prompt_manager


def load_agent_prompts(agent_name: str) -> Dict[str, Any]:
    """Convenience function to load prompts for an agent."""
    return get_prompt_manager().load_prompts(agent_name)