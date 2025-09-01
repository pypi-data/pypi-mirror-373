"""
SNID OpenRouter Integration
===========================

OpenRouter API integration for SNID LLM functionality.
"""

from .openrouter_llm import (
    call_openrouter_api,
    configure_openrouter_dialog,
    get_openrouter_config,
    get_openrouter_api_key,
    save_openrouter_api_key,
    save_openrouter_config,
    fetch_free_models,
    fetch_all_models,
    get_model_test_status,
    set_model_test_status,
    format_context_length,
    strip_thinking
)

from .openrouter_summary import (
    EnhancedOpenRouterSummary,
    create_openrouter_summary
)

__all__ = [
    'call_openrouter_api',
    'configure_openrouter_dialog', 
    'get_openrouter_config',
    'get_openrouter_api_key',
    'save_openrouter_api_key',
    'save_openrouter_config',
    'fetch_free_models',
    'fetch_all_models',
    'get_model_test_status',
    'set_model_test_status',
    'format_context_length',
    'strip_thinking',
    'EnhancedOpenRouterSummary',
    'create_openrouter_summary'
] 