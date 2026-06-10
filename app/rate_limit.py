from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import APIRouter, Request
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

class RateLimitedRouter(APIRouter):
    def __init__(self, limit: str = "30/minute", **kwargs):
        super().__init__(**kwargs)
        self.default_limit = limit

def add_rate_limit_exception_handler(app):
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
