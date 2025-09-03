from http import HTTPStatus
from typing import Any, Optional

from fastapi import HTTPException


class APIException(HTTPException):
    def __init__(
        self,
        status_code: HTTPStatus,
        error_code: str,
        message: str,
        display_message: str,
        headers: Optional[dict[str, Any]] = None
    ) -> None:
        detail = {
            "error_code": error_code,
            "message": message,
            "display_message": display_message
        }

        super().__init__(
            status_code=status_code.value,
            detail=detail,
            headers=headers
        )

        self.status_code: HTTPStatus = status_code
        self.error_code: str = error_code
        self.message: str = message
        self.display_message: str = display_message

    def __str__(self):
        return (
            f"[{self.status_code}] {self.error_code}: {self.message} "
            f"(Display: {self.display_message})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code.value,
            "error_code": self.error_code,
            "message": self.message,
            "display_message": self.display_message,
        }
