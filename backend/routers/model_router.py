"""
Model management router for LLM model selection and loading.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

from services.llm_service import (
    get_available_models_from_ollama,
    load_model,
    get_current_model
)


router = APIRouter()


class ModelLoadRequest(BaseModel):
    """Schema for model load request"""
    name: str = Field(..., description="Name of the model to load")


class ModelLoadResponse(BaseModel):
    """Schema for model load response"""
    success: bool
    model: str
    message: str
    settings: Dict = Field(default_factory=dict)


class CurrentModelResponse(BaseModel):
    """Schema for current model response"""
    name: str
    loaded: bool
    timeout: int
    tier: str
    size: str
    description: str


@router.get("/models/available", response_model=List[Dict])
async def get_available_models():
    """
    Get list of available models from Ollama server.
    
    Returns:
        List of models with their configuration
    """
    try:
        models = get_available_models_from_ollama()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.get("/models/current", response_model=CurrentModelResponse)
async def get_current():
    """
    Get currently loaded model information.
    
    Returns:
        Current model details
    """
    try:
        current = get_current_model()
        return CurrentModelResponse(**current)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current model: {str(e)}")


@router.post("/models/load", response_model=ModelLoadResponse)
async def load_model_endpoint(request: ModelLoadRequest):
    """
    Load a specific model into Ollama server.
    
    Args:
        request: Model load request with model name
    
    Returns:
        Load status and settings
    """
    try:
        result = load_model(request.name)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return ModelLoadResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
