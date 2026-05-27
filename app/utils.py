from typing import Any

from sqlalchemy.orm import Session


def apply_updates(instance: Any, data: dict[str, Any]) -> Any:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)
    return instance
