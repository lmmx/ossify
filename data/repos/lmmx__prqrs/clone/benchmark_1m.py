import prqrs
import random
import time

pq = prqrs.PriorityQueue()

# Generating 1 million items
items = [
    prqrs.Item(value=random.randint(0, 1000), priority=random.randint(1, 100))
    for _ in range(1000000)
]

# Benchmark enqueue
start_time = time.time()
for item in items:
    pq.push(item)
enqueue_duration = time.time() - start_time
print(f"Enqueue time for 1 million items: {enqueue_duration} seconds")

# Benchmark dequeue
start_time = time.time()
while not pq.is_empty():
    pq.pop()
dequeue_duration = time.time() - start_time
print(f"Dequeue time for 1 million items: {dequeue_duration} seconds")
