#!/usr/bin/env python3
import socket
import argparse
import random
import time
import sys
import threading
import math
from typing import Tuple, Optional

# Prime lists for different dh prime sizes
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
MEDIUM_PRIMES = [251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397]
LARGE_PRIMES = [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097]
VERY_LARGE_PRIME = 65521 


def receive_common_info(f_obj) -> Tuple[int, int]:
    base = int(f_obj.readline().strip())
    modulus = int(f_obj.readline().strip())
    return base, modulus

def dh_exchange_server(server_address: str, server_port: int) -> Tuple[int, int, int, int]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_address, server_port))
        sock.listen(1)

        conn, addr = sock.accept()
        with conn:
            print(f"Connected by {addr}")
            
            with conn.makefile('r', encoding='utf-8') as f_obj:
                base, modulus = receive_common_info(f_obj)
                print(f"Received base={base}, modulus={modulus}")
    
                secret_key = random.randint(2, max(2, modulus - 2))
                print(f"Secret is {secret_key}")
                
                public_value = pow(base, secret_key) % modulus
    
                line = f_obj.readline()
                client_public_value = int(line.strip())
                conn.sendall(f"{public_value}\n".encode())
                shared_secret = pow(client_public_value, secret_key) % modulus
                return base, modulus, secret_key, shared_secret

def send_common_info(sock: socket.socket, server_address: str, server_port: int, prime_size: str = "small") -> Tuple[int, int]:
    """Send base and modulus proposal to server."""
    if prime_size == "small":
        primes = SMALL_PRIMES
    elif prime_size == "medium":
        primes = MEDIUM_PRIMES
    elif prime_size == "large":
        primes = LARGE_PRIMES
    elif prime_size == "very_large":
        primes = [VERY_LARGE_PRIME]
    else:
        primes = SMALL_PRIMES
    
    modulus = random.choice(primes)
    base = random.randint(2, modulus - 1)
    
    message = f"{base}\n{modulus}\n"
    sock.sendall(message.encode())
    
    return base, modulus


def dh_exchange_client(server_address: str, server_port: int, prime_size: str = "small") -> Tuple[int, int, int, int]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((server_address, server_port))
            
            base, modulus = send_common_info(sock, server_address, server_port, prime_size)
            print(f"Sent base={base}, modulus={modulus}")

            secret_key = random.randint(2, max(2, modulus - 2))
            print(f"Secret is {secret_key}")

            public_value = pow(base, secret_key) % modulus

            sock.sendall(f"{public_value}\n".encode())
            
            with sock.makefile('r', encoding='utf-8') as f_obj:
                line = f_obj.readline()
                server_public_value = int(line.strip())
            
            print(f"Int received from peer is {server_public_value}")

            shared_secret = pow(server_public_value, secret_key) % modulus
            print(f"Shared secret is {shared_secret}")
            
            return base, modulus, secret_key, shared_secret
        except (ConnectionRefusedError, ValueError) as e:
            print(f"Error: {e}")
            return (0, 0, 0, 0)


def crack_dh_bruteforce(base: int, modulus: int, public_value: int) -> Optional[int]:
    print(f"Attempting to crack: base={base}, modulus={modulus}, public_value={public_value}")
    print(f"Trying all possible secret keys from 2 to {modulus}...")
    
    attempts = 0
    start_time = time.time()
    
    # Try all possible secret keys
    for secret_candidate in range(2, modulus - 1):
        attempts += 1
        # Compute what the public value would be with this secret
        computed_public = pow(base, secret_candidate) % modulus
        
        if computed_public == public_value:
            elapsed = time.time() - start_time
            print(f"SUCCESS! Found secret key: {secret_candidate}")
            print(f"Attempts: {attempts}")
            return secret_candidate
    
    return None


def crack_dh_with_shared_secret(base: int, modulus: int, 
                                 client_public: int, server_public: int) -> Optional[int]:
    print("="*70)
    print(f"Public Information:")
    print(f"  Base (g):            {base}")
    print(f"  Modulus (p):         {modulus}")
    print(f"  Client Public (A):   {client_public}")
    print(f"  Server Public (B):   {server_public}")
    print("="*70 + "\n")
    
    # Crack the client's secret key
    print("Cracking client's secret key...")
    client_secret = crack_dh_bruteforce(base, modulus, client_public)
    
    if client_secret is None:
        print("Failed to crack client secret!")
        return None
    
    # Compute shared secret using cracked client secret and server public value
    shared_secret = pow(server_public, client_secret) % modulus
    
    print(f"Shared secret = {server_public}^{client_secret} mod {modulus} = {shared_secret}")
    
    print("\n" + "="*70)
    print(f"CRACKED SHARED SECRET: {shared_secret}")
    print("="*70)
    
    return shared_secret


def benchmark_crack_speed(base: int, modulus: int) -> float:
    print("\nBenchmarking crack speed...")
    # Use enough iterations to get a measurable time (at least 100k operations)
    iterations = max(100000, modulus * 100)
    
    start = time.time()
    for i in range(iterations):
        _ = pow(base, i % modulus) % modulus
    elapsed = time.time() - start
    
    # Ensure we don't divide by zero
    if elapsed < 0.000001:  # Less than 1 microsecond
        elapsed = 0.000001
    
    ops_per_second = iterations / elapsed
    print(f"Benchmark: {ops_per_second:.2e} operations/second ({iterations} ops in {elapsed:.4f}s)")
    return ops_per_second


def estimate_crack_time(modulus_bits: int, attempts_per_second: float):
    print(f"\n{'='*70}")
    print("ESTIMATING CRACK TIME FOR LARGER KEYS")
    print('='*70)
    
    # Use logarithms to avoid overflow
    log_ops_per_sec = math.log10(attempts_per_second)
    log_seconds = modulus_bits * math.log10(2) - log_ops_per_sec
    
    # Convert to other time units
    log_minutes = log_seconds - math.log10(60)
    log_hours = log_minutes - math.log10(60)
    log_days = log_hours - math.log10(24)
    log_years = log_days - math.log10(365.25)
    
    print(f"Modulus size: {modulus_bits} bits")
    print(f"Possible keys: ~2^{modulus_bits} ≈ 10^{modulus_bits * math.log10(2):.1f}")
    print(f"Crack speed: {attempts_per_second:.2e} attempts/second")
    print(f"\nEstimated crack time:")
    print(f"  ~10^{log_years:.1f} years")
    print('='*70)

def run_dh_exchange_with_seed(seed=42, prime_size="small"):
    print("="*70)
    print("Running DH key exchange...")
    print("="*70)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    server_address = "127.0.0.1"
    server_port = 8765  # Use different port to avoid conflicts
    
    server_result = [None]  # Use list to capture result from thread
    
    def run_server():
        result = dh_exchange_server(server_address, server_port)
        server_result[0] = result
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(0.5)
    
    # Run client
    print("\nClient connecting...")
    client_result = dh_exchange_client(server_address, server_port, prime_size)
    
    # Wait for server to finish
    server_thread.join(timeout=2)
    
    if server_result[0] is None:
        print("Server failed to complete exchange")
        return None
    
    # Extract values
    base_c, modulus_c, client_secret, client_shared = client_result
    base_s, modulus_s, server_secret, server_shared = server_result[0]
    
    # Verify both sides agree
    assert base_c == base_s, "Base mismatch!"
    assert modulus_c == modulus_s, "Modulus mismatch!"
    assert client_shared == server_shared, "Shared secret mismatch!"
    
    # Compute public values (what an attacker would see)
    client_public = pow(base_c, client_secret) % modulus_c
    server_public = pow(base_s, server_secret) % modulus_s
    
    print("\n" + "="*70)
    print("EXCHANGE COMPLETE")
    print("="*70)
    print(f"Public Information (visible to attacker):")
    print(f"  Base (g):            {base_c}")
    print(f"  Modulus (p):         {modulus_c}")
    print(f"  Client Public (A):   {client_public}")
    print(f"  Server Public (B):   {server_public}")
    print(f"\nPrivate Information (should remain secret):")
    print(f"  Client Secret:       {client_secret}")
    print(f"  Server Secret:       {server_secret}")
    print(f"  Shared Secret:       {client_shared}")
    print("="*70)
    
    return base_c, modulus_c, client_public, server_public, client_shared


def demonstrate_larger_modulus():
    """Demonstrate that larger modulus takes longer to crack."""
    print("\n\n")
    print("#"*70)
    print("# TESTING WITH LARGER MODULUS")
    print("#"*70)
    
    # Test with progressively larger primes
    test_cases = [
        (3, 97, "Small prime (< 100)"),
        (5, 251, "Medium prime (~250)"),
        (7, 1009, "Large prime (~1000)"),
        (11, 65521, "Very large prime (~65000)"),
    ]
    
    for base, modulus, description in test_cases:
        print(f"\n{'='*70}")
        print(f"Testing: {description}")
        print(f"Base={base}, Modulus={modulus}")
        print('='*70)
        
        # Generate a secret and public value
        secret = random.randint(2, modulus - 2)
        public = pow(base, secret) % modulus
        
        print(f"Secret: {secret}, Public: {public}")
        
        # Attempt to crack it
        start = time.time()
        cracked = crack_dh_bruteforce(base, modulus, public)
        elapsed = time.time() - start
        
        server_public_test = pow(base, random.randint(2, modulus-2), modulus)
        shared_secret_actual = pow(server_public_test, secret, modulus)
        shared_secret_cracked = pow(server_public_test, cracked, modulus)

        if shared_secret_cracked == shared_secret_actual:
            print(f"Successfully cracked in {elapsed:.8f} seconds")
    
    # Benchmark and estimate for realistic sizes
    print("\n\n")
    print("#"*70)
    print("# ESTIMATING REALISTIC KEY SIZES")
    print("#"*70)
    
    # Use a medium-sized modulus for benchmarking
    ops_per_sec = benchmark_crack_speed(5, 251)
    
    # Estimate for realistic key sizes
    realistic_sizes = [512, 1024, 2048, 4096]
    for bits in realistic_sizes:
        estimate_crack_time(bits, ops_per_sec)


def run_demo(prime_size="small"):  

    # Run legitimate exchange
    result = run_dh_exchange_with_seed(seed=69, prime_size=prime_size)
    if result is None:
        print("Failed to run DH exchange")
        return 1
    
    base, modulus, client_public, server_public, actual_shared_secret = result
    
    # Crack the exchange
    print("\n\n")
    print("#"*70)
    print("# ATTACKING THE KEY EXCHANGE")
    print("#"*70)
    print()
    
    cracked_secret = crack_dh_with_shared_secret(base, modulus, client_public, server_public)
    
    if cracked_secret == actual_shared_secret:
        print("  SUCCESS! Cracked shared secret matches the actual shared secret")
        print(f"  Actual:  {actual_shared_secret}")
        print(f"  Cracked: {cracked_secret}")
    else:
        print("  FAILED! Cracked secret doesn't match")
        print(f"  Actual:  {actual_shared_secret}")
        print(f"  Cracked: {cracked_secret}")
    
    # Demonstrate scaling with larger modulus
    demonstrate_larger_modulus()
    
    
def main():
    parser = argparse.ArgumentParser(
        description="Diffie-Hellman Cracking Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--crack",
        action="store_true",
    )
    
    parser.add_argument(
        "-g", "--base",
        type=int,
    )
    
    parser.add_argument(
        "-p", "--modulus",
        type=int,
    )
    
    parser.add_argument(
        "-A", "--client-public",
        type=int,
    )
    
    parser.add_argument(
        "-B", "--server-public",
        type=int,
    )
    
    parser.add_argument(
        "--estimate",
        nargs='+',
        type=int,
    )
    
    parser.add_argument(
        "--prime-size",
        choices=["small", "medium", "large", "very_large"],
        default="small",
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    
    args = parser.parse_args()
    
    # Crack a specific exchange
    if args.crack:
        if not all([args.base, args.modulus, args.client_public, args.server_public]):
            parser.error("--crack requires -g/--base, -p/--modulus, -A/--client-public, -B/--server-public")
        
        shared_secret = crack_dh_with_shared_secret(
            args.base,
            args.modulus,
            args.client_public,
            args.server_public
        )
        
        # Benchmark and estimate larger keys if requested
        if args.estimate:
            ops_per_sec = benchmark_crack_speed(args.base, args.modulus)
            for bits in args.estimate:
                estimate_crack_time(bits, ops_per_sec)
    
    else:
        random.seed(args.seed)
        return run_demo(args.prime_size)


if __name__ == "__main__":
    sys.exit(main() or 0)