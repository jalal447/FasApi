import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to headers for downstream use if needed
        # request.state.request_id = request_id
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(
            f"Request ID: {request_id} | Path: {request.url.path} | "
            f"Method: {request.method} | Status: {response.status_code} | "
            f"Duration: {duration:.4f}s"
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Execution-Time"] = str(duration)
        
        return response
