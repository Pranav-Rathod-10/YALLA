"""Domain errors rendered as RFC 7807 problem+json."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    status: int = 400
    code: str = "bad_request"
    title: str = "Bad request"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.title)
        self.detail = detail or self.title


class NotFoundError(DomainError):
    status, code, title = 404, "not_found", "Not found"


class ForbiddenError(DomainError):
    status, code, title = 403, "forbidden", "Forbidden"


class ConflictError(DomainError):
    status, code, title = 409, "conflict", "Conflict"


class UnauthorizedError(DomainError):
    status, code, title = 401, "unauthorized", "Unauthorized"


def problem(status: int, code: str, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": title,
            "status": status,
            "code": code,
            "detail": detail,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _domain(_: Request, exc: DomainError) -> JSONResponse:
        return problem(exc.status, exc.code, exc.title, exc.detail)
