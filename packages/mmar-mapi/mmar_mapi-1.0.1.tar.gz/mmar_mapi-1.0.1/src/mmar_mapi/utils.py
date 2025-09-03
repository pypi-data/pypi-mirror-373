from datetime import datetime


def make_session_id() -> str:
    return f"{datetime.now():%Y-%m-%d--%H-%M-%S}"
