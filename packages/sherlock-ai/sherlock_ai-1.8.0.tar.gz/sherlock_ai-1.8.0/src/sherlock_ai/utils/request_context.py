from contextvars import ContextVar
import uuid
from typing import Optional

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def set_request_id(req_id: Optional[str] = None) -> str:
    """
    Set request ID for current context
    Args:
        req_id: Optional request ID. If None, generates a new one
    Returns:
        The request ID that was set
    """
    if req_id is None:
        req_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    request_id_var.set(req_id)
    return req_id


def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_var.get("")


def clear_request_id():
    """Clear the current request ID"""
    request_id_var.set("")