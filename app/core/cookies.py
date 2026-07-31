from fastapi import Response


def set_auth_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=max_age,
    )
