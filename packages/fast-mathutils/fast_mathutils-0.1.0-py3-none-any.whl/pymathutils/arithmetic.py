def factorial(n):
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def fibonacci(n):
    if n < 0:
        raise ValueError("Fibonacci not defined for negative numbers. Try again...")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
