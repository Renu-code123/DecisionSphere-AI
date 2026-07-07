import time
from fastapi import Request, HTTPException, status
from app.config import settings

# In-memory dictionary to store request timestamps for each IP
# Format: { ip: [timestamp1, timestamp2, ...] }
request_history = {}

def rate_limiter(request: Request):
    """
    Client-IP based sliding window rate limiter.
    Configuration is read from the settings.
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    # Initialize list if first request
    if client_ip not in request_history:
        request_history[client_ip] = []
        
    # Filter out timestamps older than the rate limit window
    history = [t for t in request_history[client_ip] if current_time - t < settings.RATE_LIMIT_WINDOW_SECONDS]
    request_history[client_ip] = history
    
    # Check limit
    if len(history) >= settings.RATE_LIMIT_CALLS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
        
    # Record current request timestamp
    request_history[client_ip].append(current_time)
