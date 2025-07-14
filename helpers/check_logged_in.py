from fastapi import HTTPException, status


def check_logged_in(user) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='could not validate user'
        )