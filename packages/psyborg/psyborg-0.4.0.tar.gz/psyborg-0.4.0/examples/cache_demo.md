# Cache Demo for psyborg

This example demonstrates the caching functionality in psyborg. When you run this script multiple times, subsequent runs will use cached results for both code execution and LLM responses.

## Setup

Let's start with some basic setup and time tracking to demonstrate caching:

```python
import time
import random

# Record start time
start_time = time.time()
print(f"Script started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Simulate some expensive computation
print("Performing expensive computation...")
time.sleep(2)  # Simulates a slow operation
result = sum(range(1000000))
print(f"Computation result: {result}")
```

## Generate Random Data

```python
# Generate some random data
random.seed(42)  # Fixed seed for reproducibility
data = [random.randint(1, 100) for _ in range(10)]
print(f"Generated data: {data}")
```

## LLM Analysis

Create a function to analyze the data and calculate statistics (mean, median, min, max).

## More Processing

```python
# The LLM should have created a function above
# Let's use it if it exists
if 'analyze_data' in globals():
    stats = analyze_data(data)
    print(f"Statistics: {stats}")
else:
    print("No analyze_data function found")
```

## Another LLM Task

Create a simple bar chart visualization of the data using ASCII characters. Make each bar proportional to the value.

## Final Summary

```python
# Calculate total execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"\nTotal execution time: {execution_time:.2f} seconds")
print("\n" + "="*50)
print("CACHING NOTES:")
print("="*50)
print("1. First run: Full execution, slower")
print("2. Subsequent runs: Uses cache, much faster")
print("3. Use --no-cache flag to disable caching")
print("4. Use --clear-cache flag to clear cache")
print("="*50)
```

## Instructions for Testing

To test the caching functionality:

1. **First run** (no cache):
   ```bash
   psyborg examples/cache_demo.md
   ```
   Note the execution time.

2. **Second run** (with cache):
   ```bash
   psyborg examples/cache_demo.md
   ```
   Notice how much faster it runs!

3. **Run without cache**:
   ```bash
   psyborg examples/cache_demo.md --no-cache
   ```
   This will be slow again like the first run.

4. **Clear cache and run**:
   ```bash
   psyborg examples/cache_demo.md --clear-cache
   ```
   This clears the cache before running.

The caching system uses SHA-256 hashing to create unique identifiers for:
- Code blocks (based on code content and current variable state)
- LLM prompts (based on instruction and execution context)

This ensures that identical code/prompts with the same context will reuse cached results, significantly speeding up iterative development and testing.
