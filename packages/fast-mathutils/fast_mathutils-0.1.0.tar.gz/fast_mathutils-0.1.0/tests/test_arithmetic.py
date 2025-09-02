from pymathutils import factorial, fibonacci

def test_factorial():
    assert factorial(0) == 1
    assert factorial(5) == 120

def test_fibonacci():
    assert fibonacci(0) == 0
    assert fibonacci(5) == 5

#I'm very clean so I put it inside folders
