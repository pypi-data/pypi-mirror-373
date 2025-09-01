```python
import random
import statistics

# Generate sample data
data = [random.randint(1, 100) for _ in range(20)]
print(f"Generated data: {data}")
```

Calculate the mean, median, and standard deviation of the data and display them nicely.

```python
# Display the length of our dataset
print(f"\nDataset contains {len(data)} values")
```

Create a simple histogram of the data using ASCII characters (group the data into 5 bins).

```python
# Find min and max for reference
print(f"\nRange: {min(data)} to {max(data)}")
```

Sort the data and display the top 5 and bottom 5 values.
