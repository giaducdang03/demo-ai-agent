"""
Base Service Implementation

This file defines the base service class and a decorator for handling service methods.
It provides:
- A base class for all services to inherit from
- A decorator for handling exceptions in service methods
- Dependency injection for Unit of Work and repositories

The BaseService class is a generic class that requires a repository type to be specified
by subclasses. It provides a consistent interface for accessing repositories and managing
transactions.

Dependencies:
- FastAPI for dependency injection and HTTP exceptions
- SQLAlchemy for database operations
- Unit of Work pattern for transaction management
- Repository pattern for data access

Author: Minh An
Last Modified: 21 Jan 2024
Version: 1.0.0
"""

from abc import abstractmethod
from typing import Generic, TypeVar, Callable, Type
from functools import wraps
from fastapi import Depends, HTTPException, status

T = TypeVar('T')


def service_method(func: Callable):
    """
    Decorator for service methods to handle exceptions

    Args:
        func (Callable): The service method to be decorated

    Returns:
        Callable: The wrapped service method with exception handling
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return wrapper


class BaseService(Generic[T]):
    """
    Base service class for managing repositories and transactions

    Attributes:
        repository_type (Type[BaseRepository]): The type of repository to be used by the service
        uow (UnitOfWork): The Unit of Work instance for managing transactions
    """