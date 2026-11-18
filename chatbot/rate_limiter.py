import time
from django.core.cache import cache
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip

def check_rate_limit(client_id: str, request) -> tuple[bool, int]:
    """
    Checks rate limits:
    - 15 requests per minute
    - 150 requests per day
    per client_id and IP (FR-035).
    Returns (is_allowed, retry_after_seconds).
    """
    ip = get_client_ip(request)
    now = int(time.time())

    limit_min = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 15)
    limit_day = getattr(settings, 'RATE_LIMIT_PER_DAY', 150)

    key_min = f"rl:min:{client_id}:{ip}"
    key_day = f"rl:day:{client_id}:{ip}"

    # Get minute history
    min_requests = cache.get(key_min, [])
    # Keep only timestamps within last 60 seconds
    min_requests = [t for t in min_requests if now - t < 60]

    if len(min_requests) >= limit_min:
        oldest = min_requests[0]
        retry_after = max(1, 60 - (now - oldest))
        return False, retry_after

    # Get day history
    day_requests = cache.get(key_day, [])
    # Keep only timestamps within last 86400 seconds
    day_requests = [t for t in day_requests if now - t < 86400]

    if len(day_requests) >= limit_day:
        oldest = day_requests[0]
        retry_after = max(1, 86400 - (now - oldest))
        return False, retry_after

    # Record current timestamp
    min_requests.append(now)
    day_requests.append(now)

    cache.set(key_min, min_requests, timeout=65)
    cache.set(key_day, day_requests, timeout=86405)

    return True, 0
