from aiolimiter import AsyncLimiter

# Create a global rate limiter instance
rate_limiter = AsyncLimiter(max_rate=300, time_period=60)