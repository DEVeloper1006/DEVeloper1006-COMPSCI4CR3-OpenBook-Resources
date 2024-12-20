import random, sympy, math
from hashlib import sha256

class PrimeCyclicGroupMult:
    
    def __init__ (self, n):
        self.n = n
        self.elements = [num for num in range(1, n)]
        self.orders = self.orders()
        self.primitives = self._find_primitives()
        self.subgroups = self._find_subgroups()
    
    def orders (self):
        orders = dict()
        for i in self.elements:
            orders[i] = self.find_order(i)
        return orders
    
    def find_order (self, a):
        if a not in self.elements:
            raise ValueError("Element not in group")
        result = a
        count = 1
        while pow(result, count, self.n) != 1:
            count += 1
        return count
    
    def _find_primitives (self):
        primitives = []
        for i in self.elements:
            if self.orders[i] == len(self.elements):
                primitives.append(i)
        return primitives
    
    def _find_subgroups (self):
        subgroups = {}
        subgroups[len(self.elements)] = self.elements
        marked = set()
        for order in self.orders.values():
            if order != len(self.elements) and order not in marked:
                subgroup = []
                for i in self.elements:
                    if self.orders[i] == order:
                        subgroup.append(i)
                for primitive in self.primitives:
                    subgroup.append(primitive)
                subgroups[order] = subgroup
                marked.add(order)
        return subgroups
                
    def print_order (self):
        for i in self.elements:
            print(f"Order of {i} is {self.find_order(i)}")
            
    def is_generator (self, a):
        return a in self.primitives
    
    def derive_new_element (self, a, b):
        if a not in self.elements or b not in self.elements:
            raise ValueError("Elements not in group")
        return (a * b) % self.n
    
    def discrete_log_problem (self, generator, constant): #Very Hard for Large N
        if generator not in self.primitives or constant not in self.elements:
            raise ValueError("Elements not in group")
        result = generator
        count = 1
        while (pow(result, count, self.n) != constant):
            count += 1
        return count
    
    def find_inverse (self, element):
        
        def extended_ea(x, y):
            if y == 0:
                return x, 1, 0
            gcd, s, t = extended_ea(y, x % y)
            return gcd, t, s - (x // y) * t
        
        if element not in self.elements:
            raise ValueError("Element not in group")
        
        gcd, x, _ = extended_ea(element, self.n)
        if gcd != 1:
            raise ValueError(f"No inverse exists for {element} modulo {self.n}")
        return x % self.n

    def print_subgroups (self):
        for order, subgroup in self.subgroups.items():
            print(f"Subgroup of order {order}: {subgroup}")
        
class DiffieHellman:
    
    def __init__ (self, prime):
        if not sympy.isprime(prime):
            self.prime = 5
            self.group = PrimeCyclicGroupMult(self.prime)
        else:
            self.group = PrimeCyclicGroupMult(prime)
            self.prime = prime
        self.alpha = random.choice(self.group.primitives)
    
    def create_public_key (self, private):
        if private not in self.group.elements:
            raise ValueError("Number not in group")
        return pow(self.alpha, private, self.prime)
    
    def create_shared_key (self, num1, private):
        if num1 not in self.group.elements or private not in self.group.elements:
            raise ValueError("Numbers not in group")
        return pow(num1, private, self.prime)
        
class NaiveElgamalEncryption:
    
    def __init__ (self, prime):
        self.private1 = None
        self.private2 = None
        self.public1 = None
        self.public2 = None
        self.diffie_hellman = DiffieHellman(prime)
        self.shared_key1 = None
        self.shared_key2 = None
        
    def set_private_key(self, value, person1=True):
        if value not in self.diffie_hellman.group.elements:
            raise ValueError("Number not in group")
        if person1:
            self.private1 = value
        else:
            self.private2 = value
        
    def set_public_keys(self, person1=True):
        if person1:
            self.public1 = self.diffie_hellman.create_public_key(self.private1)
        else:
            self.public2 = self.diffie_hellman.create_public_key(self.private2)
    
    def set_shared_keys (self, person1=True):
        if self.public1 is None or self.public2 is None:
            raise ValueError("Public keys not set")
        if person1:
            self.shared_key1 = self.diffie_hellman.create_shared_key(self.public2, self.private1)
        else:
            self.shared_key2 = self.diffie_hellman.create_shared_key(self.public1, self.private2)
    
    def encrypt (self, plaintext, person1=True):
        if self.shared_key1 is None or self.shared_key2 is None:
            raise ValueError("Shared keys not set")
        if plaintext not in self.diffie_hellman.group.elements:
            raise ValueError("Plaintext not in group")
        if person1:
            return self.diffie_hellman.group.derive_new_element(plaintext, self.shared_key1)
        else:
            return self.diffie_hellman.group.derive_new_element(plaintext, self.shared_key2)
    
    def decrypt (self, ciphertext, person1=True):
        if self.shared_key1 is None or self.shared_key2 is None:
            raise ValueError("Shared keys not set")
        if ciphertext not in self.diffie_hellman.group.elements:
            raise ValueError("Ciphertext not in group")
        if person1:
            return self.diffie_hellman.group.derive_new_element(ciphertext, self.diffie_hellman.group.find_inverse(self.shared_key1))
        else:
            return self.diffie_hellman.group.derive_new_element(ciphertext, self.diffie_hellman.group.find_inverse(self.shared_key2))
        
class ElgamalEncryption:
    
    def __init__ (self, prime):
        self.private1 = None
        self.private2 = None
        self.public1 = None
        self.public2 = None
        self.shared_key1 = None
        self.shared_key2 = None
        if not sympy.isprime(prime):
            self.prime = 5
            self.group = PrimeCyclicGroupMult(self.prime)
        else:
            self.group = PrimeCyclicGroupMult(prime)
            self.prime = prime
        self.alpha = random.choice(self.group.primitives)
    
    def set_private_key(self, value, person1=True):
        if value not in self.diffie_hellman.group.elements:
            raise ValueError("Number not in group")
        if person1:
            self.private1 = value
        else:
            self.private2 = value
            
    def set_public_key(self, person1=True):
        if self.private1 is None or self.private2 is None:
            raise ValueError("Private Keys Not Set")
        if person1:
            self.public1 = pow(self.alpha, self.private1, self.prime)
        else:
            self.public2 = pow(self.alpha, self.private2, self.prime)
            
    def encrypt (self, plaintext, person1=True):
        if self.public1 is None or self.public2 is None:
            raise ValueError("Public Keys Not Set")
        if plaintext not in self.group.primitives:
            raise ValueError("Plaintext not in group")
        if person1:
            return self.group.derive_new_element(plaintext, pow(self.public2, self.private1, self.prime))
        else:
            return self.group.derive_new_element(plaintext, pow(self.public1, self.private2, self.prime))
        
    def decrypt (self, ciphertext, person1=True):
        if self.public1 is None or self.public2 is None:
            raise ValueError("Public Keys Not Set")
        if ciphertext not in self.group.primitives:
            raise ValueError("Plaintext not in group")
        if person1:
            return self.group.derive_new_element(ciphertext, pow(self.public2, self.prime - self.private1 - 1, self.prime))
        else:
            return self.group.derive_new_element(ciphertext, pow(self.public1, self.prime - self.private2 - 1, self.prime))
        
class ElgamalSignatureScheme:
    def __init__(self, prime):
        self.p = prime  # Prime number for the group
        self.g = 2  # Generator for the group (often 2 is used)
        self.x = random.randint(1, self.p-2)  # Private key
        self.y = pow(self.g, self.x, self.p)  # Public key y = g^x mod p

    def signature_generation(self, message):
        # Step 1: Choose a random k such that gcd(k, p-1) = 1
        while True:
            k = random.randint(1, self.p-2)
            if self.gcd(k, self.p-1) == 1:
                break
        
        # Step 2: Calculate r = g^k mod p
        r = pow(self.g, k, self.p)
        
        # Step 3: Calculate s = k^(-1) * (m - x * r) mod (p-1)
        k_inv = self.mod_inverse(k, self.p-1)  # Modular inverse of k modulo (p-1)
        s = (k_inv * (message - self.x * r)) % (self.p - 1)
        
        return (r, s)

    def signature_verification(self, signature, message):
        r, s = signature
        if not (1 <= r < self.p and 1 <= s < self.p):
            return False
        
        # Step 1: Calculate v1 = y^r * r^s mod p
        v1 = (pow(self.y, r, self.p) * pow(r, s, self.p)) % self.p
        
        # Step 2: Calculate v2 = g^m mod p
        v2 = pow(self.g, message, self.p)
        
        # Step 3: If v1 == v2, the signature is valid
        return v1 == v2

    def mod_inverse(self, a, m):
        # Extended Euclidean Algorithm to find the modular inverse
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            m, a = a % m, m
            x0, x1 = x1 - q * x0, x0
        if x1 < 0:
            x1 += m0
        return x1

    def gcd(self, a, b):
        # Euclidean algorithm to find greatest common divisor
        while b:
            a, b = b, a % b
        return a

class DSA:
    
    def __init__ (self):
        self.p, self.q = self._generate_large_primes()
        self.group = PrimeCyclicGroupMult(self.q)
        self.alpha = random.choice(self.group.elements)
        self.d = random.randint(0, self.q)
        self.beta = pow(self.alpha, self.d, self.p)
        self.public = (self.p, self.q, self.alpha, self.beta)
        self.private = self.d

    def _generate_large_primes (self):
        
        def miller_rabin(n, k=10):
            if n < 2:
                return False
            if n in (2, 3):
                return True
            if n % 2 == 0:
                return False

            r, d = 0, n - 1
            while d % 2 == 0:
                d //= 2
                r += 1

            for _ in range(k):
                a = random.randint(2, n - 2)
                x = pow(a, d, n)
                if x == 1 or x == n - 1:
                    continue
                for _ in range(r - 1):
                    x = pow(x, 2, n)
                    if x == n - 1:
                        break
                else:
                    return False
            return True
        
        def generate_large_prime (self, lower_bound, upper_bound):
            while True:
                candidate = random.randint(lower_bound, upper_bound)
                if miller_rabin(candidate):
                    return candidate
            
        lower_bound_q = 2**223
        upper_bound_q = 2**224 - 1
        lower_bound_p = 2**2047
        upper_bound_p = 2**2048 - 1

        for _ in range(4096):
            # Step 1: Find a 224-bit prime q
            q = generate_large_prime(lower_bound_q, upper_bound_q)

            # Step 2: Find a 2048-bit prime p such that p - 1 is a multiple of q
            for _ in range(1000):  # Limit attempts to find p
                m = random.randint(lower_bound_p, upper_bound_p)
                p = m - (m % (2 * q)) + 1  # Adjust m so that p-1 is a multiple of q
                if p > lower_bound_p and p < upper_bound_p and sympy.isprime(p):
                    return p, q

        raise ValueError("Failed to find suitable primes p and q within 4096 iterations.")  
    
    def signature_generation (self, x):
        ephemeral = random.randint(0, self.q)
        ephemeral_inv = self.group.find_inverse(ephemeral)
        r = pow(self.alpha, ephemeral, self.p) % self.q
        h_x = sha256(x.encode("utf-8").hexdigest())
        s = self.group.derive_new_element((h_x + self.d * r), ephemeral_inv)
        return (h_x, (r, s))
        
    def signature_verification (self, msg):
        h_x, (r, s) = msg
        w = self.group.find_inverse(s) % self.q
        u1 = self.group.derive_new_element(w, h_x)
        u2 = self.group.derive_new_element(w, r)
        v = ((self.alpha ** u1) * (self.beta ** u2)) % self.q
        return v % self.q == r   
    
p = 59
q = 29
alpha = 3
beta = 25
d = 23

h_x = 17
k_e = 25
k_e_inv = sympy.mod_inverse(k_e, q)

r = pow(alpha, k_e, p) % q
s = ((h_x + d * r) * k_e_inv) % q
print(f"Signature: ", (r, s))

w = sympy.mod_inverse(s, q)
u1 = (w*h_x) % q
u2 = (w*r) % q
v = (alpha ** u1) * (beta ** u2)