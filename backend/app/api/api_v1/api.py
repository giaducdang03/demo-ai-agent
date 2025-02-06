"""
API V1 Endpoints

This file defines the API V1 endpoints for the application.
It includes endpoints for user management, item management, and math operations.

Dependencies:
- FastAPI for creating API endpoints
- Pydantic for data validation and serialization
- Various service classes for business logic

Author: Minh An
Last Modified: 21 Jan 2024
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from app.services.services.math_service import MathService
from app.schemas.response_schema import UserResponse, ItemResponse, MessageResponse
from app.schemas.request_schema import UserRequest, ItemRequest, MathOperationRequest

api_router = APIRouter()  # Changed variable name to api_router


# Math operations endpoints
@api_router.post("/math/{operation}")
async def calculate(
        operation: str,
        request: MathOperationRequest,
):
    return await MathService.calculate_operation(operation, request.x, request.y)


__all__ = ["api_router"]  # Explicitly export api_router
