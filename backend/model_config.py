"""
Model configuration for Ollama LLM models.
Defines available models with their tiers and recommended configurations.
"""

# Model tier configuration with recommended use cases
MODEL_TIERS = {
    "llama3.1:8b": {
        "tier": "Fast",
        "size": "4.9 GB",
        "description": "Lightweight model for quick responses",
        "recommended_timeout": 20
    },
    "gpt-oss:20b": {
        "tier": "Balanced",
        "size": "13 GB",
        "description": "Good balance of speed and quality",
        "recommended_timeout": 120
    },
    "qwen2.5-coder:32b": {
        "tier": "Balanced",
        "size": "19 GB",
        "description": "Optimized for code and technical analysis",
        "recommended_timeout": 60
    },
    "deepseek-r1:32b": {
        "tier": "Balanced",
        "size": "19 GB",
        "description": "Advanced reasoning capabilities",
        "recommended_timeout": 60
    },
    "llama3.3:70b-instruct-q2_K": {
        "tier": "High Quality",
        "size": "26 GB",
        "description": "High quality with quantization",
        "recommended_timeout": 90
    },
    "llama3.3:70b": {
        "tier": "Best Quality",
        "size": "42 GB",
        "description": "Maximum quality for complex analysis",
        "recommended_timeout": 600
    },
    "gpt-oss:120b": {
        "tier": "Best Quality",
        "size": "65 GB",
        "description": "Largest model for most demanding tasks",
        "recommended_timeout": 600
    }
}

# Default model to load on startup
DEFAULT_MODEL = "qwen2.5-coder:32b"

def get_model_info(model_name: str) -> dict:
    """Get configuration info for a specific model."""
    if model_name in MODEL_TIERS:
        return {
            "name": model_name,
            **MODEL_TIERS[model_name]
        }
    return {
        "name": model_name,
        "tier": "Unknown",
        "size": "N/A",
        "description": "Custom model",
        "recommended_timeout": 60
    }

def get_all_models() -> list:
    """Get list of all configured models with their info."""
    return [
        {
            "name": model_name,
            **config
        }
        for model_name, config in MODEL_TIERS.items()
    ]

def get_recommended_settings(model_name: str) -> dict:
    """Get recommended timeout for a model."""
    info = get_model_info(model_name)
    return {
        "timeout": info.get("recommended_timeout", 60)
    }
