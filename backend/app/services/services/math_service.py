from app.services.utils.example_core import MathOperations
from app.services.services.base_service import service_method
from fastapi import HTTPException, status
from fastapi import Depends


class MathService:

    def __init__(self):
        """
        Initialize the math service with a Unit of Work

        Args:
            uow (UnitOfWork): The Unit of Work instance for managing transactions
        """
        self.operations = {
            'add': MathOperations.add,
            'subtract': MathOperations.subtract,
            'multiply': MathOperations.multiply,
            'divide': MathOperations.divide,
            'power': MathOperations.power
        }

    @service_method
    async def calculate_operation(self, operation: str, x: float, y: float) -> float:
        """
        Perform a mathematical operation

        Args:
            operation (str): The name of the operation to perform
            x (float): The first operand
            y (float): The second operand

        Returns:
            float: The result of the operation

        Raises:
            HTTPException: If the operation is not supported
        """
        if operation not in self.operations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported operation: {operation}"
            )
        return self.operations[operation](x, y)
