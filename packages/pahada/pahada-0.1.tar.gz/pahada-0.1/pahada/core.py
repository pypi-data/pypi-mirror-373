import random

def generate(n: int, upto: int = 10) -> list[str]:
    """Generate multiplication table of n up to `upto`."""
    return [f"{n} x {i} = {n*i}" for i in range(1, upto+1)]

def quiz(n: int, upto: int = 10) -> str:
    """Give a random multiplication question for n."""
    i = random.randint(1, upto)
    return f"What is {n} x {i}?"
