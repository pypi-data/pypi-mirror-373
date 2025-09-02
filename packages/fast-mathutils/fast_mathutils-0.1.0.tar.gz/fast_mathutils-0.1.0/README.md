# 📦 pymathutils

A simple, self-contained Python math utilities module.  
Includes factorial, Fibonacci, primes, gcd, and lcm.

## Installation
```
git clone https://github.com/SuperHappycat/pymathutils.git
cd pymathutils
```
## Usage
```
from pymathutils import factorial, fibonacci, is_prime, gcd, lcm

print(factorial(5))   # 120
print(fibonacci(7))   # 13
print(is_prime(29))   # True
print(gcd(12, 18))    # 6
print(lcm(12, 18))    # 36
```
## Testing
⚠️ WARNING!  Testing needs pytest installed. 
```
python3 -m pip install pytest
python3 -m pytest tests      
```

## License
MIT
