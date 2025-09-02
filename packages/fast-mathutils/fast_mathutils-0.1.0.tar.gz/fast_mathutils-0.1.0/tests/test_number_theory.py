from pymathutils import is_prime, gcd, lcm

def test_is_prime():
    assert is_prime(2)
    assert not is_prime(4)

def test_gcd_lcm():
    assert gcd(12, 18) == 6
    assert lcm(12, 18) == 36
