"""
LLM utility functions for DeepCode project.

This module provides common LLM-related utilities to avoid circular imports
and reduce code duplication across the project.
"""

import os
import yaml
from typing import Any, Type, Dict, Tuple

# Import LLM classes. These will be monkey-patched at runtime.
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM


def get_preferred_llm_class(config_path: str = "mcp_agent.secrets.yaml") -> Type[Any]:
    """
    Returns a preferred LLM class. Since the classes are monkey-patched to use
    Gemini at runtime, we can return either. We return OpenAIAugmentedLLM for
    consistency. The function signature is maintained for compatibility.
    """
    return OpenAIAugmentedLLM


def get_default_models(config_path: str = "mcp_agent.config.yaml"):
    """
    Get default models from configuration file.
    For compatibility, this function still returns 'anthropic' and 'openai' keys,
    but they now point to the Gemini model defined in the configuration.
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            gemini_config = config.get("google_gemini") or {}
            gemini_model = gemini_config.get("default_model", "gemini-1.5-flash")

            return {"anthropic": gemini_model, "openai": gemini_model}
        else:
            print(f"Config file {config_path} not found, using default models")
            return {"anthropic": "gemini-1.5-flash", "openai": "gemini-1.5-flash"}

    except Exception as e:
        print(f"❌Error reading config file {config_path}: {e}")
        return {"anthropic": "gemini-1.5-flash", "openai": "gemini-1.5-flash"}


def get_document_segmentation_config(
    config_path: str = "mcp_agent.config.yaml",
) -> Dict[str, Any]:
    """
    Get document segmentation configuration from config file.
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            seg_config = config.get("document_segmentation", {})
            return {
                "enabled": seg_config.get("enabled", True),
                "size_threshold_chars": seg_config.get("size_threshold_chars", 50000),
            }
        else:
            return {"enabled": True, "size_threshold_chars": 50000}
    except Exception as e:
        print(f"📄 Error reading segmentation config from {config_path}: {e}")
        return {"enabled": True, "size_threshold_chars": 50000}


def should_use_document_segmentation(
    document_content: str, config_path: str = "mcp_agent.config.yaml"
) -> Tuple[bool, str]:
    """
    Determine whether to use document segmentation based on configuration and document size.
    """
    seg_config = get_document_segmentation_config(config_path)
    if not seg_config["enabled"]:
        return False, "Document segmentation disabled in configuration"
    doc_size = len(document_content)
    threshold = seg_config["size_threshold_chars"]
    if doc_size > threshold:
        return True, f"Document size ({doc_size:,} chars) exceeds threshold ({threshold:,} chars)"
    else:
        return False, f"Document size ({doc_size:,} chars) below threshold ({threshold:,} chars)"


def get_adaptive_agent_config(
    use_segmentation: bool, search_server_names: list = None
) -> Dict[str, list]:
    """
    Get adaptive agent configuration based on whether to use document segmentation.
    """
    if search_server_names is None:
        search_server_names = []
    config = {
        "concept_analysis": [],
        "algorithm_analysis": search_server_names.copy(),
        "code_planner": search_server_names.copy(),
    }
    if use_segmentation:
        config["concept_analysis"] = ["document-segmentation"]
        if "document-segmentation" not in config["algorithm_analysis"]:
            config["algorithm_analysis"].append("document-segmentation")
        if "document-segmentation" not in config["code_planner"]:
            config["code_planner"].append("document-segmentation")
    else:
        config["concept_analysis"] = ["filesystem"]
        if "filesystem" not in config["algorithm_analysis"]:
            config["algorithm_analysis"].append("filesystem")
        if "filesystem" not in config["code_planner"]:
            config["code_planner"].append("filesystem")
    return config


def get_adaptive_prompts(use_segmentation: bool) -> Dict[str, str]:
    """
    Get appropriate prompt versions based on segmentation usage.
    """
    from prompts.code_prompts import (
        PAPER_CONCEPT_ANALYSIS_PROMPT,
        PAPER_ALGORITHM_ANALYSIS_PROMPT,
        CODE_PLANNING_PROMPT,
        PAPER_CONCEPT_ANALYSIS_PROMPT_TRADITIONAL,
        PAPER_ALGORITHM_ANALYSIS_PROMPT_TRADITIONAL,
        CODE_PLANNING_PROMPT_TRADITIONAL,
    )
    if use_segmentation:
        return {
            "concept_analysis": PAPER_CONCEPT_ANALYSIS_PROMPT,
            "algorithm_analysis": PAPER_ALGORITHM_ANALYSIS_PROMPT,
            "code_planning": CODE_PLANNING_PROMPT,
        }
    else:
        return {
            "concept_analysis": PAPER_CONCEPT_ANALYSIS_PROMPT_TRADITIONAL,
            "algorithm_analysis": PAPER_ALGORITHM_ANALYSIS_PROMPT_TRADITIONAL,
            "code_planning": CODE_PLANNING_PROMPT_TRADITIONAL,
        }