def is_prime(n):
    """Return True if n is prime (self-contained)."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def gcd(a, b):
    """Return greatest common divisor."""
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Return least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)
