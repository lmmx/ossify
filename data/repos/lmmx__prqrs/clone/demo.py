import prqrs
import random

pq = prqrs.PriorityQueue()

# Enqueue items
for _ in range(10):
    item = prqrs.Item(value=random.randint(0, 10), priority=random.randint(1, 10))
    pq.push(item)

# Benchmark
print(
    prqrs.benchmark_enqueue(
        pq,
        [
            prqrs.Item(value=random.randint(0, 10), priority=random.randint(1, 10))
            for _ in range(10)
        ],
    ),
)
print(prqrs.benchmark_dequeue(pq))
