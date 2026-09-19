from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging incoming requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request details
        logger.info(f"Request: {request.method} {request.url.path}")
        logger.debug(f"Request headers: {dict(request.headers)}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response details
        logger.info(f"Response status: {response.status_code} in {process_time:.4f}s")

        # Add custom headers for monitoring
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Cache-Hit"] = "false"

        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors gracefully."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)

            # Handle specific error cases
            if response.status_code >= 400:
                logger.warning(f"Error response: {response.status_code} for {request.url.path}")

            return response

        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            return JSONResponse({"error": "Internal server error", "status": 500}, status_code=500)