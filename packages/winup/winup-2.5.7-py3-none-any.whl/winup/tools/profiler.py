import time
import functools

class Profiler:
    def __init__(self):
        self.results = {}
        self.memo_hits = 0
        self.memo_misses = 0

    def record_memo_hit(self):
        self.memo_hits += 1

    def record_memo_miss(self):
        self.memo_misses += 1

    def measure(self, func_name=None):
        """
        A decorator to measure the execution time of a function.
        Results are stored in the 'results' dictionary.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or func.__name__
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # in milliseconds
                
                self.results[name] = f"{execution_time:.4f} ms"
                print(f"Profiled '{name}': {execution_time:.4f} ms")
                
                return result
            return wrapper
        return decorator

    def print_results(self):
        """Prints all stored profiling results."""
        print("\n--- Performance Profile ---")
        if not self.results and self.memo_hits == 0 and self.memo_misses == 0:
            print("No profiling data has been recorded.")
            return

        for name, timing in self.results.items():
            print(f"- {name}: {timing}")
        
        if self.memo_hits > 0 or self.memo_misses > 0:
            total_lookups = self.memo_hits + self.memo_misses
            hit_ratio = (self.memo_hits / total_lookups * 100) if total_lookups > 0 else 0
            print("\n--- Memoization Cache ---")
            print(f"- Hits: {self.memo_hits}")
            print(f"- Misses: {self.memo_misses}")
            print(f"- Hit Ratio: {hit_ratio:.2f}%")

        print("-------------------------\n")

# Singleton instance
profiler = Profiler() 