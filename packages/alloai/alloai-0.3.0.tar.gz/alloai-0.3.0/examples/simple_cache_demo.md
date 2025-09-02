```python
import time
import math

# Record start time for performance measurement
execution_start = time.time()

# Simulate expensive computation
print("Computing prime numbers...")
def find_primes(n):
    primes = []
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

primes = find_primes(1000)
print(f"Found {len(primes)} prime numbers")
print(f"First 10 primes: {primes[:10]}")
```

Calculate the sum and average of the first 50 prime numbers and display them

```python
# Display timing information
execution_end = time.time()
total_time = execution_end - execution_start
print(f"\nExecution time: {total_time:.3f} seconds")

# Cache demonstration message
print("\n" + "="*50)
print("CACHING DEMONSTRATION:")
print("="*50)
print("First run: Full computation (slower)")
print("Subsequent runs: Uses cached results (instant)")
print("Try running this script multiple times!")
print("Use --no-cache to disable caching")
print("Use --clear-cache to reset the cache")
print("="*50)
```
