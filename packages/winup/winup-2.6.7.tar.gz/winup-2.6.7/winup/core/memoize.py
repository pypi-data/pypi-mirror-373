import functools
from ..tools import profiler

_cache = {}
_hits = 0
_misses = 0

def memo(func):
    """
    A memoization decorator for WinUp components.
    
    Caches the component's output based on its arguments. If the component
    is called again with the same arguments, the cached widget is returned
    instead of re-creating it. This can significantly speed up rendering
    of complex or repeated components.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _hits, _misses
        # Create a cache key from the function and its arguments.
        # We handle unhashable types like dicts and lists.
        try:
            key = (func, args, frozenset(kwargs.items()))
        except TypeError:
            # Fallback for unhashable kwargs by converting them to a string.
            # This is less robust but handles common cases like dicts in props.
            key = (func, args, str(kwargs))

        # Check if the result is already in the cache.
        if key in _cache:
            _hits += 1
            profiler.results['memo_hits'] = _hits
            return _cache[key]
        
        # If not, call the function, store the result, and return it.
        _misses += 1
        profiler.results['memo_misses'] = _misses
        result = func(*args, **kwargs)
        _cache[key] = result
        return result
        
    return wrapper

def clear_memo_cache():
    """Clears the entire memoization cache."""
    global _cache, _hits, _misses
    _cache.clear()
    _hits = 0
    _misses = 0
    if 'memo_hits' in profiler.results:
        del profiler.results['memo_hits']
    if 'memo_misses' in profiler.results:
        del profiler.results['memo_misses']
    print("Memoization cache cleared.") 